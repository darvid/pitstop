Command-Line Interface
======================

.. note::

   **pitstop** is currently in alpha, so the library API and
   command-line interface is subject to change and break backwards compatibility.

The purpose of the **pitstop** CLI is to provide a convenient utility
for developers that facilitates interaction with every tier of
configuration, without having to write any code or deal with connecting
to backends individually.

.. code-block:: text

    pitstop 0.1a1

    Usage:
      command [options] [arguments]

    Options:
      -h, --help                      Display this help message
      -q, --quiet                     Do not output any message
      -V, --version                   Display this application version
          --ansi                      Force ANSI output
          --no-ansi                   Disable ANSI output
      -n, --no-interaction            Do not ask any interactive question
      -v|vv|vvv, --verbose[=VERBOSE]  Increase the verbosity of messages: 1 for normal output, 2 for more verbose output and 3 for debug

    Available commands:
      help     Displays help for a command
      list     Lists commands
      resolve  Resolve all backend sources and output resolved configuration.

``pitstop resolve``
-------------------

Given a meta-configuration file and strategy, resolves a snapshot of
application configuration across all configuration backends into a
JSON object. This is useful for debugging, but also for applications not
written in Python that could benefit from **pitstop**'s functionality,
as they can simply wrap the ``pitstop`` command and parse the output.

Because dogfood is delicious, here's an example of **pitstop**'s own
meta-configuration resolved from its ``pyproject.toml``::

  $ pitstop resolve
  {
    "tool": {
      "pitstop": {
        "backends": [
          {
            "driver": "fs",
            "priority": 1,
            "encoding": "toml",
            "options": {
              "path": "pyproject.toml"
            }
          }
        ],
        "strategy": {
          "version": 1,
          "backend_priority_overrides": null
        }
      }
    }
  }
