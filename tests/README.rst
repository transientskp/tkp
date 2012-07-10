Usage
=====

First setup a test database::

 $ cd ../../../database
 $ ./setup.sh -d testdb -u testdb -p testdb

Then setup your PYTHONPATH to point to the TKP source folder (and maybe other packages::

 $ export PYTHONPATH=..

And then run python nose from the tests folder::

 $ nosetests

