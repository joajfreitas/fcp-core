![](https://github.com/joajfreitas/fcp-core/actions/workflows/ci.yml/badge.svg)

# FST Communication Protocol

FCP is an interface description language to exchange information independently of language and platform.

## Install

	$ pip install fcp

## Example

```fcp
version: "3"

mod temperature;

/*this is a comment*/
enum SensorState {
        Off = 0,
        On = 1,
        Error = 2,
}

struct SensorInformation {
    temperature @ 0: Temperature,
    sensor_state @ 1: SensorState,
}
```

## Documentation

See [readthedocs.io](https://fcp-core.readthedocs.io/en/latest/)

 * [Contributing](./CONTRIBUTING.md)
 * [Authors](./AUTHORS)
 * [License](./LICENSE)
