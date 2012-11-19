.. _logic:

****************************
Trap logic flow overview
****************************

.. |last_updated| last_updated::
:Last updated: |last_updated|


Main logic flow
----------------

.. To do: update documentation for each recipe, link to them here...

For :py:data:`image` in :py:data:`input_list`, run:
 * :py:mod:`source_extraction.py`  (includes per-image-association)
 * :py:mod:`monitoringlist.py` (includes first search for transient candidates)
 * :py:mod:`transient_search.py` (lightcurve variability analysis) 
 * :py:mod:`feature_extraction.py` (Attempt to characterise our transients)
 * :py:mod:`classification.py` (Basically a placeholder currently).
 * :py:mod:`prettyprint.py`

