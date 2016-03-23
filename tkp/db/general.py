"""
A collection of back end subroutines (mostly SQL queries).

In this module we collect together various routines
that don't fit into a more specific collection.
"""

import math
import logging
import itertools

import tkp.db
from tkp.utility.coordinates import eq_to_cart
from tkp.utility.coordinates import alpha_inflate
from tkp.utility import substitute_inf


logger = logging.getLogger(__name__)


lightcurve_query = """
SELECT im.taustart_ts
      ,im.tau_time
      ,ex.f_int
      ,ex.f_int_err
      ,ex.id
      ,im.band
      ,im.stokes
      ,bd.freq_central
  FROM extractedsource ex
      ,assocxtrsource ax
      ,image im
      ,frequencyband bd
 WHERE ax.runcat IN (SELECT runcat
                       FROM assocxtrsource
                      WHERE xtrsrc = %(xtrsrc)s
                    )
   AND ax.xtrsrc = ex.id
   AND ex.image = im.id
   AND bd.id = im.band
ORDER BY im.taustart_ts
"""

update_dataset_process_end_ts_query = """
UPDATE dataset
   SET process_end_ts = NOW()
 WHERE id = %(dataset_id)s
"""

def update_dataset_process_end_ts(dataset_id):
    """Update dataset start-of-processing timestamp.

    """
    args = {'dataset_id': dataset_id}
    tkp.db.execute(update_dataset_process_end_ts_query, args, commit=True)
    return dataset_id


def insert_dataset(description):
    """Insert dataset with description as given by argument.

    DB function insertDataset() sets the necessary default values.
    """
    query = "SELECT insertDataset(%s)"
    arguments = (description,)
    cursor = tkp.db.execute(query, arguments, commit=True)
    dataset_id = cursor.fetchone()[0]
    return dataset_id


def insert_monitor_positions(dataset_id, positions):
    """
    Add entries to the ``monitor`` table.

    Args:
      dataset_id (int): Positions will only be monitored when processing this
        dataset.
      positions (list of tuples): List of (RA, decl) tuples in decimal degrees.
    """

    monitor_entries = [(dataset_id, p[0], p[1]) for p in positions]

    insertion_query =  """\
INSERT INTO monitor
  (
  dataset
  ,ra
  ,decl
  )
VALUES {placeholder}
"""
    cols_per_row = 3
    placeholder_per_row = '('+ ','.join(['%s']*cols_per_row) +')'
    placeholder_full = ','.join([placeholder_per_row]*len(positions))
    query = insertion_query.format(placeholder= placeholder_full)
    cursor = tkp.db.execute(
        query, tuple(itertools.chain.from_iterable(monitor_entries)),
        commit=True)
    insert_num = cursor.rowcount
    logger.info("Inserted %d sources in monitor table for dataset %s" %
                    (insert_num, dataset_id))


def insert_image(dataset, freq_eff, freq_bw,
                 taustart_ts, tau_time,
                 beam_smaj_pix, beam_smin_pix, beam_pa_rad,
                 deltax, deltay,
                 url,
                 centre_ra, centre_decl, xtr_radius,
                 rms_qc,  rms_min, rms_max,
                 detection_thresh, analysis_thresh
                 ):
    """
    Insert an image for a given dataset.

    Args:
        dataset (int): ID of parent dataset.
        freq_eff: See :ref:`Image table definitions <schema-image>`.
        freq_bw: See :ref:`Image table definitions <schema-image>`.
        taustart_ts: See :ref:`Image table definitions <schema-image>`.
        taus_time: See :ref:`Image table definitions <schema-image>`.
        beam_smaj_pix (float): Restoring beam semimajor axis length in pixels.
            (Converted to degrees before storing to database).
        beam_smin_pix (float): Restoring beam semiminor axis length in pixels.
            (Converted to degrees before storing to database).
        beam_pa_rad (float): Restoring beam parallactic angle in radians.
            (Converted to degrees before storing to database).
        deltax(float): Degrees per pixel increment in x-direction.
        deltay(float): Degrees per pixel increment in y-direction.
        centre_ra(float): Image central RA co-ord, in degrees.
        centre_decl(float): Image central Declination co-ord, in degrees.
        xtr_radius(float): Radius in degrees from field centre that will be used
            for source extraction.

    """
    query = """\
    SELECT insertImage(%(dataset)s
                      ,%(tau_time)s
                      ,%(freq_eff)s
                      ,%(freq_bw)s
                      ,%(taustart_ts)s
                      ,%(rb_smaj)s
                      ,%(rb_smin)s
                      ,%(rb_pa)s
                      ,%(deltax)s
                      ,%(deltay)s
                      ,%(url)s
                      ,%(centre_ra)s
                      ,%(centre_decl)s
                      ,%(xtr_radius)s
                      ,%(rms_qc)s
                      ,%(rms_min)s
                      ,%(rms_max)s
                      ,%(detection_thresh)s
                      ,%(analysis_thresh)s
                      )
    """
    arguments = {'dataset': dataset,
                 'tau_time': tau_time,
                 'freq_eff': freq_eff,
                 'freq_bw': freq_bw,
                 'taustart_ts': taustart_ts,
                 'rb_smaj': beam_smaj_pix * math.fabs(deltax),
                 'rb_smin': beam_smin_pix * math.fabs(deltay),
                 'rb_pa': 180 * beam_pa_rad / math.pi,
                 'deltax': deltax,
                 'deltay': deltay,
                 'url': url,
                 'centre_ra': centre_ra,
                 'centre_decl': centre_decl,
                 'xtr_radius': xtr_radius,
                 'rms_qc': rms_qc,
                 'rms_min': rms_min,
                 'rms_max': rms_max,
                 'detection_thresh': detection_thresh,
                 'analysis_thresh': analysis_thresh,
                 }
    cursor = tkp.db.execute(query, arguments, commit=True)
    image_id = cursor.fetchone()[0]
    return image_id


def insert_extracted_sources(image_id, results, extract_type,
                             ff_runcat_ids=None, ff_monitor_ids=None):
    """
    Insert all detections from sourcefinder into the extractedsource table.

    Besides the source properties from sourcefinder, we calculate additional
    attributes that are increase performance in other tasks.

    The strict sequence from results (the sourcefinder detections) is given below.
    Note the units between sourcefinder and database.
    (0) ra [deg], (1) dec [deg],
    (2) ra_fit_err [deg], (3) decl_fit_err [deg],
    (4) peak_flux [Jy], (5) peak_flux_err [Jy],
    (6) int_flux [Jy], (7) int_flux_err [Jy],
    (8) significance detection level,
    (9) beam major width (arcsec), (10) - minor width (arcsec), (11) - parallactic angle [deg],
    (12) ew_sys_err [arcsec], (13) ns_sys_err [arcsec],
    (14) error_radius [arcsec]
    (15) gaussian fit (bool)
    (16), (17) chisq, reduced_chisq (float)

    ra_fit_err and decl_fit_err are the 1-sigma errors from the gaussian fit,
    in degrees. Note that for a source located towards the poles the ra_fit_err
    increases with absolute declination.
    error_radius is a pessimistic on-sky error estimate in arcsec.
    ew_sys_err and ns_sys_err represent the telescope dependent systematic errors
    and are in arcsec.
    An on-sky error (declination independent, and used in de ruiter calculations)
    is then:
    uncertainty_ew^2 = ew_sys_err^2 + error_radius^2
    uncertainty_ns^2 = ns_sys_err^2 + error_radius^2
    The units of uncertainty_ew and uncertainty_ns are in degrees.
    The error on RA is given by ra_err. For a source with an RA of ra and an error
    of ra_err, its RA lies in the range [ra-ra_err, ra+ra_err].
    ra_err^2 = ra_fit_err^2 + [alpha_inflate(ew_sys_err,decl)]^2
    decl_err^2 = decl_fit_err^2 + ns_sys_err^2.
    The units of ra_err and decl_err are in degrees.
    Here alpha_inflate() is the RA inflation function, it converts an
    angular on-sky distance to a ra distance at given declination.

    Input argument "extract" tells whether the source detections originate from:
    'blind': blind source extraction
    'ff_nd': from forced fits at null detection locations
    'ff_ms': from forced fits at monitoringlist positions

    Input argument ff_runcat is not empty in the case of forced fits from
    null detections. It contains the runningcatalog ids from which the
    source positions were derived for the forced fits. In that case the
    runcat ids will be inserted into the extractedsource table as well,
    to simplify further null-detection processing.
    For blind extractions this list is empty (None).

    For all extracted sources additional parameters are calculated,
    and appended to the sourcefinder data. Appended and converted are:

        - the image id to which the extracted sources belong to
        - the zone in which an extracted source falls is calculated, based
          on its declination. We adopt a zoneheight of 1 degree, so
          the floor of the declination represents the zone.
        - the positional errors are converted from degrees to arcsecs
        - the Cartesian coordinates of the source position
        - ra * cos(radians(decl)), this is very often being used in
          source-distance calculations
    """
    if not len(results):
        logger.debug("No extract_type=%s sources added to extractedsource for"
                    " image %s" % (extract_type, image_id))
        return

    xtrsrc = []
    for i, src in enumerate(results):
        r = list(src)
        # Drop any fits with infinite flux errors
        if math.isinf(r[5]) or math.isinf(r[7]):
            logger.warn("Dropped source fit with infinite flux errors "
                        "at position {} {} in image {}".format(
                r[0], r[1], image_id))
            continue
        # Use 360 degree rather than infinite uncertainty for
        # unconstrained positions.
        r[14] = substitute_inf(r[14], 360.0)
        r[15] = int(r[15])
        # ra_err: sqrt of quadratic sum of fitted and systematic errors.
        r.append(math.sqrt(r[2]**2 + alpha_inflate(r[12]/3600., r[1])**2))
        # decl_err: sqrt of quadratic sum of fitted and systematic errors.
        r.append(math.sqrt(r[3]**2 + (r[13]/3600.)**2))
        # uncertainty_ew: sqrt of quadratic sum of systematic error and error_radius
        # divided by 3600 because uncertainty in degrees and others in arcsec.
        r.append(math.sqrt(r[12]**2 + r[14]**2)/3600.)
        # uncertainty_ns: sqrt of quadratic sum of systematic error and error_radius
        # divided by 3600 because uncertainty in degrees and others in arcsec.
        r.append(math.sqrt(r[13]**2 + r[14]**2)/3600.)
        r.append(image_id) # id of the image
        r.append(int(math.floor(r[1]))) # zone
        r.extend(eq_to_cart(r[0], r[1])) # Cartesian x,y,z
        r.append(r[0] * math.cos(math.radians(r[1]))) # ra * cos(radians(decl))
        if extract_type == 'blind':
            r.append(0)
        elif extract_type == 'ff_nd':
            r.append(1)
        elif extract_type == 'ff_ms':
            r.append(2)
        else:
            raise ValueError("Not a valid extractedsource insert type: '%s'"
                             % extract_type)
        if ff_runcat_ids is not None:
            assert len(results)==len(ff_runcat_ids)
            r.append(ff_runcat_ids[i])
        else:
            r.append(None)

        if ff_monitor_ids is not None:
            assert len(results)==len(ff_monitor_ids)
            r.append(ff_monitor_ids[i])
        else:
            r.append(None)

        xtrsrc.append(r)

    insertion_query = """\
INSERT INTO extractedsource
  (ra
  ,decl
  ,ra_fit_err
  ,decl_fit_err
  ,f_peak
  ,f_peak_err
  ,f_int
  ,f_int_err
  ,det_sigma
  ,semimajor
  ,semiminor
  ,pa
  ,ew_sys_err
  ,ns_sys_err
  ,error_radius
  ,fit_type
  ,chisq
  ,reduced_chisq
  ,ra_err
  ,decl_err
  ,uncertainty_ew
  ,uncertainty_ns
  ,image
  ,zone
  ,x
  ,y
  ,z
  ,racosdecl
  ,extract_type
  ,ff_runcat
  ,ff_monitor
  )
VALUES {placeholder}
"""
    if xtrsrc:
        cols_per_row = len(xtrsrc[0])
        placeholder_per_row = '('+ ','.join(['%s']*cols_per_row) +')'

        placeholder_full = ','.join([placeholder_per_row]*len(xtrsrc))

        query = insertion_query.format(placeholder= placeholder_full)
        cursor = tkp.db.execute(query, tuple(itertools.chain.from_iterable(xtrsrc)),
                                commit=True)
        insert_num = cursor.rowcount
        #if insert_num == 0:
        #    logger.info("No forced-fit sources added to extractedsource for "
        #                "image %s" % (image_id,))
        if extract_type == 'blind':
            logger.debug("Inserted %d sources in extractedsource for image %s" %
                        (insert_num, image_id))
        elif extract_type == 'ff_nd':
            logger.debug("Inserted %d forced-fit null detections in extractedsource"
                        " for image %s" % (insert_num, image_id))
        elif extract_type == 'ff_ms':
            logger.debug("Inserted %d forced-fit for monitoring in extractedsource"
                        " for image %s" % (insert_num, image_id))


def lightcurve(xtrsrcid):
    """
    Obtain a light curve for a specific extractedsource

    Args:

        xtrsrcid (int): the source identifier that corresponds to a point on
            the light curve. Note that the point does not have to be the start
            (first) point of the light curve.

    Returns:
        list: a list of tuples, each containing:
            - observation start time as a datetime.datetime object
            - integration time (float)
            - integrated flux (float)
            - integrated flux error (float)
            - database ID of this particular source
            - frequency band ID
            - stokes
    """
    args = {'xtrsrc': xtrsrcid}
    cursor = tkp.db.execute(lightcurve_query, args)
    return cursor.fetchall()
