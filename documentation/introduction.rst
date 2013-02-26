.. _introduction:

++++++++++++
Introduction
++++++++++++

This is the Transient Key Project (TKP), a Python package which contains the
necessary routines for source finding, source associations, determination of
source characteristics, source classification transient detection and transient
classification.

Philosophy
==========

The idea is that the TKP library is installed on a system. The end user can
then use the supplied script(s) to setup, configure and maintain a pipeline
environment. A pipeline environment is a folder somewhere in the end user's
folder containing a configuration and a set of one or more jobs.

Configuration
=============

Per-user settings may be defined by in the file .tkp.cfg in your home
directory. This file follows the standard Python ConfigParser syntax.

You will need to configure a database unless you can rely upon the default.

    [database]
    enabled = True
    host = ldb001
    name = tkp
    user = tkp
    password = tkp
    port = 50000

A default configuration file may be generated as follows::

  import tkp.config
  tkp.config.write_config()


Note that this will overwrite any existing configuration file: use with care!

.. Warning::

  We are working on moving all tkp.config settings to configuration and parset
  files inside a pipeline project folder, this will be removed in the future.


TKP library Details
===================
The transients pipeline library is a set of Python modules that form the
backbone of the transients pipeline: it contains the routines used by the
various steps in the pipeline.

The modules are separated into four subpackages:

**database**
 the routines that interface with the database. The modules in this subpackage
 contain the necessary SQL queries to
 match sources and find transients, as well as more general functions and a few
 classes.

**sourcefinder**
 the modules in this subpackage handle the detection of sources in an (2D) image.

**classification**
 the modules in this subpackage deal with the classification of detected
 sources, mainly through the source light curves (and possibly their spectra).
 It also contains functions to extract therequired characteristics of the light
 curves for classification.

**utility**
 this subpackage contains a variety of utility functions, such as (image) data
 file handlers and coordinate functions.

