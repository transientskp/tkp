.. _installation:

++++++++++++
Installation
++++++++++++

To install the TraP you must:

#. Install and configure a suitable back-end database;
#. Optionally, install and configure `MongoDB <http://www.mongodb.org/>`_
   as a :ref:`pixel store <mongodb-intro>`;
#. Install the core pipeline dependencies (casacore etc);
#. Install the TraP itself, via the 'tkp' Python package.

Some details on each of these steps is provided below.

Note, though, that the overall procedure is complex, and can be difficult if
you've not had prior experience with e.g. database configuration.
It is possible instead to use
`Vagrant <http://www.vagrantup.com/>`_ to quickly and easily set up a virtual
machine which provides a fully configured and working ready-to-go pipeline and
supporting tools. This is a quick and easy way to get up and running for
testing purposes or when simplicity is preferable to ultimately high
performance. Refer to the `Vagrant TraP
<https://github.com/transientskp/vagrant_trap>`_ repository for details and
instructions.

Back-end Database
=================

The TraP supports one database management systems for use as the
:ref:`pipeline database <database-intro>`: `PostgreSQL <http://www.postgresql.org/>`_.
PostgreSQL is available for common operating systems and package
managers. Install it on your system.

A complete description of configuring your database management system is
beyond the scope of this guide: refer to its documentation for details. Some
brief notes on things to look out for follow.

PostgreSQL
----------

Ensure that the access rights to your server are set appropriately, for
example to trust connections from whichever machine(s) will be used to run the
TraP. This is done by editing ``pg_hba.conf``, and can be verified by
connecting with the command line tool ``psql``.

Pixel Store
===========

Optionally, the pixel contents of all images processed (but not the metadata)
can be saved to a `MongoDB <http://www.mongodb.org/>`_ database for future
reference (e.g. via the `Banana <https://github.com/transientskp/banana>`_ web
interface). This naturally requires that a MongoDB daemon is installed and
configured to accept requests from TraP clients.


Core Dependencies
=================

TraP mostly depends on standard packages which you should be able to find
in your system's package manager (e.g. apt, yum, etc).
To install the TraP, you will need the following:

* C++ and Fortran compilers (tested with `GCC <http://gcc.gnu.org/>`_)
* `GNU Make <https://www.gnu.org/software/make/>`_
* `Python <https://www.python.org/>`_ (2.7.x series, including header files)
* `Boost Python <http://www.boost.org/doc/libs/release/libs/python/doc/>`_
* `WCSLIB <http://www.atnf.csiro.au/people/mcalabre/WCS/>`_


TraP also has a number of Python-package dependencies. The install process
will attempt to download and install these as necessary, but you may
wish to pre-install system packages for some of the following,
in order to save time recompiling them from source:

* `NumPy <http://www.numpy.org/>`_ (at least version 1.3.0)
* `SciPy <http://www.scipy.org/>`_ (at least version 0.7.0)
* `python-dateutil <http://labix.org/python-dateutil>`_ (at least version 1.4.1)
* `python-psycopg2 <http://initd.org/psycopg/>`_ (for PostgreSQL)

To work with the :ref:`pixel store <mongodb-intro>` you will also need:

* `PyMongo <http://api.mongodb.org/python/current/>`_

Finally, TraP also requires the 'casacore' library, which is not yet widely
available as a system package:

* `casacore <https://github.com/casacore/casacore/>`_ (including measures data)

Casacore can be compiled from source, or users of
Ubuntu-based distributions might find the
`Radio Astronomy Launchpad page <https://launchpad.net/~radio-astro/+archive/ubuntu/main>`_
useful.

.. warning::

    See also the note on :ref:`casacore measures data <casacore-measures>`,
    which can often cause confusing errors if out-of-date or incorrectly
    configured.


Install TKP
============

Once all dependencies have been satisfied, installation should be
straightforward. You can either install from source::

  $ git clone https://github.com/transientskp/tkp.git
  $ cd tkp
  $ pip install -e ".[pixelstore]"

Following installation, including setting up and configuring the database,
follow the :ref:`test procedure <testing>` to ensure that everything is
working and ready for use.
