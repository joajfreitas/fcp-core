![](https://gitlab.com/joajfreitas/can-ids-spec/badges/master/pipeline.svg)

# FST CAN Protocol
JSON specification for can bus messages and helper tools.

## Install

	$ pip install fcp

## Usage

	$ fcp
	Usage: fcp [OPTIONS] COMMAND [ARGS]...
	
	Options:
	  --version
	  --help     Show this message and exit.
	
	Commands:
	  c-gen             Transform FCP json into a C library.
	  docs              Generate FCP documentation.
	  dump-cfg-list
	  dump-cmd-list
	  dump-dev-list
	  dump-log-list
	  dump-msg-list
	  dump-signal-list
	  gui               Launch FCP json editor GUI.
	  init              Create a basic FCP json file.
	  print-dev
	  print-log
	  print-msg
	  print-signal
	  read-dbc          Transform a DBC file into FCP json.
	  validate          Verify correctness of FCP json file.
	  write_dbc         Transform FCP json file into a DBC :param json_file:

## Implementations

 * Rust: https://gitlab.com/joajfreitas/fcp-rust
 * C++: https://gitlab.com/joajfreitas/fcp-cpp

## Documentation

See [readthedocs.io](https://fcp-core.readthedocs.io/en/latest/)
