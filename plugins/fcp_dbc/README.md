# FCP DBC generator

fcp plugin to generate CAN bus [dbc](https://www.csselectronics.com/pages/can-dbc-file-database-intro) schemas.

## Usage

```
$ fcp generate dbc <fcp source> <output directory>
```

## Supported schema fields

### Impl

 * **id**: CAN bus frame identifier
 * **device**: Sender name
 * **bus**: Name of the CAN bus line.

### SignalBlock

 * **mux_count**: Number of variants for muxed signal
 * **mux_signal**: Signal that muxes the current signal
 * **endianess**: byte order of the encoded signal
 * **bitstart**: Start bit for the current signal
 * **scale**: Scaling multiplier for the encoded signal
 * **offset**: Scaling offset for the encoded signal
 * **minimum**: Allowed minimum value for the decoded signal
 * **maximum**: Allowed maximum value for the decoded signal


## Example

```fcp
version: "3"

enum SensorState {
    Off = 0,
    On = 1,
    Error = 2,
}

struct SensorInformation {
    temperature @0: f32 | unit("C"),
    sensors_state @1: SensorState,
    sensor_id @2: u8,
}

impl can for SensorInformation {
    id: 100,
    device: "ecu1",

    signal temperature {
        mux_count: 16,
        mux_signal: "sensor_id",
    },

    signal sensor_state {
        mux_count: 16,
        mux_signal: "sensor_id",
    },
}
```
