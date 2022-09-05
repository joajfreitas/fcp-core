# FCP v2 goals

## Stage 1
 * [x] Replace the json config file with the fcp idl
 * [x] Remove the can id split between dev id and msg id - moved to code generator
 * [x] Change the data model. Use message as a top level construct
 * [x] Remove fcp gui
 * [x] Remove all non schema related tags from fcp idl
 * [x] Replace current code generation scheme with a pluggable system

## Stage 2
 * [x] Update logger setup
 * [ ] Implement configuration verifier
 * [ ] Implement fcp v1 -> fcp v2
 * [ ] Implement automatic signal start 
 * [ ] Update documentation generator

## Stage 3
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
