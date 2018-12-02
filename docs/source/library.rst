Using the Library
=================

Quickstart
----------

The following example is not typical of how you'd use **pitstop** in
practice, but gives you a feel for the API:

.. code-block:: python

   from pitstop.backends.base import DictBackend
   from pitstop.strategies import strategy_factory

   # The metaconfig defines your actual configuration backends and
   # schema. In this example, we're using an in-memory DictBackend so
   # we don't need to define any backends.
   metaconfig = {
       'strategy': {'version': 1},
       'schema': {
           'frobnicator_level': {'type': 'integer', 'default': 42},
           'frobnicator_name': {'type': 'string'},
       }
   }

   # A configuration fragment, akin to one that might be deserialized
   # from a popular configuration format (JSON, YAML, INI, whatever)
   config = {'frobnicator_name': 'foobar'}

   # Backends require a name and priority at minimum, more on that
   # later. ``obj`` is a required parameter of the DictBackend, it's
   # the configuration dictionary itself.
   backend = DictBackend(name='dict', priority=1, obj=config)

   # Create a strategy from our metaconfig, and add the DictBackend.
   # Backends can be added and removed ad-hoc within your application
   # or library at any time.
   strategy = strategy_factory(metaconfig)
   strategy.backends.add(backend)

   # Resolving is what aggregates every backend within the strategy into
   # a single, JSON serializable mapping.
   print(strategy.resolve())
   # -> {'frobnicator_level': 42, 'frobnicator_name': 'foobar'}

   # You can also get keys individually.
   print(strategy.get('frobnicator_name'))
   # -> 'foobar'
