.. _steps-section:

************************
TraP logic flow overview
************************

Main logic flow
---------------

 * First, we run ``persistence``` extracts metadata from the image headers,
   and creates corresponding entries in the database.
 * Next, ```quality_check`` performs various checks on each image file,
   which may result in some being marked as 'rejected'
   (unsuitable for further processing). Subsequent recipes only act on 'good'
   images.
 * ``source_extraction.py``  Performs blind extraction and source association.
 * ``monitoringlist.py`` Performs forced fits for the user-provided
   source positions to be monitored. Associates the monitoring sources
   1-to-1 with the known monitoring sources in the runningcatalog
   (:py:func:`tkp.db.monitoringlist.associate_ms`).
 * ``transient_search.py`` First selects sources from the runningcatalog which
   satisfy the user-supplied criteria for variability indices.
   The variability indices are then used to calculate a chi-squared value for
   a test against a model of constant flux (null hypothesis).
   Finally, this chi-squared value is used to compute the probability that
   the null hypothesis is false, i.e. how likely that the source is
   intrisincally transient / variable.
 * ``feature_extraction.py`` Calculates various properties for the
   lightcurves of each identified transient source,
   e.g. mean, median, skew, peak, etc.
 * ``classification.py`` (Basically a placeholder currently).
 * ``prettyprint.py`` Prints the transients identified.



Features overview
=================

The TraP has several steps; most steps are optional, but leaving out
some will make little sense. The steps are:

- **Source extraction, database storage and source association.** This
  will detect sources in the current image, stores the sources in a
  database and associates the sources with previously detected
  sources from the same dataset.

  Note: currently, this is one step (recipe), though it may be split
  up into two steps for clarity (extraction and association are quite
  different steps).

- **Null detections.** This takes care of measuring source properties
  of undetected sources in the current image, because the source is known
  in the runningcatalog. A forced fit at this catalog position serves
  as input for association with the known catalog sources, so
  that the light curve now has upper limits at those timestamps.

- **Monitor user-added sources.** This step takes care of sources
  that were obtained from a user-specified list, such as a new X-ray
  source: the pipeline will now monitor this position so the full
  LOFAR light curve for this source can be measured.

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

A number of features are not currently implemented in the TraP logic flow, but
are under development.

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


Steps and their parameters
--------------------------

This page gives a very brief description of each script / recipe used in the
TraP workflow, and details the parameters supplied
either via command line arguments (in the case of top-level scripts) or via
parameter sets (for the recipes).


persistence
================
Checks for accessibility of each listed image file, inserts it into the database,
and stores in the MongoDB image store if configured to do so.


source_extraction
=================

Run the source finding routine. In addition, this recipe will store
the detected sources inside the database, and tries to associate the
new sources with existing ones.

- inputs:

  - image: list of (FITS) images.

  - parset: parameter set containg the following optional
    settings. Note that these setting supersede the values in your
    (local) TKP configuration file.

    - detection.threshold: peak detection threshold for a source to be
      found.

    - analysis.threshold: threshold to include neighbouring pixels
      into the determination of the source details.

    - association.radius: radius in units of the default De Ruiter
      radius to associate sources with previously extracted sources.

    - backsize.x, backsize.y: mesh size to determine the background
      level.

  - nproc: number of maximum simultaneous processors per node. Useful
    when performing source extraction on multiple subbands
    simultaneously.


- outputs:

  - dataset_id: see the dataset_id entry in the inputs.

Notes:

- In a future TraP version, the source association part may get its
  own recipe.

- A future version will allow for other images than just FITS.



.. _transient-search-recipe:

transient_search
================

Search through all matched sources and find variable sources by
looking for deviations in their light curve.

- inputs:

  - parset: parameter set, with the following parameters:

    - probability.threshold: likeliness above which the variable is
      assumed a transient (between 0 and 1).

    - probability.minpoints: minimum number of light curve data points
      to determine the variability of a source.

    - probability.eta_lim: eta (least-squared sum) limit above which
      a source is assumed to be variable (related to `threshold`
      above).

   - probability.V_lim: limit for V (measure of variation around the
     mean value) above which a source is assumed to be variable.

- outputs:

  - transient_ids: list of database IDs of the sources which are found
    to be transient.

  - siglevels: significance levels of the "transientness".

  - transients: list of ``Transient`` objects.


This routine is implemented by performing a database search, and thus
the recipe is simply run on the front-end node.

.. _feature_extraction:

feature_extraction
==================

Obtain characteristics from detected transient sources. This may fail
(ie, produces None or 0 for values) when little to no
background/steady-state information is known.

Current characteristics obtained are:

- duration

- peak flux

- increase and decrease from background to peak and back, and their
  ratio.

Each feature extraction is run as a separate node.

- inputs:

  - transients: list of ``Transient`` objects, previously obtained with the
    transient_search recipe.

  - nproc: number of maximum simultaneous processors per node.

- outputs:

  - transients: list of ``Transient`` objects.
