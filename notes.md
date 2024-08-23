## FCP v2 goals

### Stage 1
 * [x] Replace the json config file with the fcp idl
 * [x] Remove the can id split between dev id and msg id - moved to code generator
 * [x] Change the data model. Use message as a top level construct
 * [x] Remove fcp gui
 * [x] Remove all non schema related tags from fcp idl
 * [x] Replace current code generation scheme with a pluggable system

### Stage 2
 * [x] Update logger setup
 * [X] Implement configuration verifier
 * [X] Implement fcp v1 -> fcp v2
 * [X] Implement automatic signal start 
 * [ ] Update documentation generator

### Stage 3
 * [ ] Implement arrays in IDL
 * [ ] Implement struct nesting
 * [ ] Implement fcp file encoding
 * [ ] Implement file preview


```
device dcu

message req_get: device(all) | id(2) | dlc(8) {
  ...
}
```

## MVP

- Abstract library with support for a myriad of communication protocols and code languages
- Unique .fcp file that defines the information about the desired messages
- Plugins are unique for communication protocol and generated code language. These act as code and message generators.
- Plugin manager through pyPi?
