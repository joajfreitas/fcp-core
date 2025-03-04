
Services
========

Syntax
------

.. code-block::

    service: "service" identifier "{" rpc* "}"
    rpc: "rpc" identifier "(" identifier ")"  "returns" identifier

Example
^^^^^^^

.. code-block::

    version: "3"
    struct Input {
        field1: u32,
        field2: u32,
    }

    struct Output {
        result: u32,
        carry: u1,
    }

    service foo {
        rpc bar(Input) returns output
    }

CAN bus
-------

.. code-block::

    version: "3"
    struct Input {
        field1: u32,
        field2: u32,
    }

    struct Output {
        result: u32,
        carry: u1,
    }

    service foo {
        rpc bar(Input) returns output
    }

    impl can for foo {
        service_id = 1,
        device = "ecu1",

        rpc bar {
            method_id = 1,
        }
    }
