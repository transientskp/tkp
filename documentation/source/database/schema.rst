.. _database_schema:

++++++
Schema
++++++

.. image:: schema.jpg

assoccatsource
==============

This table stores the information about the extractedsources that could be associated with a catalogedsource.

**xrtsrc**
   This refers to the xtrsrcid of the extractedsource

**catsrc**
   This is the id of the catalogedsource that could be associated to the extractedsource as its counterpart

**type**
   Type of the association

**distance_arcsec**
   The distance in arcsec between the associated sources

**r**
   The dimensionless distance (De Ruiter radius) between the associated sources. It is determined as the positional differences weighted by the errors (Scheers thesis ch3).

**loglr**
   The logarithm of the likelihood ratio of the associated sources (Scheers thesis ch3).


assocxtrsource
==============

This table stores the information about the sources that could be associated.

**runcat**
   refers to the runcatid in runningcatalog.  It is the "base" id of a series of polarized spectral lightcurve datapoints.

**xtrsrc** 
   This is the id of the extracted source that could be associated to runningcatalog source.  Together, the runcat_id and the assoc_xtrsrc_id form a unique pair.

**type**
    Type of association.  x-y, where x is the number of runningcatalog sources, and y the number of extractedsources
    1. 1-1
    2. 1-n
    3. n-1
    4. n-m
    5. 0-1

**distance_arcsec**
   The distance in arcsec between the associated sources.

**r**
   The dimensionless distance (De Ruiter radius) between the associated sources. It is determined as the positional differences weighted by the errors (Scheers thesis ch3).

**loglr**      
   The logarithm of the likelihood ratio of the associated sources (Scheers thesis ch3).


catalogedsource
===============

This table contains the known sources that were detected previously, either by LOFAR itself or other instruments.  It is a selection from the table containing all the catalog sources (in the catlogue area). 

Every observation has its field(s) of view and for this all the known sources are collected. This table will be loaded from the catalog table in the catalog database before every observation.  This table will be used to load the sources table and will not be touched any more during an observation.

Fluxes are in Jy, ra, decl, ra_err and decl_err in degrees.  PA, major, minor in degrees


catalog
=======

This table stores the information about the catalogs that are loaded into the pipeline database.


classification
==============

This table contains classification of transients


dataset
=======

This table contains the information about the dataset that is produced by LOFAR.  A dataset has an integration time and consists of multiple frequency layers.

**taustart_timestamp**
    the start time of the integration


extractedsource
===============

This table contains all the extracted sources during an observation.  Maybe source is not the right description, because measurements may be made that were erronous and do not represent a source.

This table is empty BEFORE an observation.  DURING an observation new sources are inserted into this table AFTER an observation this table is dumped and transported to the catalog database.

**id**
    Every inserted source/measurement gets a unique id.

**image**
    The reference id to the image from which this sources was extracted.

**zone**
    The zone id in which the source declination resides.  The sphere is devided into zones of equal width: here fixed to 1 degree. (decl=31.3 => zone=31)

**ra**
    Right ascension of the measurement [in degrees]

**decl**
    Declination of the measurement [in degrees]

**ra_err**
    The 1-sigma error of the ra measurement [in arcsec]

**decl_err**
    The 1-sigma error of the declination measurement [in arcsec]

**x, y, z**
    Cartesian coordinate representation of (ra,decl)

**margin**
    Used for association procedures to take into account sources that lie close to ra=0 & ra=360 meridian.
    * True: source is close to ra=0 meridian
    * False: source is far away enough from the ra=0 meridian
    * NOTE & TODO: This is not implemented yet.

**det_sigma**
    The sigma level of the detection (Hanno's thesis): 20*(I_peak/det_sigma) gives the rms of the detection.

**semimajor**
    Semi-major axis that was used for gauss fitting [in arcsec]

**semiminor**
    Semi-minor axis that was used for gauss fitting [in arcsec]

**pa**
    Position Angle that was used for gauss fitting [from north through local east, in degrees]

**f_peak**
    peak flux [Jy]

**f_int**
    integrated flux [Jy]

**f_peak/int_err**
    1-sigma errors respectively [Jy]

**type**
    Reports how the source was extracted by sourcefinder (Hanno's thesis):

    1: gaussian fit
    2: moments fit
    3: forced fit to pixel

**node(s)**
    Determine the current and number of nodes in case of a sharded database set-up.


frequencyband
=============

This table contains the frequencies at which the extracted sources were detected. It might also be preloaded with the frequencies at which the stokes of the catalog sources were measured.


image
=====

This table contains the images that are being processed.  The only format for now is FITS. The HDF5 format will be implemented later.

An image is characterised by

* integration time (tau)
* frequency band (band) 
* timestamp (seq_nr).

A group of images that belong together (not specified any further) are in the same data set (they have the same ds_id).

**tau_time**
   in seconds (ref. tau)
**freq_eff**
   in Hz (ref. band)

**taustart_timestamp**
    in YYYY-MM-DD-HH:mm:ss:nnnnnn, but without interpunctions (ref. seq_nr)

**bsmaj, bsmin, bpa**
	the semimajor, semiminor axes of the synthesized beam in degrees. NOTE that these *ARE* the semimajor axes.

**centr_ra and _decl**
	the central coordinates (J2000) of the image in degrees.


monitoringlist
==============

This table contains the list of sources that are monitored. This implies that the source finder software will measure the flux in an image at exactly the given position. 

These positions are 0 by default, since they can be retrieved by joining with the runningcatalog.

For user defined sources, however, positions may be available that are more precise than those in the runningcatalog. Hence the ra and decl columns are still necessary for these sources.  The xtrsrc_id refers to the xtrsrc_id in the runningcatalog, when available. Eg, manually inserted sources with positions obtained differently will not have an xtrsrc_id to start with (hence the default of -1), until the first time the flux has been measured; then these sources (even when actual upper limits) will be inserted into extractedsources and runningcatalog, and have an xtrsrc_id.  They will still have userentry set to true, so that the position used is that in this table (the more precise position), not that of the runningcatalog.


node
====

This table keeps track of the versions and changes


runningcatalog
==============

This table contains the unique sources that were detected during an observation.

TODO: The resolution element (from images table) is not implemented yet.

Extractedsources not in this table are appended when there is no positional match or when a source was detected in a higher resolution image.

We maintain weighted averages for the sources (see ch4, Bevington).

**wm_** 
    weighted mean

**wm_ra**
    avg_wra/avg_weight_ra

**wm_decl**
    avg_wdecl/avg_weight_decl

**wm_ra_err**
    1/(N * avg_weight_ra)

**wm_decl_err**
    1/(N * avg_weight_decl)

**avg_wra**
    avg(ra/ra_err^2)

**avg_wdecl**
    avg(decl/decl_err^2)

**avg_weight_ra**
    avg(1/ra_err^2) 

**avg_weight_decl**
    avg(1/decl_err^2)



runningcatalog_flux
===================

**stokes**
    Stokes parameter: 1 = I, 2 = Q, 3 = U, 4 = V

**f_datapoints**
    the number of datapoints for which the averages were calculated

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


temprunningcatalog
==================

This table contains the unique sources that were detected during an observation.
Extractedsources not in this table are appended when there is no positional match or when a source was detected in a higher resolution image.


transient
=========

This table contains the detected transients and their characteristics.


version
=======

This table contains the current schema version of the database. It is used to decide which operations are required to upgrade the database to a specific version.

