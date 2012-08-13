Usage
=====

First setup a test database::

 $ cd ../../../database
 $ ./setup.sh -d testdb -u testdb -p testdb

Then obtain the test data (requires authentication)::

 $ svn co http://svn.transientskp.org/data/unittests/tkp_lib data


Then setup your PYTHONPATH to point to the TKP source folder (and maybe other packages::

 $ export PYTHONPATH=..

And then run python nose from the tests folder::

 $ nosetests

