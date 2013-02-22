Introduction
============

This is the Transient Key Project (TKP), a Python package which contains the
necessary routines for source finding, source associations, determination of
source characteristics and source classification.

Please read the documentation at the website, or generate it yourself
using Sphinx and the documentation source in the documentation folder.

You can find the online documentation at::

 http://docs.transientskp.org/


Installation
============

You can use CMake to build this project::

 $ mkdir build && cd build && cmake ..

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

For running the TRAP you need to in stall the Lofar System software.


Installation for Ubuntu
-----------------------

All packages above (except pyrap and pygsl) are available in debian/ubuntu
and pypi::

    $ sudo apt-get install build-essential cmake python-numpy python-scipy \
        python-dateutil python-pyfits libboost-python-dev libwcs4 wcslib-dev \
        python-tz gfortran python-pymongo python-gridfs mongodb-server

To install pyrap and pygsl download the source from the website and follow the
instructions in the README.

TKP uses MonetDB for storing all data. If you want to run a MonetDB server
follow the instructions described here: http://dev.monetdb.org/downloads/deb/



