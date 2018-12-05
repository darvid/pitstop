Rationale
=========

.. image:: _static/configuration-management-sucks.jpg
   :align: right
   :scale: 50%

Configuration management in terms of simply *parsing a config file* and
*getting or setting keys* is a solved problem. Depending on application
requirements, one can use stdlib provided packages like
:mod:`configparser` and :mod:`json`, third party packages providing
support for formats like YAML and TOML, or simply use Python itself as
a means of dynamic configuration, as popular Python web frameworks do.

For extremely simple applications and prototypes, using the filesystem
and a popular data serialization format as the only means of
configuration is a perfectly reasonable solution. But what about
production? Multiple application environments? That's a solved problem,
too — just follow the `twelve-factor app`_ and *use the environment
as configuration!*

But now you have to do a lot of work for configuration keys that aren't
simple strings. Data validation, coercion, normalization, graceful
fallbacks — if you're motivated enough to concern yourself with such
things, of course. Be honest, how many times have you seen (or written)
some variation of this?

.. code-block:: python

   SECRET_KEY = os.getenv('SECRET_KEY')
   if not SECRET_KEY:
       SECRET_KEY = generate_secret_key()
   RDBMS_PORT = int(os.getenv('RDBMS_PORT', 5432))

And what about secrets? Assuming you're fortunate enough to be able to
utilize a secrets management solution like `HashiCorp Vault`_ or
`AWS SSM Parameter Store`_, you are more or less on your own to
integrate them with your application, using a third-party library or
a `shim`_. Or maybe you don't use a secrets management tool, and opt
for the "simpler" solution consisting of reading a file not checked into
source control.

.. image:: _static/most-developers.jpg
   :align: center
   :scale: 60%

Is a multi-tiered, encoding agnostic, schema driven configuration
parsing kitchen sink really necessary for most applications? No. Should
you have ten different configuration sources? Probably not. But if you
find yourself writing a similar solution repetitively and wishing there
was a better way, try out **pitstop**.


.. _twelve-factor app: https://12factor.net/config
.. _HashiCorp Vault: https://www.vaultproject.io/
.. _AWS SSM Parameter Store: https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-paramstore.html
.. _shim: https://github.com/channable/vaultenv
