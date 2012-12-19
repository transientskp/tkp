.. _database_schema:

++++++
Schema
++++++

.. image:: schema.png

assoccatsource
==============

This table stores the association between an extracted source and one or more
cataloged sources (i.e. VLSS, WENSSm, WENSSp, and NVSS sources).

For every association pair the association parameters, distance_arcsec, r and
loglr are calculated as well. Only source pairs that fullfil the criterion of
an association (:math:`r < r_{lim}`) are accepted and appended to this table.
:math:`r_{lim}` may be specified in the user parsets or tkp.cfg, otherwise it
defaults to 3.717, corresponding to missing :math:`10^{-3}` counterparts (see
`Scheers's thesis <http://dare.uva.nl/en/record/367374>`_, section 3.2.3)


**xrtsrc**
   This refers to the xtrsrcid of the extractedsource

**catsrc**
   This is the id of the catalogedsource that could be associated to the
   extractedsource as its counterpart

**type**
   Type of the association, determined by the association procedure inside the
   database. See under assocxtrsource for types and their descriptions

**distance_arcsec**
   The distance in arcsec between the associated sources, calculated by the
   database using the dot product and Cartesian coordinates

**r**
   The dimensionless distance (De Ruiter radius) between the associated
   sources. It is determined as the positional differences weighted by the
   errors, calculated by the association procedure inside the database (Scheers
   thesis ch3).

**loglr**
   The logarithm of the likelihood ratio of the associated sources, defaults to
   NULL if not calculated (Scheers thesis ch3).


assocxtrsource
==============

This table stores the association between an extracted source and its
runningcatalog counterpart source, where the relation might be of type 1-1, 1-n
or n-1.

*runcat**
   refers to the runcatid in runningcatalog.  It is considered as the "base" id
   of a lightcurve, whereas the lightcurve consist of multiple frequency bands
   and Stokes parameters.

**xtrsrc**
   This is the id of the extracted source that could be associated to
   runningcatalog source.  Together, the runcat_id and the xtrsrc form a unique
   pair.

**type**
    Type of association, and its description.  n-m, where n is the number of
    runningcatalog sources, and m the number of extractedsources.
    Type 1: 1-1 association; type 2: 1-n (one-to-many) association; type 3:
    n-1, many-to-one association; type 4: n-m (many-to-many) association; type
    5: 0-1 (zero-to-one) association, a new source.

**distance_arcsec**
   The distance in arcsec between the associated sources, calculated by the
   database using the dot product Cartesian coordinates

**r**
   The dimensionless distance (De Ruiter radius) between the associated
   sources. It is determined as the positional differences weighted by the
   errors, calculated by the association procedure inside the database (Scheers
   thesis chapter 3).

**loglr**
   The logarithm of the likelihood ratio of the associated sources, defaults to
   NULL if not calculated (Scheers thesis ch3).


catalogedsource
===============

This table contains the sources from renown surveys/catalogues, VLSS, WENSS
and NVSS. The original data (all columns) are downloaded from the CDS Vizier
websites (`VLSS <http://cdsarc.u-strasbg.fr/viz-bin/VizieR?-source=VIII/79>`_,
`WENSS <http://cdsarc.u-strasbg.fr/viz-bin/VizieR?-source=VIII/62>`_ and `NVSS
<http://cdsarc.u-strasbg.fr/viz-bin/VizieR?-source=VIII/65>`_) The catalogues
also contains the exoplanets, of which the entries were provided by
Jean-Mathias Griessmeier.

This table will be pre-loaded in the database, in order to have it available
all the time. As opposed to the runningcatalog, the catalogedsources table is
static and fixed and won't change during runs.


**id**
    Every inserted catalog source gets a unique id, generated sequentially by
    the database.

**catalog**
    The reference id to the catalog from which this source originates from.

**orig_catsrcid**
    The original id of the source as reported in the catalog

**catsrcname**
    The original name of the source as reported in the catalog

**tau**
    The integration time. Defaults to NULL.

**band**
    The reference id to the frequencyband at which this survey was carried out.

**stokes**
    The Stokes parameter. Four possible values 1 - I, 2 - Q, 3 - U, 4 - V.
    (Currently the external catalogues only report the Stokes I values).

**freq_eff**
    The effective frequency (in Hz) of the survey, as reported in the catalog

**zone**
    The zone id in which the source declination resides, calculated by the
    database.  The sphere is devided into zones of equal width: currently
    fixed to 1 degree, and the zone is effectively the truncated declination.
    (``decl`` = 31.3 → ``zone`` = 31, ``decl`` = 31.9 → ``zone`` = 31). This
    column is primarly for speeding up source look-up queries.

**ra**
    The right ascension (RA) of the source in J2000 degrees.

**decl**
    The declination (decl) of the source in J2000 degrees.

**ra_err**
    The 1-sigma error of the source in RA as measured on the sky, in arcsec.

**decl_err**
    The 1-sigma error of the source in decl as measured on the sky, in arcsec.

**x**
    The x-Cartesian coordinate of the source, generated by the database from
    ``ra``, ``decl``: :math:`\cos(decl) * \cos(ra)`.

**y**
    The y-Cartesian coordinate of the source, generated by the database from
    ``ra``, ``decl``: :math:`\cos(decl) * \sin(ra)`.

**z**
    The z-Cartesian coordinate of the source, generated by the database from
    ``ra``, ``decl``: :math:`\sin(decl)`.

**margin**
    Not used, defaults to 0.

**det_sigma**
    The detection level of the source, which none of the current catalogs
    provides, and defaults to 0.

**src_type**
    Only the WENSS catalog reports the source type: M for a multi-component
    source, C for a subcomponent of the parent M, S for a single source and E
    for an extended source. Currently, we associate extracted sources with all
    source types.

**fit_probl**
    WENSS and NVSS report occasional fit problems.

**PA**
    Position angle of fitted major axis, in degrees

**PA_err**
    Error on position angle of fitted major axis, in degrees

**major**
    Major axis of deconvolved component size, in arcsec

**major_err**
    Mean error on major axis, in arcsec

**minor**
    Minor axis of deconvolved component size, in arcsec

**minor_err**
    Mean error on minor axis, in arcsec

**avg_f_peak**
    Peak flux (in Jy) of source. It is prefixed by avg, since its value is
    based on a number of observations, as will also be the case when we add
    LOFAR surveys (MSSS) to this table.

**avg_f_peak_err**
    Mean error on peak flux of source, in Jy

**avg_f_int**
    Integrated flux of source, in Jy

**avg_f_int_err**
    Mean error on integrated flux of source, in Jy

**frame**
    Some catalogs have a reference to a frame/fits image/jpg postage stamp for
    the field the source was detected in.


catalog
=======

This table stores the information about the catalogs that are loaded into the
pipeline database.


**id**
    Every catalog gets a unique id, generated sequentually by the database.

**name**
    An acronym under which the catalog is well-known, e.g. 'NVSS'

**fullname**
    The (nearly) full name under which the catalog is known, e.g. 'NRAO VLA
    Sky Survey'


classification
==============

This table contains classification of transients


dataset
=======

This table contains the information about a dataset. A dataset is nothing more
than a collection of images grouped together for processing. When the same
group is reprocessed, and the dataset.inname is identical (e.g. when the
processing runs with other trap parameters), the rerun is incremented by 1, but
the id is auto-incremented as well, treating it as an independent dataset.


**id**
    Every dataset gets a unique id. The id is generated by the database.

**rerun**
    The value indicates how many times a dataset with a given description was
    processed by the pipeline. Note that every dataset still has a unique id,
    even when it was reprocessed.
    At insertion time, by the insertDataset() SQL function, this is incremented
    by 1 when the description of the dataset is already present in the table,
    otherwise defaults to 0.

**type**
    Not being used.

**process_ts**
    The timestamp of the start of processing the dataset, generated by the
    database.

**detection_threshold**
    The detection threshold that was used by source finder to extract sources.
    Value read from either the source finder parset file or the tkp.cfg file.
    See the :ref:`PySE documentation <pyse>` for more information.

**analysis_threshold**
    The analysis threshold that was used by source finder to extract sources.
    Value read from either the source finder parset file or the tkp.cfg file.
    See the :ref:`PySE documentation <pyse>` for more information.

**assoc_radius**
    The association radius that is being used for associating sources. Value
    read from either the source finder parset file or the tkp.cfg file.

**backsize_x**
    Background grid segment size in x. Value read from either the source finder
    parset file or the tkp.cfg file. See the :ref:`PySE documentation <pyse>`
    for more information.

**backsize_y**
    Background grid segment size in y. Value read from either the source finder
    parset file or the tkp.cfg file. See the :ref:`PySE documentation <pyse>`
    for more information.

**margin_width**
    Margin applied to each edge of image (in pixels). Value read from either
    the source finder parset file or the tkp.cfg file. See the :ref:`PySE
    documentation <pyse>` for more information.

**description**
    A description of the dataset, with a maximum of 100 characters.

**node(s)**
    Determine the current and number of nodes in case of a sharded database
    set-up.

extractedsource
===============

This table contains all the extracted sources (measurements) of an image.
Maybe source is not the right description, because measurements may be made
that were erronous and do not represent a source.

Most values come from the sourcefinder procedures, and some are auxiliary
deduced values generated by the database.

This table is empty BEFORE an observation. DURING an observation new sources
are inserted into this table AFTER an observation this table is dumped and
transported to the catalog database.

All detections (measurements) found by sourcefinder are appended to this table.
At insertion time some additional auxiliary parameters are calculated by the
database as well. At anytime, no entries will be deleted or updated.
The TraP may add forced-fit entries to this table as well. Then
``extract_type`` is set to 1.

**id**
    Every inserted source/measurement gets a unique id, generated by the
    database.

**image**
    The reference id to the image from which this sources was extracted.

**zone**
    The zone id in which the source declination resides, calculated by the
    database.  The sphere is devided into zones of equal width: currently fixed
    to 1 degree, and the zone is effectively the truncated declination.
    (decl=31.3 => zone=31, decl=31.9 => zone=31). This column is primarly for
    speeding up source look-up queries.

**ra**
    Right ascension of the measurement [in J2000 degrees], calculated by the
    sourcefinder procedures.

**decl**
    Declination of the measurement [in J2000 degrees], calculated by the
    sourcefinder procedures.

**ra_err**
    The 1-sigma error on ra, the square root of the quadratic sum of the
    gaussian fit and systematic errors, calculated by the database at insertion time.

**decl_err**
    The 1-sigma error on declination, the square root of the quadratic sum of the
    gaussian fit and systematic errors, calculated by the database at insertion time.

**ra_fit_err**
    The 1-sigma error from the source fitting for ra [in arcsec], calculated by the
    sourcefinder procedures. NOTE: the db unit is in arcsec, while the
    sourcefinder produces degrees, so be careful with convertions.

**decl_fit_err**
    The 1-sigma error from the source fitting for declination [in arcsec],
    calculated by the sourcefinder procedures. NOTE: the db unit is in arcsec,
    while the sourcefinder produces degrees, so be careful with convertions.

**ra_sys_err**
    The systematic error on ra, as determined after source finder testing
    by Dario Carbone and reported at 2012-12-04 `TKP Meeting
    <https://speakerdeck.com/transientskp/source-finder-testing-overview-and-status>`_,
    to be set at 20 arcsec.

**decl_sys_err**
    The systematic error on decl, as determined after source finder testing
    by Dario Carbone and reported at 2012-12-04 `TKP Meeting
    <https://speakerdeck.com/transientskp/source-finder-testing-overview-and-status>`_,
    to be set at 20 arcsec.

**x, y, z**
    Cartesian coordinate representation of (ra,decl), calculated by the
    database at insertion time.

**racosdecl**
    The product of ra and cosine of the declination. Helpful in source look-up
    association queries where we use the De Ruiter radius as an association
    parameter.

**margin**
    Used for association procedures to take into account sources that lie close
    to ra=0 & ra=360 meridian.
    * True: source is close to ra=0 meridian
    * False: source is far away enough from the ra=0 meridian
    * NOTE & TODO: This is not implemented yet.

**det_sigma**
    The sigma level of the detection (Hanno's thesis): 20*(f_peak/det_sigma)
    gives the rms of the detection. Calculated by the sourcefinder procedures.

**semimajor**
    Semi-major axis that was used for gauss fitting [in arcsec], calculated by
    the sourcefinder procedures.

**semiminor**
    Semi-minor axis that was used for gauss fitting [in arcsec], calculated by
    the sourcefinder procedures.

**pa**
    Position Angle that was used for gauss fitting [from north through local
    east, in degrees], calculated by the sourcefinder procedures.

**f_peak**
    peak flux [Jy], calculated by the sourcefinder procedures.

**f_peak_err**
    1-sigma error (in Jy) of ``f_peak``, calculated by the sourcefinder
    procedures.

**f_int**
    integrated flux [Jy], calculated by the sourcefinder procedures.

**f_int_err**
    1-sigma error (in Jy) of ``f_int``, calculated by the sourcefinder
    procedures.

**extract_type**
    Reports how the source was extracted by sourcefinder (Hanno's thesis),
    generated by the sourcefinder procedures. Currently implemented values
    are:

        * ``NULL``: gaussian fit
        * ``NULL``: moments fit
        * ``1``: forced fit to pixel

**node(s)**
    Determine the current and number of nodes in case of a sharded database
    set-up.


frequencyband
=============

This table contains the frequency bands that are being used inside the
database. 
Here we adopt the set of pre-defined Standard LOFAR Frequency Bands and their
bandwidths as defined for `MSSS
<http://www.lofar.org/wiki/doku.php?id=msss:documentation#standard_msss-lba_frequency_bands>`_. 
Included are frequency bands outside the LOFAR bands, in order to match the
external catalogue frequency bands.
When an image is taken at an unknown band, it is added to this table by the SQL
function ``getBand()``, using the image's effective frequency as central
frequency and its bandwidth to determine the low and high end of the band.

**id**
    Every frequency band has its unique id, generated by the database.

**freq_central**
    The central frequency of the defined frequency band. (Note that this is not
    the effective frequency, which is stored as a property in the image table.)

**freq_low**
    The low end of the frequency band.

**freq_high**
    The high end of the frequency band.



image
=====

This table contains the images that are being or were processed in the TraP. 
Note that the format of the image is not stored as an image property. 
An image might be a composite of multiple images, but it is not yet defined how
the
individual values for effective frequency, integration times, etc are
propagated to 
the columns of the ``image`` table.
`The CASA Image description for LOFAR
<http://www.lofar.org/operations/lib/exe/fetch.php?media=public:documents:casa_image_for_lofar_0.03.00.pdf>`_
describes the structure of a LOFAR CASA Image, 
from which most of the data of the ``image`` table originates from. 

An image is characterised by

* observation timestamp (taustart_ts).
* integration time (tau)
* frequency band (band) 
* Stokes parameter (stokes)

A group of images that belong together (defined by user, but not specified any
further) are in the same data set (i.e. they have the same reference to
dataset).

**id**
    Every image gets a unique id, generated by the database.

**dataset**
    The dataset to which the image belongs to. 

**tau** 
    The integration time of the image. This is a quick reference number related
    to tau_time, similar as to which band is related to central frequency.
    Currently this is not used.

**band** 
    The frequency band at which the observation was carried out. Its value
    refers to the id in frequencyband, where the frequency bands are
    predefined. The image's effective frequency falls within this band. If an
    image has observation frequency that is not in this table, a new entry will
    be created based an the effective

**stokes** 
    The Stokes parameter of the observation. 1 = I, 2 = Q, 3 = U and 4 = V. 
    The Stokes parameter originates or is read from the CASA Main table in the
    coords subsection from the ``stokesX`` record. 
    The char value is converted by the database to one of the four (tiny)
    integers.

**tau_time** 
    The integration time (in seconds) of the image. 
    The value originates or is read from the CASA LOFAR_OBSERVATION table 
    by differencing the ``OBSERVATION_END`` and ``OBSERVATION_START`` data
    fields. 

**freq_eff** 
    The effective frequency (or synonymously rest frequency) (in Hz) at 
    which the observation was carried out. 
    The value originates or is read from the CASA Main table in the coords
    subsection from the ``spectralX`` record and the ``crval`` field. 
    Note that in the case of FITS files the header keywords representing the
    effective frequency are not uniquely defined and may differ per FITS file. 

**freq_bw** 
    The frequency bandwidth (in Hz) of the observation. 
    Value originates or is read from the CASA Main table in the coords
    subsection from the ``spectralX`` record and the ``cdelt`` field. N
    This is a required value and when it is not available an error is thrown.

**taustart_ts** 
    The timestamp of the start of the observation, originating or read from 
    the CASA LOFAR_OBSERVATION table from the ``OBSERVATION_START`` data field.

**centre_ra** and **centre_decl**
    The central coordinates (J2000) (or pointing centre) of the image in
    degrees. 
    RA and dec values originate or are read from the CASA Main table in the
    coords subsection from the ``pointingcenter`` record. 
    Note the conversion from radians to degrees.

**x**, **y** and **z**
    The Cartesian coordinates of centre_ra and centre_decl. 
    Values are calculated by the database from centre_ra and centre_decl. Not
    yet stored in table.

**rb_maj** 
    The major axis of the restoring beam, in arcsec. 
    Value originates or is read from the CASA Main table in the imageinfor
    subsection from the ``restoringbeam`` record. 

**rb_min** 
    The minor axis of the restoring beam, in arcsec. 
    Value originates or is read from the CASA Main table in the imageinfor
    subsection from the ``restoringbeam`` record. 

**rb_pa** 
    The position angle of the restoring beam (from north to east to the major
    axis), in degrees. 
    Value originates or is read from the CASA Main table in the imageinfor
    subsection from the ``restoringbeam`` record. 

**fwhm_arcsec**
    The full width half maximum of the primary beam, in arcsec. Value not yet
    stored in table.

**fov_degrees**
    The field of view of the image, in square degrees. Not yet stored in table.

**url** 
    The url of the physical location of the image at the time of processing.
    NOTE that this needs to be updated when the image is moved.

**node(s)** 
    Determine the current and number of nodes in case of a sharded database
    set-up.


monitoringlist
==============

This table contains the list of sources that are monitored. This implies that
the source finder software will measure the flux in an image at exactly the
given position. 

These positions are 0 by default, since they can be retrieved by joining with
the runningcatalog.

For user defined sources, however, positions may be available that are more
precise than those in the runningcatalog. 
Hence the ra and decl columns are still necessary for these sources.  
The runcat refers to the id in the runningcatalog, when available. 
Eg, manually inserted sources with positions obtained differently will not have 
a runcat to start with (in which case runcat will have the NULL value), 
until the first time the flux has been measured; 
then these sources (even when actual upper limits) will be inserted into
extractedsources and runningcatalog, and have a runcat.  
They will still have userentry set to true, so that the position used is that 
in this table (the more precise position), not that of the runningcatalog.

**id**
    Every source in the monitoringlist gets a unique id

**runcat**
    Refers to the id in runningcatalog.  

**ra**
    The Right Ascension (J2000) of the source

**decl** 
    The Declination (J2000) of the source

**dataset**
    Refers to the id in dataset, to which this monitoringlist belongs to.

**userentry** 
    Boolean to state whether it is an user inserted soure (true) or by the trap
    (false)


node
====

This table keeps track of zones (declinations) of the stored sources on the
nodes in a sharded database configuration. Every node in such a set-up will
have this table, but with different content.

**node**
    The id of the node

**zone**
    The zone that is available on the node

**zone_min**
    The minimum zone of the zones

**zone_max**
    The maximum zone of the zones

**zone_min_incl**
    Boolean determining whether the minimum zone is included.

**zone_max_incl**
    Boolean determining whether the maximum zone is included.

**zoneheight**
    The zone height of a zone, in degrees

**nodes**
    The total number of nodes in the sharded database configuration.

runningcatalog
==============

While a single entry in ``extractedsource`` corresponds to an individual source
measurement, 
a single entry in ``runningcatalog`` corresponds to a unique astronomical
source detected in a specific dataset (series of images). 
The position of this unique source is a weighted mean of all its individual
source measurements.
The relation between a ``runningcatalog`` source and all its measurements in
``extractedsource`` is maintained in ``assocxtrsource``.

The association procedure matches extracted sources with counterpart candidates 
in the runningcatalog table. 
Depending on their association parameters (distance and De Ruiter radius) of
the ``runningcatalog`` source and ``extractedsource`` source, 
the source pair ids are added to ``assocxtrsource``. 
The source properties, position, fluxes and their errors in the 
``runningcatalog`` and ``runningcatalog_flux`` tables are then updated to
include the counterpart values from the extracted source as a new datapoint.

If no counterpart could be found for an extracted sources, it is appended to
``runningcatalog`` 
as a "new" source (datapoint=1).

Weighted means for sources positions and fluxes are calculated according to
Bevington, Ch. 4.
If we have a source property :math:`x` and its 1sigma error :math:`e`), its
weighted mean is

.. math::

   \overline{\chi}_N = \frac{\sum_{i=1}^{N} w_i x_i}{\sum_{i=1}^{N} w_i},

where :math:`N` is the number of datapoints and :math:`w_i = 1/{e_i}^2` is the
weight of the :math:`i`-th measurement of :math:`x`.

**id**
    Every source in the running catalog gets a unique id.

**xtrsrc**
    The id of the extractedsource for which this runningcatalog source was
    detected for the first time.

**dataset**
    The dataset to which the runningcatalog source belongs to.

**datapoints**
    The number of datapoints (or number of times this source was detected) that
    is included in the calculation of the averages. It is assumed that a
    source's position stays relatively constant across bands and therefore all
    bands are included in averaging the position.

**zone**
    The zone id in which the source declination resides.  The sphere is devided
    into zones of equal width: here fixed to 1 degree, and the zone is
    effectively the truncated declination. (decl=31.3 => zone=31, decl=31.9 =>
    zone=31)

**wm_ra**
    The weighted mean of RA of the source.

**wm_decl**
    The weighted mean of Declination of the source.

**wm_ra_err**
    The weighted mean of the ra_err of the source

**wm_decl_err**
    The weighted mean of the decl_err of the source

**avg_wra**
    The average of ra/ra_err^2, used for calculating the average weight of ra.
    (This alleviates the computations, when we have lots of datapoints.)

**avg_wdecl**
    Analogous to avg_wra.

**avg_weight_ra**
    The average of 1/ra_err^2, used for calculating the average weight of ra.
        (This alleviates the computations, when we have lots of datapoints.)

**avg_weight_decl**
    Analogous to avg_weight_ra

**x, y, z**
    The Cartesian coordinate representation of wm_ra and wm_decl

**margin**
    Boolean to define that a source is near the 360-0 meridian. Not being used.

**inactive**
    Boolean to set an entry to inactive.  This is done during the `source
    association <database_assoc>` procedure, where e.g. the many-to-many cases
    are handled and an existing entry is replaced by two or more entries.


runningcatalog_flux
===================

The runningcatalog_flux table contains the averaged flux measurements of a
runningcatalog source, per band and stokes parameter. The combination runcat,
band and stokes is the primary key.

The flux squared and weights are used for calculations of the variability
indices, V and eta.

**runcat**
    Reference to the runningcatalog id to which this band/stokes/flux belongs
    to

**band**
    Reference to the frequency band of this flux

**stokes**
    Stokes parameter: 1 = I, 2 = Q, 3 = U, 4 = V

**f_datapoints**
    the number of datapoints for which the averages were calculated

**resolution**
    Not used.

**avg_f_peak**
    average of peak flux

**avg_f_peak_sq**
    average of (peak flux)^2

**avg_f_peak_weight**
    average of one over peak flux errors squared

**avg_weighted_f_peak**
    average of ratio of (peak flux) and (peak flux errors squared)

**avg_weighted_f_peak_sq**
    average of ratio of (peak flux squared) and (peak flux errors squared)

**avg_f_int**
    average of int flux

**avg_f_int_sq**
    average of (int flux)^2

**avg_f_int_weight**
    average of one over int flux errors squared

**avg_weighted_f_int**
    average of ratio of (int flux) and (int flux errors squared)

**avg_weighted_f_int_sq**
    average of ratio of (int flux squared) and (int flux errors squared)

.. _database_temprunningcatalog:

temprunningcatalog
==================

This table contains temporary results. 
At the beginning of the source association procedures the table is empty. 
At the start, the association query adds candidate pairs (matches between 
sources in ``runningcatalog`` and ``extractedsource``) to the temporary table. 
At insertion time, the query calculates for every found source pair 
the new statistical parameters (weighted means, averages), 
using "archive" values from ``runningcatalog`` and including 
the values from ``extractedsource`` as new datapoints. 
Below, a short description of how this is done is given.

Adding includes the new measurements. 
Then, all types of association relations 
(many-to-1, 1-to-many, etc., as described in the `source association
<database_assoc>`, are processed.
At the end of this process, the runningcatalog is updated with the new values
that now include the last datapoint.

When done, this table is emptied again, ready for the next image.

The table name is prefixed "temp", since the data are temporarily stored and
deleted at the end of the association procedure.
After handling the many-to-many, 1-to-many and many-to-1 relations, 
the ``runningcatalog`` is updated with the new "averages". 
The 0-to-1 and 1-to-0 relations are processed separatedly and do not touch this
table.

If we define the average of :math:`x` as 

.. math::

    \overline{x}_N = \frac{1}{N} \sum_{i=1}^{N} x_i,

then, if we add the next datapoint, :math:`x_{N+1}`-th, to it, we can build the
new average as:

.. math::

    \overline{x}_{N+1} = \frac{N \overline{x}_N + x_{N+1}}{N+1} .

This is slightly different for weighted means. If we have a weighted mean,
:math:`\overline{\xi}_N` defined as:

.. math::

    \overline{\xi}_N = \frac{\sum_{i=1}^{N} w_i x_i}{\sum_{i=1}^{N} w_i},

and we add the :math:`N+1`-th measurement of :math:`x_{N+1}` and its error
:math:`e_{N+1}` 
(but using again :math:`w_{N+1} = 1/{e_{N+1}}^2`), we get the new average by:

.. math::

    \frac{
            \frac{N\overline{\xi}_N + w_{N+1} x_N+1}{N+1}
         }
         {
            \frac{N\overline{w}_N + w_{N+1} x_N+1}{N+1}
         }
         = 
         \frac{
            N\overline{\xi}_N + w_{N+1} x_N+1
              }
              {
            N\overline{w}_N + w_{N+1} x_N+1
              }.

Storing the averages relaxes the computations and are helpful in calculating
the variability indices by simply multiplying the necessary columns.

The first variability indicator, the magnitude of the flux variability of a
source, is expressed as the ratio of the sample flux standard deviation.
Written in aggregate form, it is now easy to handle bulk data, and is defined
as 

.. math::

    V_{\nu} = \frac{1}{\overline{I_{\nu}}} 
              \sqrt{ \frac{N}{N-1}
                     \left( \overline{{I_{\nu}}^2}
                            -
                            \overline{I_{\nu}}^2
                     \right)
                   }

The second indicator, the significance of the flux variability, is based on
reduced :math:`\chi^2` statistics. Written in aggregate form it becomes

.. math::

    \eta_{\nu} = \frac{N}{N-1}
                 \left(
                    \overline{w {I_{\nu}}^2}
                    -
                    \frac{\overline{w I_{\nu}}^2}{\overline{w}}
                 \right)

Note that the indices are calculated per frequency band (and per Stokes
parameter).
The parameters in the last two equations correspond to columns in the tables as
follows:

:math:`\overline{I_{\nu}}` to ``avg_f_peak``

:math:`\overline{{I_{\nu}}^2}` to ``avg_f_peak_sq``

:math:`\overline{w {I_{\nu}}^2}` to ``avg_weighted_f_peak_sq``

:math:`\overline{w I_{\nu}}` to ``avg_weighted_f_peak``

:math:`\overline{w}` to ``avg_f_peak_weight``

:math:`N` to ``f_datapoints``, (and not ``datapoints``)


**runcat**
    Reference to the ``runningcatalog`` id. runcat and xtrsrc together form a
    unique combination.

**xtrsrc** 
    Reference to the ``extractedsource`` id. runcat and xtrsrc together form a
    unique combination.

**distance_arcsec**
    The distance in arcsec on the sky of the runcat-xtrsrc association,
    calculated by the database.

**r**
    The De Ruiter radius of the runcat-xtrsrc association, calculated by the
    database.

**dataset** 
    Reference to the ``dataset`` for which this association was calculated.
    Note that it is abundant, since it can also be deduced from runcat.

**band** 
    Reference to ``frequencyband`` id. Association candidates are searched for
    in the same band of the image of the extracted sources

**stokes** 
    Stokes parameter: 1 = I, 2 = Q, 3 = U, 4 = V. Association candidates are
    searched for to have the same Stokes parameter as the image of the
    extracted sources

**datapoints** 
    The number of datapoints, but now including the new measurement. So this is
    calculated as :math:`N = N + 1`, where :math:`N` is the number of
    datapoints from ``runningcatalog`` 

**zone** 
    The zone value, calculated from the updated ``wm_decl`` value.

**wm_ra**
    The weighted mean of RA of the ``runningcatalog`` source *and* the
    extracted source, calculated as above.

**wm_decl** 
    The weighted mean of DEC of the ``runningcatalog`` source *and* the
    extracted source, calculated as above.

**wm_ra_err** 
    The weighted mean of the 1sigma error of RA of the ``runningcatalog``
    source *and* the extracted source, calculated as above.

**wm_decl_err** 
    The weighted mean of the 1sigma error of DEC of the ``runningcatalog``
    source *and* the extracted source, calculated as above.

**avg_wra**
    The average of the weighted ra (ie ra/ra_err^2) of the ``runningcatalog``
    source *and* the extracted source, calculated as above

**avg_wdecl** 
    The average of the weighted DEC (ie decl/decl_err^2) of the
    ``runningcatalog`` source *and* the extracted source, calculated as above

**avg_weight_ra** 
    The average of the weight of ra (ie 1/ra_err^2) of the ``runningcatalog``
    source *and* the extracted source, calculated as above

**avg_weight_decl** 
    The average of the weight of DEC (ie 1/decl_err^2) of the
    ``runningcatalog`` source *and* the extracted source, calculated as above

**x, y, z** 
    The Cartesian coordinate representation of wm_ra and wm_decl

**margin** 
    Not used (yet)

**inactive** 
    During evaluation of the association pairs, some pairs might be set to
    inactive (TRUE), defaults to FALSE.

**beam_semimaj, beam_semimin, beam_pa** 
    Not used (yet)

**f_datapoints** 
    The association query checks (LEFT OUTER JOIN) whether flux measurements of
    this source pair already existed in ``runningctalog_flux``. If not it is
    set to 1, else it will be incremented by 1.

**avg_f_peak** 
    The average peak flux, as stored in ``runningcatalog_flux``, of the
    ``runningcatalog`` source *and* the peak flux of the extracted source,
    calculated as above.

**avg_f_peak_sq** 
    The average of the peak flux squared, as stored in ``runningcatalog_flux``,
    of the ``runningcatalog`` source *and* the peak flux squared of the
    extracted source, calculated as above.

**avg_f_peak_weight** 
    The average of the weight of the peak flux (ie 1/f_peak_err^2), as stored
    in ``runningcatalog_flux``, of the ``runningcatalog`` source *and* the
    weight of the peak flux of the extracted source, calculated as above.

**avg_weighted_f_peak** 
    The average of the weighted peak flux (ie f_peak/f_peak_err^2), as stored
    in ``runningcatalog_flux``, of the ``runningcatalog`` source *and* the
    weighted peak flux of the extracted source, calculated as above.

**avg_weighted_f_peak_sq** 
    The average of the weighted peak flux squared (ie f_peak^2/f_peak_err^2),
    as stored in ``runningcatalog_flux``, of the ``runningcatalog`` source
    *and* the weighted peak flux squared of the extracted source, calculated as
    above.

**avg_f_int** 
    Analoguous to the avg_f_peak

**avg_f_int_sq** 
    Analoguous to the avg_f_peak_sq

**avg_f_int_weight** 
    Analoguous to the avg_f_peak_weight

**avg_weighted_f_int** 
    Analoguous to the avg_weighted_f_peak

**avg_weighted_f_int_sq** 
    Analoguous to the avg_weighted_f_peak_sq



transient
=========

This table contains the detected transients and their characteristics. Based on
the values of the variability indices a source is considered a transient and
appended to the transient table.

We choose to test the null hypothesis, :math:`H_0`, that the source under
consideration is not variable. Contributing terms to :math:`\eta_{\nu}` in the
sum will be of the order of unity, giving a value of roughly one after
:math:`N` measurements. 
With the integral probability, we can quantify the probability of having 
a value equal to or larger than the :math:`\eta_{\nu}` obtained from the
measurements.


**id**
    Every source in the transient table gets a unique id, set by the database

**runcat**
    Reference to the runningcatalog source to which this transient belongs to.
    Since every trasient has an entry in th erunningcatalog this cannot be
    NULL.

**band**
    The frequency band in which the transient was found, and for which th
    evariability are calculated

**siglevel** 
    The significance level of the 2nd variability index value. Calculated by
    the scipy module chisqprob(), where we use :math:`N-1` as the degree of
    freedom

**v_int**
    The first variability index, :math:`V_{\nu}`, based on the integrated flux
    values.

**eta_int** 
    The second variability index, :math:`\eta_{\nu}`, based on the integrated
    flux values.

**detection_level**
    Currently not set

**trigger_xtrsrc**
    Reference to the extracted source id that caused this transient to be added

**status**
    Currently not set

**t_start**
    Currently not set

version
=======

This table contains the current schema version of the database. Every schema
upgrade will increment the value by 1.

**name**
    The name of the version

**value**
    The version number, which increments after every database change
