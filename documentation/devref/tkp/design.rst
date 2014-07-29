++++++
Design
++++++

The transients pipeline library is a set of Python modules that form
the backbone of the transients pipeline: it contains the routines used
by the various steps in the pipeline. All routines are written in
Python, with a few exceptions as detailed below.

The modules are separated into four subpackages:

- database: the routines that interface with the database. The modules
  in this subpackage contain the necessary SQL queries to match
  sources and find transients, as well as more general functions and a
  few classes.

- sourcefinder: the modules in this subpackage handle the detection of
  sources in an (2D) image.

- classification: the modules in this subpackage deal with the
  classification of detected sources, mainly through the source light
  curves (and possibly their spectra). It also contains functions to
  extract the required characteristics of the light curves for
  classification.

- utility: this subpackage contains a variety of utility functions,
  such as (image) data file handlers and coordinate functions.

At the root of the package, there is also the :mod:`config` module,
which deals with the setup and configuration of the various modules in
the library.

For practical usage, start with reading through the transient pipeline
documentation instead. For details on the various TKP modules and
functions, see the rest of this documentation: most of the modules and
functions have doc strings that should explain a good deal about the
details. In the end, of course, the real details are obtained by
"reading the source".
