.. pitstop documentation master file, created by
   sphinx-quickstart on Sat Dec  1 16:51:23 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

pitstop
=======

.. include:: ../../README.rst
   :start-after: -begin-short-
   :end-before: -end-short-

Features
--------

.. image:: _static/pitstop.png
   :align: center

.. include:: ../../README.rst
   :start-after: -begin-features-
   :end-before: -end-features-

Installation
------------

**pitstop** has a hard minimum requirement of Python 3.7.

In general, the Python package can be installed with ``pip``, which will
include the ``pitstop`` command line utility.

.. code-block:: shell

   $ pip install pitstop

However, if you are *only* going to be using the CLI, it is highly
recommended to use `pipsi <https://github.com/mitsuhiko/pipsi>`_
instead:

.. code-block:: shell

   $ pipsi install pitstop

.. toctree::
   :maxdepth: 2

   Library Usage <library>
   API Reference <pitstop>
