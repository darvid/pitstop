Concepts
========

Meta-configuration
------------------

Configuration that describes your application configuration schema,
configuration backends, and other **pitstop** configuration.

Backends
--------

Drivers for configuration sources, such as the filesystem, in-memory
caches, key-value stores, and various other database engines.

Strategies
----------

Public interfaces to configuration backends. Strategies resolve
configuration keys based on a given schema and prioritized list of
backends, and can produce a complete snapshot of application
configuration.

Encodings
---------

Encoders and decoders for popular data serialization formats, such as
JSON, TOML, YAML, INI, and more.
