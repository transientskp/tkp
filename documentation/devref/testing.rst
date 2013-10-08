.. _testing:

Testing
=======

For testing we advice you to use nosetests. All tests are located in the
tests subfolder.

To run the tests you need a test database::

 $ cd database
 $ ./setup.sh -d testdb -u testdb -p testdb

If you don't want to test the DB you can turn these tests off::

   $ cat >> ~/.tkp.cfg
   [database]
   enabled = False

Then obtain the test data (requires authentication)::

 $ svn co http://svn.transientskp.org/data/unittests/tkp_lib tests/data

tests/data is the default location You can change the location here::

   $ cat >> ~/.tkp.cfg
   [test]
   datapath = /path/to/storage/unittests/tkp_lib


Then setup your PYTHONPATH to point to the TKP source folder (and maybe other
packages like monetdb)::

 $ export PYTHONPATH=<location of TKP project>

And then run python nose from the tests folder::

 $ cd tests && nosetests

It is vital that the test suite be run before changes are committed. Also we
try to keep the coverage as high as possible e.g. make sure all code lines
in the tkp module are 'touched' at least once.
