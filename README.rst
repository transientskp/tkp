Introduction
============

This is the Transient Key Project (TKP).


Installation
============

You can use CMake to build this project::

 $ mkdir build && cd build && cmake ..

Don't forget that you need to populate a database also. see the database
subdirectory for details.


Requirements
============

Build
-----

- GCC & GFortran <http://gcc.gnu.org/>
- CMake <http://www.cmake.org/>
- F2PY <http://www.scipy.org/F2py>

Runtime
-------

For core functionality:

- NumPy <http://www.numpy.org/>
- SciPy <http://www.scipy.org/>
- python-dateutil <http://labix.org/python-dateutil>
- pytz <http://pytz.sourceforge.net/>
- pyfits <http://www.stsci.edu/resources/software_hardware/pyfits/>
- Boost::Python <http://www.boost.org/>
- wcslib <http://www.atnf.csiro.au/people/mcalabre/WCS/>
- h5py <http://alfven.org/wp/hdf5-for-python/>

Optional:

- pyrap <https://code.google.com/p/casacore/>
- pygsl <http://pygsl.sourceforge.net/>


testing
-------

- nosetests


Testing
=======

To run the tests you need a test database::

 $ database
 $ ./setup -d testdb -u testdb -p testdb

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


It is vital that the test suite be run before changes are committed. If your
changes cause additional test failures, they must be accompanied by
appropriate adjustments to the test suite and a full explanation in the commit
message.
Note that the full system is rather complex: in order to run all the tests, a
complete installation of MonetDB is required. This may be impractical for all
developers. Tests which require the database are disabled if database is
turned off in the user configuration::
Finally, some parts of the code will fail their tests if the optional
dependencies listed above are not available.

We adopt the following policy:

- If the database support is disabled by the user configuration (eg in
  ~/.tkp.cfg), all the database tests are automatically skipped;

- If a non-essential test within a suite cannot be executed due to the lack of
  some particular library, it can be skipped without causing the whole suite
  to fail (a good example of this is accessors.testSFImageFromAIPSpp – this is
  skipped if pyrap is not available, without causing the whole accessors test
  suite to fail);

- If a whole test suite cannot be imported or used due to missing
  dependencies, the suite is marked as a failure (eg the aipsppimage suite
  will fail unless pyrap is available);

- If the required test data is not available, a test will be skipped without
  causing the suite to fail (I'm actually not sure if this is a smart idea or
  not).


Configuration
=============

Per-user settings may be defined by in the file .tkp.cfg in your home
directory. This file follows the standard Python ConfigParser syntax.

A default configuration file may be generated as follows::

  import tkp.config
  tkp.config.write_config()

Note that this will overwrite any existing configuration file: use with care!


TKP library Details
===================
The transients pipeline library is a set of Python modules that form the backbone of the transients pipeline: it contains the routines used by the various steps in the pipeline.

The modules are separated into four subpackages:

**database**
 the routines that interface with the database. The modules in this subpackage contain the necessary SQL queries to
 match sources and find transients, as well as more general functions and a few classes.

**sourcefinder**
 the modules in this subpackage handle the detection of sources in an (2D) image.

**classification**
 the modules in this subpackage deal with the classification of detected sources, mainly through the source light curves
 (and possibly their spectra). It also contains functions to extract the required characteristics of the light curves
 for classification.

**utility**
 this subpackage contains a variety of utility functions, such as (image) data file handlers and coordinate functions.


Directory notes
===============

- *dead_scripts*: A collection of various scripts that were once useful, but are currently not in use AFAIK. To be deprecated (i.e. deleted from the current repository HEAD) if no-one yells about them within the next week or two.
- *documentation*: --
- *enduser_scripts*: Some small front-end scripts that make it easy to call routines from the command line (source extraction, image conversion etc).
- *external*: --
- *standalone_db_modules*: Modules previously kept in tkp.database that clearly contain useful code, but are not integral to the workings of the transients pipeline in its current state. Likely to be reintegrated at some point, perhaps under a 'plots' or 'quality' subpackage.
- *tests*: --
- *tkp*: The main package, see details above.



