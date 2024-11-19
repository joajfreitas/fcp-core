# Changelog

## v0.25.0

### signal_parser.c and signal_parser.h

[signal_parser.c](https://gitlab.com/projectofst/software10e/-/blob/feat/fcp/v20/fcp/skel/signal_parser.c)
and
[signal_parser.h](https://gitlab.com/projectofst/software10e/-/blob/feat/fcp/v20/fcp/skel/signal_parser.h).

The signal parser interface has suffered major changes. The decode functions
now take the `fcp_signal_t` struct as a parameter instead of individual start,
length, scale and offset parameters.

```
typedef struct _signal {
	uint16_t start;
	uint16_t length;
	double scale;
	double offset;
	fcp_type_t type;
	fcp_endianness_t endianness;
} fcp_signal_t;
```

The `fcp_signal_t` now includes the signal type and endianness. Check the
`fcp_type_t` and `fcp_endianness_t` enums for possible values.

Example usage:
```
uint64_t value = fcp_decode_signal_uint64_t(msg,
	(fcp_signal_t) {
		.start = start,
		.length = length,
		.scale = scale,
		.offset = offset,
		.type= type
		.endianness = endianness
	}
);
```

The obvious advantage of this change is the support for big endian signals.

### C codegen

The `fcp c_gen` command was updated to make use of the new signal_parser
functions.

Those that make use of `c_gen` should not notice any changes **except** for a
substantial increase in program size.

If this increase in program size is troublesome remember that the compilation
of devices can be stopped by defining: NO_DCU, NO_MASTER, NO_IIB, ...

### Author note

This release was a bit rushed due to the need to support big endian values in
Xsense. If you encounter any problems with decoding and encoding fcp signals please
notify me via discord.

## v0.47.0

### Features

* Show release notes at gui startup
* Notify of new Fcp versions
* GUI Undo/Redo

### Bug Fixes
* Recent file list is the same for any Fcp instance
* Fixed unexpected slowness when using save on the GUI

## v0.47.0

### Features

* Add fix command that fixes your json types.

### Bug Fixes
* Wrong conversion of floating point scaling/offset on decompile
* Limit number of errors in GUI.
* Remove dump and print commands that were unused.

## v0.49.0

### Features

 * c-gen --force flag to ignore validate errors

### Bug Fixes
 * gui wouldn't launch


## v0.50.0

### Features

 * fix cmd replaces mux_count 0 with mux_count 1

### Bug Fixes

 * Add fcp appdirs and sqlalchemy dependency
 * Unify requirements.txt and install_requires

## v0.53.0

### Features

 * implement mux for fcp_lib

## v0.54.0

### Bugs

 * Nag users about new version of FCP

### Features

 * Show FCP release notes

## v0.55.0

### Features

* FcpLib: FcpCom with cmd, set and get
* Property based testing for signals


## v0.55.1

### Bug Fixes

* Gui save not working

### Features

* Gui save doesn't pop a select file menu

## v0.55.2

### Bug Fixes

* Remove type hint

## v0.55.3

### Bug Fixes

* Test against python3.7

## v0.55.4

### Bug Fixes

* Command, Config, Enum add button not working
* Fixed order of recent files

## v0.55.4

### Bug Fixes

* Regression in message decoding mux support

# v0.55.5

### Bug Fixes

* Regression in message decoding mux support

## v0.55.6

### Bug Fixes

* Regression in message decoding mux support

## v0.55.7

### Features

* New docs signal page

## v0.56.0

 - Check that release notes exist:
	- add a pre-commit hook (hooks/check_release_notes).
	- call the script from .gitlab-ci.yaml,
 - Add better comparison of fcp version to the GUI:
	- Handle the case of the local version being higher than the upstream one.
 - Support for encoding socketcan messages.
 - Improve decoding of signed signals.
 - Rename fcp_v2 to idl

This release contains some bugfixes, small improvements and introduces
fcp_v2 the new description language that replaces the fcp json
specification format.

For now fcp commands support both the json specification format and
fcp_v2.

Expect more information regarding fcp_v2 in future releases.

## v0.56.1

### Bug Fixes

* Non multiplexed signals belonging to messages with other signals that are multiplexed are no longer interpreted as multiplexed signals in the decoding process.

## v1.0.0.dev1

Fcp has moved on to the next stage of its life. We've started development on
the affectionately named "fcp v2".

There's a couple main goals for the new fcp version:
 * Develop an IDL (interface description language) to replace the old json configuration.
 * Allow fcp to generate code that works for protocols other than CAN bus.
 * Extend the information that fcp is capable of encoding.

IDL example:
![fcp code showcase](https://raw.githubusercontent.com/joajfreitas/fcp-core/master/assets/code_showcase.png)

Documentation can be found in: [https://fcp-core.readthedocs.io/en/latest/](https://fcp-core.readthedocs.io/en/latest/).

### Closed issues
 * [CI](https://github.com/joajfreitas/fcp-core/issues/8)
 * [Create pyproject.toml](https://github.com/joajfreitas/fcp-core/issues/10)
 * [Remove all related to fcp_v1](https://github.com/joajfreitas/fcp-core/issues/11)
 * [Add type annotations](https://github.com/joajfreitas/fcp-core/issues/17)
 * [Remove fpi](https://github.com/joajfreitas/fcp-core/issues/13)
 * [Allow type composition](https://github.com/joajfreitas/fcp-core/issues/4)
 * [Update README](https://github.com/joajfreitas/fcp-core/issues/21)
 * [Remove the result type](https://github.com/joajfreitas/fcp-core/issues/9)
 * [Implement code generator for cpp](https://github.com/joajfreitas/fcp-core/issues/5)
 * [DBC generator](https://github.com/joajfreitas/fcp-core/issues/1)
 * [Support types smaller than 1 byte](https://github.com/joajfreitas/fcp-core/issues/64)
 * [Rethink `extends` syntax](https://github.com/joajfreitas/fcp-core/issues/65)
 * [Add description of files and directory structure](https://github.com/joajfreitas/fcp-core/issues/73)
 * [Readd default schema validation rules](https://github.com/joajfreitas/fcp-core/issues/75)
 * [Add rpc mechanism](https://github.com/joajfreitas/fcp-core/issues/59)
 * [Add arrays to IDL](https://github.com/joajfreitas/fcp-core/issues/3)
 * [Support multiple buses in fcp](https://github.com/joajfreitas/fcp-core/issues/85)
 * [Create treesitter grammar for syntax highlighting in editors](https://github.com/joajfreitas/fcp-core/issues/100)
 * [Add API docs as python docstrings](https://github.com/joajfreitas/fcp-core/issues/92)
 * [Properly support comments](https://github.com/joajfreitas/fcp-core/issues/112)
 * [Implement cpp code gen](https://github.com/joajfreitas/fcp-core/issues/12)
 * [Create CAN C generator](https://github.com/joajfreitas/fcp-core/issues/70)
 * [Add support for arrays in fcp cpp](https://github.com/joajfreitas/fcp-core/issues/121)
 * [Implement to string convertions for cpp code](https://github.com/joajfreitas/fcp-core/issues/127)
 * [Support for enums in CAN C gen](https://github.com/joajfreitas/fcp-core/issues/103)
 * [Support for period/frequency](https://github.com/joajfreitas/fcp-core/issues/104)
 * [Test builtin types in cpp gen](https://github.com/joajfreitas/fcp-core/issues/132)
 * [Add support for strings as a signal datatype](https://github.com/joajfreitas/fcp-core/issues/136)
 * [Implement python decoding library](https://github.com/joajfreitas/fcp-core/issues/2)
 * [Add support for dynamic arrays as signal datatypes](https://github.com/joajfreitas/fcp-core/issues/2)

### Changes

  * [Configure github CI](https://github.com/joajfreitas/fcp-core/pull/15) @joajfreitas
  * [Prepare fcp development](https://github.com/joajfreitas/fcp-core/pull/14). Including adding a pyproject.toml @joajfreitas
    - [Remove legacy setup.py](https://github.com/joajfreitas/fcp-core/pull/16) @joajfreitas
  * [Change license to MIT](https://github.com/joajfreitas/fcp-core/pull/19) @joajfreitas
    - [Point copyright information to the AUTHORS file](https://github.com/joajfreitas/fcp-core/pull/22) @joajfreitas
  * [Parser tests](https://github.com/joajfreitas/fcp-core/pull/26) @joajfreitas
  * [Type annotation + Type checking](https://github.com/joajfreitas/fcp-core/pull/27) @ItsNotSoftware
  * [Update readme](https://github.com/joajfreitas/fcp-core/pull/30) @joajfreitas
  * [Serialization tests](https://github.com/joajfreitas/fcp-core/pull/31) @joajfreitas
  * [config for pre commit hooks](https://github.com/joajfreitas/fcp-core/pull/32) @joajfreitas
    - [More precommit](https://github.com/joajfreitas/fcp-core/pull/33) @joajfreitas
  * [Type composition](https://github.com/joajfreitas/fcp-core/pull/35) @joajfreitas
  * [Deleted fpi](https://github.com/joajfreitas/fcp-core/pull/36) @ItsNotSoftware
  * [Dbc support](https://github.com/joajfreitas/fcp-core/pull/42) @joajfreitas
  * [Struct extension](https://github.com/joajfreitas/fcp-core/pull/44) @joajfreitas
  * [Remove semicolons](https://github.com/joajfreitas/fcp-core/pull/45) @joajfreitas
  * [Prototype for sphinx docs](https://github.com/joajfreitas/fcp-core/pull/47) @joajfreitas
  * [Redo imports](https://github.com/joajfreitas/fcp-core/pull/52) @joajfreitas
  * [Test fcp parsing errors](https://github.com/joajfreitas/fcp-core/pull/54) @joajfreitas
  * [Add Maybe type for error handling](https://github.com/joajfreitas/fcp-core/pull/55) @joajfreitas
  * [Upgrade result type](https://github.com/joajfreitas/fcp-core/pull/56) @joajfreitas
  * [Support python 3.8](https://github.com/joajfreitas/fcp-core/pull/57) @joajfreitas
  * [Test for fcp_dbc_generator](https://github.com/joajfreitas/fcp-core/pull/60) @joajfreitas
  * [Fcp dbc readme](https://github.com/joajfreitas/fcp-core/pull/61) @joajfreitas
  * [Generate dbc with composed types](https://github.com/joajfreitas/fcp-core/pull/62) @joajfreitas
  * [Add test for fcp nop](https://github.com/joajfreitas/fcp-core/pull/63) @joajfreitas
  * [Support for small types](https://github.com/joajfreitas/fcp-core/pull/66) @joajfreitas
  * [Check that code examples in markdown files are correct](https://github.com/joajfreitas/fcp-core/pull/68) @joajfreitas
  * [Add packed encoder](https://github.com/joajfreitas/fcp-core/pull/69) @joajfreitas
  * [Fix v2_parser](https://github.com/joajfreitas/fcp-core/pull/71) @ItsNotSoftware
  * [Change the extension syntax](https://github.com/joajfreitas/fcp-core/pull/74) @joajfreitas
  * [Document directory structure](https://github.com/joajfreitas/fcp-core/pull/76) @joajfreitas
  * [Add test for example in fcp dbc](https://github.com/joajfreitas/fcp-core/pull/80) @joajfreitas
  * [Fix/dbc generator](https://github.com/joajfreitas/fcp-core/pull/81) @joajfreitas
  * [Poc for rpc service](https://github.com/joajfreitas/fcp-core/pull/82) @joajfreitas
  * [Rename Signal to StructField](https://github.com/joajfreitas/fcp-core/pull/83) @joajfreitas
  * [Support for arrays](https://github.com/joajfreitas/fcp-core/pull/84) @joajfreitas
  * [Implement array support in fcp dbc](https://github.com/joajfreitas/fcp-core/pull/86) @joajfreitas
  * [Throw exception if message is too big](https://github.com/joajfreitas/fcp-core/pull/87) @joajfreitas
  * [Add units to tests](https://github.com/joajfreitas/fcp-core/pull/88) @joajfreitas
  * [Support multiple buses in one config](https://github.com/joajfreitas/fcp-core/pull/89) @joajfreitas
  * [Docstrings](https://github.com/joajfreitas/fcp-core/pull/101) @joajfreitas
  * [Fcp cpp gen](https://github.com/joajfreitas/fcp-core/pull/102) @joajfreitas
  * [CAN C generator](https://github.com/joajfreitas/fcp-core/pull/107) @ItsNotSoftware
  * [Properly support comments](https://github.com/joajfreitas/fcp-core/pull/117) @joajfreitas
  * [Supported features docs](https://github.com/joajfreitas/fcp-core/pull/126) @joajfreitas
  * [Cpp arrays](https://github.com/joajfreitas/fcp-core/pull/128) @joajfreitas
  * [First implementation of period (needs generated code checks)](https://github.com/joajfreitas/fcp-core/pull/129) @c4stelo
  * [Add missing builtin types](https://github.com/joajfreitas/fcp-core/pull/133) @joajfreitas
  * [Implement support for string builtin types](https://github.com/joajfreitas/fcp-core/pull/139) @joajfreitas
  * [Implement support for dynamic array builtin types](https://github.com/joajfreitas/fcp-core/pull/140) @joajfreitas
  * [Python decoding lib](https://github.com/joajfreitas/fcp-core/pull/143) @joajfreitas
  * [Fcp schema schema](https://github.com/joajfreitas/fcp-core/pull/145) @joajfreitas
  * [Setup release](https://github.com/joajfreitas/fcp-core/pull/148) @joajfreitas

#### Cleanups
  * [fixed v2 tests](https://github.com/joajfreitas/fcp-core/pull/7) @ItsNotSoftware
  * [Remove all related to v1](https://github.com/joajfreitas/fcp-core/pull/20) @ItsNotSoftware
  * [Move changelog to single file](https://github.com/joajfreitas/fcp-core/pull/23) @joajfreitas
  * [Cleanup](https://github.com/joajfreitas/fcp-core/pull/24) @joajfreitas
  * [Cleanup](https://github.com/joajfreitas/fcp-core/pull/25) @joajfreitas
  * [Enable colors in makefile](https://github.com/joajfreitas/fcp-core/pull/29) @joajfreitas
  * [Cleanup](https://github.com/joajfreitas/fcp-core/pull/46) @joajfreitas
  * [Fix example syntax](https://github.com/joajfreitas/fcp-core/pull/50) @joajfreitas
  * [Better printing for fcp](https://github.com/joajfreitas/fcp-core/pull/51) @joajfreitas
  * [Fix README example code](https://github.com/joajfreitas/fcp-core/pull/67) @joajfreitas
