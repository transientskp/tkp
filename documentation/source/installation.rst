.. _installation:

######################
Installation
######################
.. |last_updated| last_updated::

:last updated: |last_updated|

This page documents only how to install the Trap recipes. In order to run the
pipeline, you will also need to have installed the relevant dependencies (see
below) and have access to an appropriately configured :ref:`database
<database-section>`.

Dependencies
===============================

Installation of the Trap requires that the :ref:`TKP library
<tkpapi:introduction>` and all of its dependencies be available. Please refer
to its documentation for details.

In addition, the Trap requires:

+ `pyrap <https://code.google.com/p/pyrap/>`_.

+ `The LOFAR pipeline framework <http://lus.lofar.org/documentation/pipeline/>`_.

  Since the pipeline framework and the occasional part of the
  transients pipeline use parsets, you will also need to install the
  parset libraries from the LOFAR software. If you plan to use the
  imaging pipeline as well, you're probably best off installing all of
  the LOFAR imaging software (the LofIm package).

+ `MonetDB <http://www.monetdb.org>`_, including its Python module

  Always use the most recent version of MonetDB available.

+ The Gnu Scientific Library, and the Python module `pygsql`.

  This is used by the classification module in the TKP library.

Obtaining and installing the code
==================================

The Trap code is stored in our `GitHub repository
<http://www.github.com/transientskp/trap>`_. The code is currently only
accessible to project members.

Clone the latest version of the repository as follows::

  $ git clone git@github.com:transientskp/trap.git

Installation can be most conveniently performed using `CMake
<http://www.cmake.org/>`_. Simply::

  $ mkdir -p trap/build
  $ cd trap/build
  $ cmake -DCMAKE_INSTALL_PREFIX=<prefix> ..
  $ make && make install

Substituting ``<prefix>`` with the root of the directory structure into which
you wish to install.
