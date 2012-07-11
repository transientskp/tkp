The transients pipeline library is a set of Python modules that form the backbone of the transients pipeline: it
contains the routines used by the various steps in the pipeline.

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
---
- *dead_scripts*: A collection of various scripts that were once useful, but are currently not in use AFAIK. To be deprecated (i.e. deleted from the current repository HEAD) if no-one yells about them within the next week or two.
- *documentation*: --
- *enduser_scripts*: Some small front-end scripts that make it easy to call routines from the command line (source extraction, image conversion etc).
- *external*: --
- *standalone_db_modules*: Modules previously kept in tkp.database that clearly contain useful code, but are not integral to the workings of the transients pipeline in its current state. Likely to be reintegrated at some point, perhaps under a 'plots' or 'quality' subpackage.
- *tests*: --
- *tkp*: The main package, see details above.



