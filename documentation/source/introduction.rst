Transients Pipeline
===================

This document describes the transients pipeline: it's usage,
configuration and setup.

The transients pipeline (TRAP), or more accurately, the transients
detection and classification pipeline, is a software pipeline that
accepts LOFAR imaging data (images or UV data) and tries to find
variable and new sources in those data.

The TRAP makes use the Transients Key Project (TKP) library, a Python
package which contains the necessary routines for source finding,
source associations, determination of source characteristics and
source classification. These are described in the :ref:`TKP library
documentation <tkpapi:index>`.


The TRAP has several steps; most steps are optional, but leaving out
some will make little sense. The steps are:

- An imaging step. This actually belongs to the standard
  imaging pipeline (SIP), but can be implemented into the TRAP for
  convenience (so to have an end-to-end pipeline).

- A time slicing routine. This can be used when a long observation
  (dataset) needs to split into smaller (shorter) chunks, which are
  then compared among each other to find transients within the dataset
  (ie, not by comparing with existing catalogs).

  The two routines above are not used when the input to the TRAP
  consists of a list of individual images. In this case the TRAP will
  just loop over this list of images.


- Source extraction, database storage and source association. This
  will detect sources in the current image, stores the sources in a
  database and associates the sources with 1) previously detected
  sources from the same dataset and 2) existing catalogs.

  Note: currently, this is one step (recipe), though it may be split
  up into two steps for clarity (extraction and association are quite
  different steps).

- Transient detection. All existing light curves (ie, associated
  sources from the previous step) will be examined to determine if
  sources are variable. (The basic algorithm for this is a chi-squared
  calculation and check for significant deviations from the average.)

  Not implemented yet, but in a future version: sources will be
  compared to cataloged sources, to determine if their flux level
  differs from their cataloged value.

- Feature extraction. This will attempt to extract various
  characteristics (peak flux, duration, flux increase and decrease,
  spectral shape) from any transient detected in the previous routine. 

  Since most algorithms in the above routine rely on a good
  measurement of the average background/steady-state value, these
  algorithms may not return any (usable) values when only few
  measurements are available.

- Source classification. This routine will attempt to classify a
  source. Multiple classifications are possible, each with its own
  weight (a threshold can be set to only output classifications above
  a certain weight).

  This routine is very dependent on the results of the feature
  extraction routine. Ie, badly or no extracted features will
  obviously not lead to a (valid) classification. 
