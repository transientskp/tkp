Introduction
============

This is the Transient Key Project (TKP), a Python package which contains the
necessary routines for source finding, source associations, determination of
source characteristics, source classification transient detection and transient
classification.

Please read the documentation at the website, or generate it yourself
using Sphinx and the documentation source in the documentation folder.

You can find the online documentation at <http://docs.transientskp.org>


Installation
============

You can use CMake to build this project::

  $ mkdir -p trap/build
  $ cd trap/build
  $ cmake -DCMAKE_INSTALL_PREFIX=<prefix> ..
  $ make
  $ make install

You can also use the setup.py script, but this will not build the required
wcslib shared object.


Requirements
============

Build
-----

- GCC & GFortran <http://gcc.gnu.org/>
- CMake <http://www.cmake.org/>

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
- pyrap <http://code.google.com/p/pyrap/>
- celery <http://www.celeryproject.org/>


For storage you can choose one of the following:

- MonetDB <http://www.monetdb.org/>
- PostgreSQL <http://www.postgresql.org/>


Installation for Ubuntu
-----------------------

All packages above (except pyrap) are available in debian/ubuntu::

    $ sudo apt-get install build-essential cmake python-numpy python-scipy \
        python-dateutil python-pyfits libboost-python-dev libwcs4 wcslib-dev \
        python-tz gfortran python-pymongo python-gridfs mongodb-server

Most of the python packages are also available in pypi::

    $ pip install -r requirements.txt

To install pyrap download the source from the website and follow the
instructions in the README.

For monetdb there are ubuntu and Debian packages available. To install them
follow the instructions here: <http://dev.monetdb.org/downloads/deb/>. 


Test suite
----------

You can run the python unittests in the test subfolder to verify everything
is working for you. Set TKP_TESTPATH to overwrite the path to the test data.
