.. _testing:

+++++++
Testing
+++++++

The ``tests`` directory contains a (reasonably) comprehensive TraP test suite.
Tests are written following the `Python unittest
<https://docs.python.org/2/library/unittest.html>`_ conventions. Although they
can be run using just the standard Python library tools, you might find that
`nose <https://nose.readthedocs.org/en/latest/>`_ provides a more convenient
interface.

Test data
+++++++++

Many of the tests require data files which are distributed separately from the
TraP. Having cloned the TraP repository (into the directory ``tkp`` in this
example), fetch the appropriate test data as follows::

  $ cd tkp
  $ git submodule init
  $ git submodule update

In future, running ``git submodule update`` again will fetch the latest
version of the test data if required.

By default, the test suite will look for data in the appropriate subdirectory
of your checked out Trap source. However, if the data has been installed
elsewhere, or if you are running the test suite against an installed copy of
the TraP, you can specify the data location by exporting the ``TKP_TESTPATH``
environment variable.

If the data is not available, the relevant tests will be skipped. The partial
test suite should still complete successfully; note that your copy of the TraP
will not be fully tested.

Database
++++++++

Many of the tests require interaction with the :ref:`pipeline database
<database-intro>`. A convient way to configure the database is by using
environment variables. For example::

  $ export TKP_DBENGINE=xxx
  $ export TKP_DBNAME=xxx
  $ export TKP_DBHOST=xxx
  $ export TKP_DBPORT=xxx
  $ export TKP_DBUSER=xxx
  $ export TKP_DBPASSWORD=xxx
  $ tkp-manage.py initdb

If you do not have or need a database, you can disable all the tests which
require it by exporting the variable ``TKP_DISABLEDB``. The partial test suite
should still complete successfully, but your copy of the TraP will not be
fully tested.

Running the tests
+++++++++++++++++

Within the ``tests`` directory, use the ``runtests.py`` script to start the
test suite using ``nose``::

  $ cd tests
  $ python runtests.py -v

Command line arguments (such as ``-v``, above) are passed onwards to ``nose``;
you can use them, for example, to select a particular subset of the suite to
run.

Often it is convenient to run the TraP against a work-in-progress version of
the TraP while continuing to use other libraries and tools installed on the
system. This just requires setting the ``PYTHONPATH`` environment variable to
the root of the development tree::

  $ cd tkp
  $ export PYTHONPATH=$(pwd):${PYTHONPATH}
  $ cd tests
  $ python runtests.py -v
