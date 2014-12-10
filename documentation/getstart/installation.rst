.. _installation:

++++++++++++
Installation
++++++++++++

To install the TraP you must:

#. Install and configure a suitable back-end database;
#. Optionally, install and configure `MongoDB <http://www.mongodb.org/>`_
   as a :ref:`pixel store <mongodb-intro>`;
#. Install the core pipeline dependencies;
#. Build and install the TraP itself.

Some details on each of these steps is provided below.

Note, though, that the overall procedure is complex, and correctly configuring
all the various components can be difficult. It is possible instead to use
`Vagrant <http://www.vagrantup.com/>`_ to quickly and easily set up a virtual
machine which provides a fully configured and working ready-to-go pipeline and
supporting tools. This is a quick and easy way to get up and running for
testing purposes or when simplicity is preferable to ultimately high
performance. Refer to the `Vagrant TraP
<https://github.com/transientskp/vagrant_trap>`_ repository for details and
instructions.

Back-end Database
=================

The TraP supports two database management systems for use as the
:ref:`pipeline database <database-intro>`: `MonetDB
<http://www.monetdb.org/>`_ and `PostgreSQL <http://www.postgresql.org/>`_.
Both are available for common operating systems and package managers: pick one
and install it.

A complete description of configuring your database management system is
beyond the scope of this guide: refer to its documentation for details. Some
brief notes on things to look out for follow.

PostgreSQL
----------

Ensure that the access rights to your server are set appropriately, for
example to trust connections from whichever machine(s) will be used to run the
TraP. This is done by editing ``pg_hba.conf``.

MonetDB
-------

To be able to administer MonetDB databases, you need to be a member of the
``monetdb`` group.

To issue remote management commands, such as database creation, you need to
both enable this functionality and set a passphrase::

  monetdbd set control=yes ${dbfarm}
  monetdbd set passphrase=${myphassphrase} ${dbfarm}


Pixel Store
===========

Optionally, the pixel contents of all images processed (but not the metadata)
can be saved to a `MongoDB <http://www.mongodb.org/>`_ database for future
reference (e.g. via the `Banana <https://github.com/transientskp/banana>`_ web
interface). This naturally requires that a MongoDB daemon is installed and
configured to accept requests from TraP clients.


Core Dependencies
=================

To build the TraP, you will need:

* C++ and Fortran compilers (tested with `GCC <http://gcc.gnu.org/>`_)
* `GNU Make <https://www.gnu.org/software/make/>`_
* `Python <https://www.python.org/>`_ (2.7.x series *only*, including header files)
* `NumPy <http://www.numpy.org/>`_ (at least version 1.3.0)
* `Boost Python <http://www.boost.org/doc/libs/release/libs/python/doc/>`_
* `WCSLIB <http://www.atnf.csiro.au/people/mcalabre/WCS/>`_
* `pywcs <http://stsdas.stsci.edu/astrolib/pywcs/>`_

In addition to the above, to run the TraP you will need:

* `SciPy <http://www.scipy.org/>`_ (at least version 0.7.0)
* `python-dateutil <http://labix.org/python-dateutil>`_ (at least version 1.4.1)
* `pyrap <https://code.google.com/p/pyrap/>`_ and
  `casacore <https://code.google.com/p/casacore/>`_ (including measures data)

To work with the pipeline database, you will need at least one of:

* `python-monetdb <https://pypi.python.org/pypi/python-monetdb>`_ (for MonetDB)
* `psycopg2 <http://initd.org/psycopg/>`_ (for PostgreSQL)

To work with the :ref:`pixel store <mongodb-intro>` you will need:

* `PyMongo <http://api.mongodb.org/python/current/>`_

Most of these dependencies should be easily satisfied by operating
system-level package management or through the `Python Package Index
<https://pypi.python.org/pypi>`_, and we strongly suggest you take advantage
of that convenience rather than building everything from source. The most
notable exceptions are pyrap and casacore: these are not commonly packaged in
mainstream distributions. They can be compiled from source, or users of
Ubuntu-based distributions might find the `SKA South Africa Launchpad page
<https://launchpad.net/~ska-sa>`_ useful.

.. warning::

    See also the note on :ref:`casacore measures data <casacore-measures>`,
    which can often cause confusing errors if out-of-date or incorrectly
    configured.


Build and Install
=================

Once all dependencies have been satisfied, building should be
straightforward::

  $ git clone https://github.com/transientskp/tkp.git
  $ cd tkp
  $ python setup.py install

Following installation, including setting up and configuring the database,
follow the :ref:`test procedure <testing>` to ensure that everything is
working and ready for use.

.. _installation_distributed:

Distributed processing via Celery
=================================
If you wish to run a TraP job across multiple machines, you may optionally
also install a :ref:`Celery <celery-intro>` broker (at least version 3.0);
see the `Celery website <http://www.celeryproject.org/>`_ for further details
of the Celery package.

Multiple different options for Celery brokers are available;
refer to the Celery documentation for details.
We have had success with `RabbitMQ <http://www.rabbitmq.com/>`_.

This functionality is currently not well supported
and should be considered experimental.