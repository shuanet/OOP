
Installation/Usage
==================

To run PyRejeu, you have to install the following programs/modules
 * python3 (version >= 3.4.0)
 * SqlAlchemy_
 * `ivy-python <https://pypi.python.org/pypi/ivy-python>`_ if you want to use ivy bus
 * `PyZMQ <https://github.com/zeromq/pyzmq>`_ if you want to use ZMQ framework to exchange messages
 * `Pika <https://pika.readthedocs.io/en/0.10.0/>`_ if you want to use AMQP protocol to exchange messages (with rabbitmq for example)

.. _SqlAlchemy: http://www.sqlalchemy.org/

Run in the source directory
---------------------------

Like most of python applications, PyRejeu can be launch directly in the source
directory, simply with the command line::

    ./pyrejeu.py <data_file>

Available options (--help)::

    Usage: pyrejeu.py [options] <data_file>

    Options:
    -h, --help            show this help message and exit
    -d, --debug           View debug message.
    -b BUS_ID, --bus=BUS_ID
                          Bus id (format ivy://@IP:port for IVY |
                          zmq://*:rpc_port:evt_port for ZeroMQ  |
                          amqp://host:port for AMQP (with rabiitmq for ex)
                          default to ivy://127.255.255.255:2010)
    -a APP_NAME, --appname=APP_NAME
                          Application Name

Debian Package
--------------

A debian package can be built for PyRejeu, thanks to files included in the
debian folder. To build the package, you can use for example pbuilder/pdebuild
utilities (https://pbuilder.alioth.debian.org/)
