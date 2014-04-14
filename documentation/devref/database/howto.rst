+++++
HOWTO
+++++

Recover from disappearing clients
=================================

Current (as of April 2014) versions of the MonetDB server do not check for
clients timing out. That is, if a remote client connects to the server and
opens a transaction, then dies without shutting down cleanly for some reason
(power failure, network glitch, ...), the transaction will remain open
indefinitely. MonetDB logs all incremental updates during the transaction.
Eventually, this will both cripple performance and take a huge amount of
space.

Recover by stopping and restarting the database::

  $ monetdb stop ${database}
  stoping database '${database}'... done

Start it again and the logs will be replayed and then removed::

  $ monetdb start ${database}
  starting database '${database}'... done

Note that this procedure may take a long time (several hours) to replay a
large volume of logs.

Future versions of MonetDB (unreleased as of April 2014) will include
`a fix <http://dev.monetdb.org/hg/MonetDB/rev/2efb07e174e3>`_ for this issue
by enabling ``SO_KEEPALIVE`` on the TCP socket.

Create a schema diagram
=======================

As shown in the :ref:`schema documentation <database-schema>`.

Starting from a completely blank Ubuntu 12.04 system (I used Docker)::

  $ apt-get install python-django git \
    python-django-extensions python-pygraphviz

  $ git clone https://github.com/transientskp/banana.git

  $ cd banana

  $ cat > bananaproject/settings/__init__.py
  INSTALLED_APPS = ['banana', 'django_extensions']

  $ ./manage.py graph_models -o schema.png banana

Note that you don't actually need to connect to a database for this.
