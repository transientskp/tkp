.. _ubuntu:

======
Ubuntu
======

This page describes how to install the Transient Pipeline software on Ubuntu.
Tested with Ubuntu 12.04.


Casacore & Pyrap
================

Casacore is a collection of libraries which can be used to perform astronomical
calculations and operations. Pyrap is the python wrapper around casacore.

There are two suggested ways to install these packages: use our precompiled
binary packages or build them yourself. Some people like to compile from
source to have more control over compilation flags and installation location.

Binary packages
---------------

To install the pre compiled binaries run::

    $ sudo apt-get install software-properties-common
    $ sudo add-apt-repository ppa:gijzelaar/aartfaac
    $ sudo apt-get update
    $ sudo apt-get install libcasacore-dev casacore-data pyrap


Manual compilation
------------------

This will compile casacore from source.

First, install its dependencies::

   $ sudo apt-get install subversion cmake build-essential flex bison   \
        libblas-dev liblapack-dev libcfitsio3-dev wcslib-dev libfftw3-dev \
        libhdf5-dev libreadline-dev libncurses5-dev wget scons python-numpy-dev\
        python-dev libboost-python-dev python-setuptools subversion gfortran

Get the measures data::

   $ cd /tmp
   $ wget ftp://ftp.atnf.csiro.au/pub/software/measures_data/measures_data.tar.bz2
   $ sudo mkdir /usr/local/share/casacore && cd /usr/local/share/casacore
   $ sudo tar jxvf /tmp/measures_data.tar.bz2


Finally, casacore itself::

   $ cd /tmp
   $ svn checkout http://casacore.googlecode.com/svn/trunk/ casacore
   $ mkdir casacore/build && cd casacore/build
   $ cmake .. -DDATA_DIR=/usr/local/share/casacore/data -DUSE_FFTW3=ON \
         -DUSE_OPENMP=ON
   $ make
   $ sudo make install


and Pyrap::

   $ cd /tmp
   $ svn checkout http://pyrap.googlecode.com/svn/trunk/ pyrap
   $ cd pyrap
   $ ./batchbuild-trunk.py  #  append `--casacore-root=/usr` if you installed the binary packages


Transient Pipeline
==================

If you don't have the Trap source code yet, you need to to fetch it::

   $ sudo apt-get install git cmake build-essential python-pip python-numpy \
        python-scipy python-pygresql
   $ cd /tmp
   $ git clone https://github.com/transientskp/tkp.git
   $ mkdir tkp/build && cd tkp/build
   $ cmake ..
   $ make
   $ sudo make install
   $ cd ..
   $ pip install -r requirements.txt


Optional dependencies
=====================

Database
--------

If you want to run the pipeline you need to store the results somewhere. TKP
currently supports two database systems, `PostgreSQL`_ and `MonetDB`_. Pick one.

PostgreSQL
^^^^^^^^^^

PostgreSQL is included in Ubuntu::

    $ sudo apt-get install postgresql

After package installation, you must configure access rights to your postgres
server, by editing
`/etc/postgresql/9.1/main/pg_hba.conf
<http://www.postgresql.org/docs/9.1/static/auth-pg-hba-conf.html>`_.

For a typical development (i.e. possibly insecure) installation, you will
probably want to edit the pre-existing entries to something along the lines
of::

   local   all             all                                     trust
   host    all             all             127.0.0.1/32            trust

with all other lines commented out. Then restart the server::

   $ sudo service postgresql restart

You can check everything is working using ``psql``::

   $ psql -U postgres

You should now be able to run the :ref:`initdb <getstart-initdb>` process,
however you should note that by default all databases must be created with
user `postgres` - to allow creation of databases with other user-owners, you
must first add a new `role
<http://www.postgresql.org/docs/9.1/static/sql-createrole.html>`_, e.g.::

   $ psql -U postgres
   postgres=# CREATE ROLE myuser WITH CREATEDB SUPERUSER LOGIN;

You should now be able to run ``tkp-manage.py initdb`` with the newly added
username.

MonetDB
^^^^^^^

MonetDB is not included in Ubuntu, but there is a MonetDB repository available
with prebuild binaries. To install these packages::

    $ sudo apt-get install software-properties-common
    $ sudo add-apt-repository 'deb http://dev.monetdb.org/downloads/deb/ precise monetdb'
    $ wget --output-document=- http://dev.monetdb.org/downloads/MonetDB-GPG-KEY | sudo apt-key add -
    $ sudo apt-get update
    $ sudo apt-get install monetdb5-sql monetdb-client

To be able to manage MonetDB databases you need to add yourself to the MonetDB
group::

    $ sudo usermod -a -G monetdb $USER

When you next log in you will be a member of the appropriate group.

If you want to be able to issue remote management command like creating
databases you need to enable this and set a passphrase
(mysecretpassphrase here)::

    $ monetdbd set control=yes /var/lib/monetdb
    $ monetdbd set passphrase=mysecretpassphrase /var/lib/monetdb

For more information see the `MonetDB ubuntu packages manual`_.


Celery Broker
-------------

If you want to run :ref:`Celery <celery-intro>` workers, you need a broker.
We suggest `RabbitMQ`_::

    $ sudo apt-get install rabbitmq-server

MongoDB
-------

If you want to use the :ref:`pixel store <mongodb-intro>`, you will need to
installed MongoDB on the chosen database host::

    $ sudo apt-get install mongodb

See the `MongoDB documentation
<http://docs.mongodb.org/manual/tutorial/install-mongodb-on-ubuntu/>`_ for
full instructions.

You will also need to make sure the Python wrapper is available on your client
machine::

    $ sudo apt-get install python-pymongo


.. _RabbitMQ: http://www.rabbitmq.com/
.. _homebrew: http://mxcl.github.io/homebrew/
.. _homebrew SKA tap: https://github.com/ska-sa/homebrew-tap/
.. _PostgreSQL: http://www.postgresql.org/
.. _MonetDB: http://www.monetdb.org/
.. _MonetDB ubuntu packages manual: http://dev.monetdb.org/downloads/deb/
