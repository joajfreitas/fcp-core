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
 * Develop an IDL (interface description language) to replace the old json configuration
 * Allow fcp to generate code that works for protocols other than CAN bus.
 * Extend the information that fcp is capable of encoding.

IDL example:
![fcp code showcase](https://raw.githubusercontent.com/joajfreitas/fcp-core/master/assets/code_showcase.png)


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
  * [Deleted fpi](https://github.com/joajfreitas/fcp-core/pull/36) @joajfreitas

### Cleanups
  * [fixed v2 tests](https://github.com/joajfreitas/fcp-core/pull/7) @ItsNotSoftware
  * [Remove all related to v1](https://github.com/joajfreitas/fcp-core/pull/20) @ItsNotSoftware
  * [Move changelog to single file](https://github.com/joajfreitas/fcp-core/pull/23) @joajfreitas
  * [Cleanup](https://github.com/joajfreitas/fcp-core/pull/24) @joajfreitas
  * [Cleanup](https://github.com/joajfreitas/fcp-core/pull/25) @joajfreitas
  * [Enable colors in makefile](https://github.com/joajfreitas/fcp-core/pull/29) @joajfreitas


 * Remove fcp gui
 * Implement new fcp IDL
 * Implement converter for old fcp json configuration to new IDL.
 * Implement generator for old json configuration
