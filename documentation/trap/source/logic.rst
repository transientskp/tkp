.. _logic:

************************
Trap logic flow overview
************************
.. |last_updated| last_updated::

:Last updated: |last_updated|

Main logic flow
---------------

 * First, we run :py:mod:`persistence` extracts metadata from the image headers,
   and creates corresponding entries in the database.
 * Next, :py:mod:`quality_check` performs various checks on each image file,
   which may result in some being marked as 'rejected'
   (unsuitable for further processing). Subsequent recipes only act on 'good'
   images.
 * :py:mod:`source_extraction.py`  Performs blind extraction and source association.
 * :py:mod:`monitoringlist.py` Performs a crude transient candidates search
   (:py:func:`monitoringlist.mark_sources`) to check for new locations worth
   monitoring, and then performs forced extractions
   (:py:func:`monitoringlist.update_monitoringlist`).
 * :py:mod:`transient_search.py` First selects sources from the runningcatalog which
   satisfy the user-supplied criteria for variability indices.
   The variability indices are then used to calculate a chi-squared value for
   a test against a model of constant flux (null hypothesis).
   Finally, this chi-squared value is used to compute the probability that
   the null hypothesis is false, i.e. how likely that the source is
   intrisincally transient / variable.
 * :py:mod:`feature_extraction.py` Calculates various properties for the
   lightcurves of each identified transient source,
   e.g. mean, median, skew, peak, etc.
 * :py:mod:`classification.py` (Basically a placeholder currently).
 * :py:mod:`prettyprint.py` Prints the transients identified.

