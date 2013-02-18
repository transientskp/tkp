############################
The Transients Pipeline
############################
.. |last_updated| last_updated::

:Last updated: |last_updated|

This document describes the transients pipeline, its :ref:`installation <installation>`,
configuration, and usage.

The transients pipeline (TraP), or more accurately, the transients
detection and classification pipeline, is a software pipeline that
accepts LOFAR imaging data (images, or possibly UV data), tries to
find variable or new sources in those data, and extracts information
about those sources in an attempt to classify these sources, all fully
automated.

The TraP makes use the Transients Key Project (TKP) library, a Python
package which contains the necessary routines for source finding,
source associations, determination of source characteristics and
source classification. These are described in the :ref:`TKP library
documentation <tkpapi:front>`. The pipeline itself (the framework) is
the `LOFAR pipeline system
<http://lus.lofar.org/documentation/pipeline/>`_.


The rest of this page gives a quick overview of the current functionality provided by the Trap.
A separate page details :ref:`the exact logic flow <logic>`.

Features overview
=======================

The TraP has several steps; most steps are optional, but leaving out
some will make little sense. The steps are:

- **Source extraction, database storage and source association.** This
  will detect sources in the current image, stores the sources in a
  database and associates the sources with 1) previously detected
  sources from the same dataset and 2) existing catalogs.

  Note: currently, this is one step (recipe), though it may be split
  up into two steps for clarity (extraction and association are quite
  different steps).

- **Monitor existing or user-added sources.** This takes care of measuring fluxes
  of transient sources, even when these have disappeared below the detection
  threshold, so that the light curve is measured with upper limits instead.
  This step also takes care of sources that were obtained from elsewhere and
  manually added, such as a new X-ray source: the pipeline will now monitor
  this position so the full LOFAR light curve for this source can be measured.

- **Transient detection.** All existing light curves (ie, associated sources from
  the previous step) will be examined to determine if sources are variable.
  (The basic algorithm for this is a chi-squared calculation and check for
  significant deviations from the average.)

  Not implemented yet, but in a future version: sources will be
  compared to sources in the LOFAR global sky model, to determine if their flux
  level differs from their cataloged value.

- **Feature extraction.** This will attempt to extract various
  characteristics (peak flux, duration, background level, flux
  increase and decrease, spectral shape, standard statistical values
  such as mean, standard deviation, skew and kurtosis) from any
  transient detected in the previous routine.

  Since most algorithms in the above routine rely on a good
  measurement of the average background/steady-state value, these
  algorithms may not return any (usable) values when only few
  measurements are available.

Coming soon
-------------

A number of features are not currently implemented in the Trap logic flow, but are under development.

- **Source classification.** This routine will attempt to classify a
  source. Multiple classifications are possible, each with its own
  weight (a threshold can be set to only output classifications above
  a certain weight).

  This routine is obviously very dependent on the results of the feature
  extraction routine. Ie, badly or no extracted features will
  obviously not lead to a (valid) classification. 

  Since, at the moment, there are few to none training data sets for
  the classification, this step follows a simple manual tree
  classification, where each source gets a value (weight) associated
  with a certain type of classification. The possible classifications,
  however, are fully preprogrammed.

- An **alert system.** This will send emails to interested parties, depending on
  criteria set beforehand (which are compared to the results found in the
  classification step). In the future, this step should be replaced by sending
  out VOEvents, and the current implementation is essentially a simple way of
  alerting people to possible transients detected by the pipeline.

- An **imaging** step. This actually belongs to the standard
  imaging pipeline (SIP), but can be implemented into the TraP for
  convenience (so to have an end-to-end pipeline).
  `Currently out of commission, awaiting upstream updates to the LOFAR pipeline.`

- A **time slicing** routine. This can be used when a long observation
  (dataset) needs to split into smaller (shorter) chunks, which are
  then compared among each other to find transients within the dataset
  (ie, not by comparing with existing catalogs).

  The two routines above are not used when the input to the TraP
  consists of a list of individual images. In this case the TraP will
  just loop over this list of images.

