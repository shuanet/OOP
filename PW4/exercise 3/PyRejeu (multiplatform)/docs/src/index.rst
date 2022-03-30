.. PyRejeu documentation master file, created by
   sphinx-quickstart on Thu Mar 30 17:17:38 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to PyRejeu's documentation!
===================================

PyRejeu is an application written in python whose the aim is to replay Air Traffic. It can replace legacy rejeu application written in ada. Indeed:
 * It supports many commands/events handled by legacy rejeu on ivy bus
 * It can read trafic file created for rejeu (only text format is supported)

Moreover, PyRejeu supports two other ways to communicate with clients:
 * `AMQP <https://www.amqp.org/>`_ protocol thanks to the pika library
 * `ZeroMQ framework <http://zeromq.org/>`_ thanks to the pyzmq library

See  the :ref:`communication-section` section for details.

.. toctree::
   :maxdepth: 2

   installation
   communication
   messages

