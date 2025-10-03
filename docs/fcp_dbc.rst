=======
fcp_dbc
=======

fcp plugin to generate CAN bus `dbc <https://www.csselectronics.com/pages/can-dbc-file-database-intro>` schemas.

Usage
=====

.. code-block:: bash

    fcp generate dbc <fcp source> <output file>

Supported schema fields
=======================

Impl
---------

#. **id**: CAN bus frame identifier
#. **device**: Sender name

SignalBlock
-----------

#. **mux_count**: Number of variants for muxed signal
#. **mux_signal**: Signal that muxes the current signal
#. **endianess**: byte order of the encoded signal
#. **bitstart**: Start bit for the current signal
#. **scale**: Scaling multiplier for the encoded signal
#. **offset**: Scaling offset for the encoded signal
#. **minimum**: Allowed minimum value for the decoded signal
#. **maximum**: Allowed maximum value for the decoded signal


Example
=======

.. code-block:: protobuf

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

    device ecu1 {
        protocol can {
            impl SensorInformation {
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
            },
        },
    }

API
===

.. automodule:: fcp_dbc.generator
   :members:

.. automodule:: fcp_dbc.dbc_writer
   :members:
