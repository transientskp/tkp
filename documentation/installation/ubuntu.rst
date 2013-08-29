.. _ubuntu:

======
Ubuntu
======

This page describes how to install the Transient Pipeline software on Ubuntu.
Tested with Ubuntu 12.04.


Casacore
========

Casacore is a collection of libraries which can be used to perform astronomical
calculations and operations.

There are two ways to install Casacore, use our precompiled binary packages or
compile Casacore by yourself. Some people like to compile casacore themselves
to have more control over compilation flags and installation location.

Binary packages
---------------

To install the pre compiled binaries run::

    $ sudo apt-get install software-properties-common
    $ sudo add-apt-repository ppa:gijzelaar/aartfaac
    $ sudo apt-get update
    $ sudo apt-get install libcasacore-dev casacore-data


Manual casacore compilation
---------------------------

This will compile casacore from source.

First, install its dependencies::

   $ sudo apt-get install subversion cmake build-essential flex bison   \
        libblas-dev liblapack-dev libcfitsio3-dev wcslib-dev libfftw3-dev \
        libhdf5-dev libreadline-dev libncurses5-dev wget

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
         -DUSE_HDF5=ON -DUSE_OPENMP=ON
   $ make
   $ sudo make install


Pyrap
=====

Pyrap is a a Python wrapper around casacore.

Pyrap depends on scons, numpy and boost::

   $ sudo apt-get install scons python-numpy-dev python-dev \
        libboost-python-dev python-setuptools subversion libblas-dev \
        liblapack-dev gfortran wcslib-dev libcfitsio3-dev

To install install Pyrap::

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


MonetDB
^^^^^^^

monetDB is not included in Ubuntu, but there is a MonetDB repository available
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

For more information see the `MonetDB ubuntu packages manual`_.


Broker
------

If you want to run `Celery`_ workers, you need a broker. There are multiple
`brokers`_ where you can choose from. If you do not have a compelling reason
to choose another, we suggest `RabbitMQ`_::

    $ sudo apt-get install rabbitmq-server

.. _Celery: http://www.celeryproject.org/
.. _brokers: http://docs.celeryproject.org/en/latest/getting-started/brokers/index.html
.. _RabbitMQ: http://www.rabbitmq.com/
.. _homebrew: http://mxcl.github.io/homebrew/
.. _homebrew SKA tap: https://github.com/ska-sa/homebrew-tap/
.. _PostgreSQL: http://www.postgresql.org/
.. _MonetDB: http://www.monetdb.org/
.. _MonetDB ubuntu packages manual: http://dev.monetdb.org/downloads/deb/
