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

Don't forget that you need to populate a database also. see the database
subdirectory for details.

You can also use the setup.py script, but this will not build the required
wcslib shared object.


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
- pyrap <http://code.google.com/p/pyrap/>
- pygsl <http://pygsl.sourceforge.net/>
- MonetDB <http://www.monetdb.org/>


For running the TKP pipeline you need to in stall the Lofar User Software:

- LUS <http://lus.lofar.org/documentation/pipeline/>


Installation for Ubuntu
-----------------------

All packages above (except pyrap and pygsl) are available in debian/ubuntu::

    $ sudo apt-get install build-essential cmake python-numpy python-scipy \
        python-dateutil python-pyfits libboost-python-dev libwcs4 wcslib-dev \
        python-tz gfortran python-pymongo python-gridfs mongodb-server

Most of the python packages are also available in pypi.

To install pyrap and pygsl download the source from the website and follow the
instructions in the README.

There are ubuntu and Debian packages available. To install them follow the
instructions here: <http://dev.monetdb.org/downloads/deb/>. Don't forget
the monetdb-python package.



