+++++++++++++
Library & API
+++++++++++++

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


.. toctree::
   :maxdepth: 2

   design
   config
   steps
   accessors
   database/index
   sourcefinder/index
   utility/index
   classification/index
   conf/index
   distribute/index
   lofar/index
   quality/index
   alerts
   monitoringlist
   testutil
