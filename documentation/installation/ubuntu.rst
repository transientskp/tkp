.. _ubuntu:

======
Ubuntu
======

casacore
--------

install requirements::

   $ sudo apt-get install subversion cmake build-essential flex bison gfortran \
        libblas-dev liblapack-dev libcfitsio3-dev wcslib-dev libfftw3-dev \
        libhdf5-dev libreadline-dev libncurses5-dev

get the casa data::

   $ cd ~
   $ wget ftp://ftp.atnf.csiro.au/pub/software/measures_data/measures_data.tar.bz2
   $ sudo mkdir /usr/local/share/casacore && cd /usr/local/share/casacore
   $ sudo tar jxvf ~/measures_data.tar.bz2


install casacore::

   $ svn checkout http://casacore.googlecode.com/svn/trunk/ casacore
   $ mkdir casacore/build && cd casacore/build
   $ cmake .. -DDATA_DIR=/usr/local/share/casacore/data -DUSE_FFTW3=ON \
         -DUSE_HDF5=ON -DUSE_OPENMP=ON



pyrap
-----

install da shizzle::
   $ cd ~
   $ svn checkout http://pyrap.googlecode.com/svn/trunk/ pyrap
   $ cd pyrap


TKP
---

   $ sudo apt-get install git
