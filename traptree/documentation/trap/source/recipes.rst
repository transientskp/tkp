.. _recipes-section:

##############################
recipes and their parameters
##############################

.. |last_updated| last_updated::

:Last updated: |last_updated|

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

- In a future TRAP version, the source association part may get its
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

  - transients: list of :ref:`Transient
    <tkpapi:classification-transient-transient>` objects.


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

  - transients: list of :ref:`Transient
    <tkpapi:classification-transient-transient>` objects,
    previously obtained with the transient_search recipe.

  - nproc: number of maximum simultaneous processors per node.

- outputs:

  - transients: list of :ref:`Transient
    <tkpapi:classification-transient-transient>` objects.
