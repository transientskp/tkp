.. _job_params_cfg:

+++++++++++++++++++++++++++++++++++++++++++++++++
``job_params.cfg`` - Job Parameters Configuration
+++++++++++++++++++++++++++++++++++++++++++++++++

The job parameters file provides the detailed, scientifically-motivated
settings for each pipeline step. Providing the appropriate configuration here
is essential for achieving scientifically valid results.

The default ``job_params.cfg`` file is as follows:

.. literalinclude:: /../tkp/config/job_template/job_params.cfg

The file follows the :ref:`standard ConfigParser syntax <configparser>`.

The parameters in this file are defined as follows:

.. _job_params_persistence:

``persistence`` Section
=======================
(See also the :ref:`stage-persistence`.)

``dataset_id``
   Integer. Specifies the unique ID of a dataset to which the current pipeline
   run should be appended. If ``-1``, a new dataset is created. If you specify
   a specific data set ID the configuration of your job is retrieved from the
   database. This will override your job configuration.

``description``
   String. The name under which the database will be stored in the database.
   This value is only used if a new dataset is constructed (see
   ``dataset_id``, below).

``rms_est_sigma``
   Float. Sigma value used for iterative clipping.

``rms_est_fraction``
   Integer. Determines the size of the subsection used for RMS measurement:
   the central ``1/f`` of the image will be used (where f=rms_est_fraction).

.. _job_params_quality:

``quality_lofar`` Section
=========================
These are the quality-checking parameters applied if the ingested data is from LOFAR.
See also :ref:`stage-quality`.

``low_bound``
   Float. Reject the image if the measured RMS is less than ``low_bound``
   times the theoretical noise.
``high_bound``
   Float. Reject the image if the measured RMS is greater than ``high_bound``
   times the theoretical noise.
``oversampled_x``
    The maximum length of a beam axis.
``elliptical_x``
    The maximum ratio of major to minor axis length.
``min_separation``
    The minimum allowed distance from the image centre to a bright radio
    source in degrees.

.. _job_params_source_extraction:

``source_extraction`` Section
==============================
Parameters used in source extraction.
See also :ref:`stage-extraction` and :ref:`stage-forcedfit`.

``detection_threshold``
   Float. The detection threshold as a multiple of the RMS noise.

``analysis_threshold``
   Float. The analysis threshold as a multiple of the RMS noise.

``back_size_x``, ``back_size_y``
   Integers. The size of the background grid parallel to the X and Y axes of
   the pixel grid.

``margin``
   Integer. Pixel data within ``margin`` pixels of the edge of the image will
   be excluded from the analysis.

``extraction_radius_pix``
   Integer. Pixel data more than ``extraction_radius_pix`` pixels from the
   centre of the image will be excluded from the analysis.

``deblend_nthresh``
   Integer. The number of subthresholds to use for deblending. Set to ``0`` to
   disable deblending.

``force_beam``
   Boolean. If ``True``, all detected sources are assumed to have the size and
   shape of the restoring beam (ie, to be unresolved point sources), and these
   parameters are held constant during fitting. If ``False``, all parameters
   are allowed to vary freely.

``box_in_beampix``
    The size of the masking aperture which determines which pixels are used
    for forced fitting, as a multiple of the beam major axis length.
    See :py:func:`tkp.sourcefinder.image.ImageData.fit_to_point` for details.

``ew_sys_err``, ``ns_sys_err``
   Floats. Systematic errors in units of arcseconds which augment the
   sourcefinder-measured errors on source positions when performing source
   association. These variables refer to an absolute angular error along an
   east-west and north-south axis respectively. (NB Although these values
   are *stored* during the source-extraction process, they affect the
   source-association process.)

`expiration`
    The number of forced fits performed since the last blind fit. Used to
    'expire' the runningcatalog - else said to stop monitoring a source of
    which the flux went below the detection threshold after a configurable
    amount of timesteps.


.. _job_params_association:

``association`` Section
==============================
Parameters used in source-association. See :ref:`stage-association` for details.
NB the ``ew_sys_err``, ``ns_sys_err`` parameters detailed above also affect
source-association.

``deruiter_radius``
   Float. Maximum DeRuiter radius for two sources to be considered candidates
   for association.

``beamwidths_limit``
   Float. Maximum separation for two sources to be considered candidates for
   association, as a multiple of the restoring-beam semimajor-axis length.
   Default is 1.0, which was the fixed default prior to TraP release 2.1.
   It may be necessary to use a larger number if your data has large
   systematic position errors, i.e. if the sources 'jitter' between images,
   but note that using a large value can cause slowdown of database operations.

.. _job_params_transient_search:

``transient_search`` Section
==============================
Parameters used in transient-detection. See also the
:ref:`stage-transient`.

``new_source_sigma_margin``
    Float. A newly detected source is considered transient if it is
    significantly above the best (lowest) previous detection limit for that
    point on-sky. 'Significantly above' is defined by a 'margin of error,'
    intended to screen out steady sources that just happen to be fluctuating
    around the detection threshold due to measurement noise.
    This value sets that margin as a multiple of the RMS of the previous-best
    image.
