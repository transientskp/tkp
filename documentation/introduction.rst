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


Documentation layout
====================

The documentation is split into three parts:

**Usage**
  where you can read about what TKP is and  how you can use it.

**Overview**
  which will explain more about the design of TKP and how this is implemented.

**Developers**
  which should be used as reference for TKP developers, or if you want to reuse
  parts of TKP in an other project.



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

