===================
VOEvent-ZeroMQ Demo
===================

This is a proof-of-concept of distributing `VOEvent
<http://www.voevent.org/>`_ packets using `ZeroMQ <http://www.zeromq.org>`_.
This code is not production ready and is not intended for "serious" use.

Server
======

The server connects to a broker which provides events using the `VOEvent
Transport Protocol <http://www.ivoa.net/Documents/Notes/VOEventTransport/>`_
(by default, we use that provided by `DC-3 Dreams
<http://voevent.dc3.com/>`_). Events are rebroadcast using the ZeroMQ
"pub/sub" system.

Requirements
------------

- Python 2.6 or 2.7 (other versions untested).
- `Python bindings for ZeroMQ <http://www.zeromq.org/bindings:python>`_.
- `Twisted <http://twistedmatrix.com/trac/>`_.

Configuration
-------------

Edit the file `config.py`.

Usage
-----

Use the `twistd` command to run the server. For example::

  $ twistd -ny server.tac

Client
======

The client connects to the server and receives events over ZeroMQ. It simply
dumps the received events to standard output.

Requirements
------------

- Python 2.6 or 2.7 (other versions untested).
- `Python bindings for ZeroMQ <http://www.zeromq.org/bindings:python>`_.

Configuration
-------------

Edit the source.

Usage
-----

Run the client using Python::

  $ python client.py
