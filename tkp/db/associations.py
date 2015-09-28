"""
A collection of back end subroutines (mostly SQL queries), In this module we
deal with source association.
"""
import logging
import tkp.db
from sqlalchemy.exc import IntegrityError


logger = logging.getLogger(__name__)


def associate_extracted_sources(image_id, deRuiter_r, beamwidths_limit=1,
                                new_source_sigma_margin=3):
    """
    Associate extracted sources with sources detected in the running
    catalog.

    See the "developer's reference" section of the docs for a step-by-step
    breakdown of the logic encapsulated here.

    The dimensionless distance between two sources is given by the
    "De Ruiter radius", see Chapters 2 & 3 of Scheers' thesis.
    """

    logger.debug("Using a De Ruiter radius of %s" % (deRuiter_r,))
    ##This is used as a check that everything from the sourcefinder is sensible.
    ##Currently switched off as it's incompatible with sources about the meridian.
#    _delete_bad_blind_extractions(conn, image_id)
    _empty_temprunningcatalog()
    #+------------------------------------------------------+
    #| Here we select all extracted sources that have one or|
    #| more counterparts in the runningcatalog              |
    #| Association pairs are of the sequence runcat-xtrsrc, |
    #| which may be matching one of the following cases:    |
    #| many-to-many, many-to-one, one-to-many, one-to-many  |
    #+------------------------------------------------------+
    mw = _check_meridian_wrap(image_id)
    _insert_temprunningcatalog(image_id, deRuiter_r, beamwidths_limit, mw)
    #+------------------------------------------------------+
    #| Here we process (flag) the many-to-many associations.|
    #+------------------------------------------------------+
    database = tkp.db.Database()

    # Since the _flag_many_to_many_tempruncat uses the temprunningcatalog table
    # as a temporary use space the table will receive many writes and updates.
    # On postgresql for speed up reasons rows are not directly deleted, but
    # marked for deletion and eventually deleted by an auto vacuum process.
    # Because of the nested complexity of this query it may happen the
    # computational complexity of the query explodes, resulting in massive
    # slowdowns. To make sure the temprunningcatalog table doesn't contain dead
    # rows we force a manual vacuum here.
    database.vacuum('temprunningcatalog')

    # _process_many_to_many()
    _flag_many_to_many_tempruncat()
    #+------------------------------------------------------+
    #| After this, the assocs have been reduced to many-to-1|
    #| which are treated identical as 1-to-1, and 1-to-many.|
    #+------------------------------------------------------+
    # _process_many_to_1() => process_1_to_1()
    #+------------------------------------------------------+
    #| Here we process the one-to-many associations.        |
    #+------------------------------------------------------+
    try:
        _insert_1_to_many_runcat()
    except IntegrityError as e:
        logger.error("Error caught around _insert_1_to_many_runcat - "
                 "possible 'IntegrityError'. See Issue #4778. Will now re-raise.")
        raise e

    _flag_1_to_many_inactive_runcat()

    _insert_1_to_many_runcat_flux()
    _delete_1_to_many_inactive_runcat_flux()

    _insert_1_to_many_basepoint_assocxtrsource()
    _insert_1_to_many_replacement_assocxtrsource()
    _delete_1_to_many_inactive_assocxtrsource()

    _insert_1_to_many_assocskyrgn()
    _delete_1_to_many_inactive_assocskyrgn()

    _insert_1_to_many_newsource()
    _delete_1_to_many_inactive_newsource()

    _flag_1_to_many_inactive_tempruncat()

    #+-----------------------------------------------------+
    #| Here we process the one-to-one associations         |
    #+-----------------------------------------------------+
    # _process_1_to_1()
    _insert_1_to_1_assoc()
    _update_1_to_1_runcat()
    n_updated_rf = _update_1_to_1_runcat_flux()  # update flux in existing band
    if n_updated_rf:
        logger.debug("Updated 1-to-1 fluxes for %s sources" % n_updated_rf)
    n_new_rf = _insert_1_to_1_runcat_flux()  # insert flux for new band
    if n_new_rf:
        logger.debug("Inserted new fluxes for %s sources" % n_new_rf)
    #+-------------------------------------------------------+
    #| Here we take care of the extracted sources that could |
    #| not be associated with any runningcatalog source      |
    #+-------------------------------------------------------+
    _insert_new_runcat(image_id)
    _insert_new_runcat_flux(image_id)
    _insert_new_runcat_skyrgn_assocs(image_id)
    _insert_new_assocxtrsource(image_id)
    _determine_newsource_previous_limits(image_id, new_source_sigma_margin)

    _empty_temprunningcatalog()
    _update_ff_runcat_extractedsource()
    _delete_inactive_runcat()

##############################################################################
# Subroutines...
# Here be SQL dragons.
##############################################################################


def _delete_bad_blind_extractions(image_id):
    """Remove blind extractions centred outside designated extract region.

    These occur sometimes due to highly elliptical fits on noisy data,
    creating a best fit centred outside the original pixel region.
    The source-extraction code has been modified to (probably) prevent this,
    but we check for them anyway.

    NB. We currently only delete blind extractions.
    We expect that occasionally forced fits to sources just inside the extraction
    radius might converge just outside, but these should be restricted to a
    very small additional margin. By not deleting these edge cases,
    the data allows us to construct proper lightcurves, and (I think) does
    not contribute to their weighted mean positions (so sources cannot 'migrate'
    across the border).
    TODO(TS): Check this.

    Only extractions from the specified image are checked for deletion.

    Returns:
      Number of extractedsource rows deleted.
    """
    query = """\
DELETE
FROM extractedsource
WHERE image = %(imgid)s
  AND id IN (SELECT badid
              FROM (SELECT ex0.id as badid
                    ,SQRT(
                      ( (ex0.ra  - sky.centre_ra)* COS(RADIANS(sky.centre_decl))
                     *(ex0.ra  - sky.centre_ra)* COS(RADIANS(sky.centre_decl))
                      + (ex0.decl - sky.centre_decl) * (ex0.decl - sky.centre_decl))
                      ) as distance
                      ,sky.xtr_radius as xtr_radius
                  FROM extractedsource ex0
                      ,image im
                      ,skyregion sky
                  WHERE im.id = %(imgid)s
                   AND ex0.image = im.id
                   AND ex0.extract_type = 0
                   AND im.skyrgn = sky.id
                   ) t1
               WHERE t1.distance > t1.xtr_radius
               )
"""

    qry_params = {'imgid':image_id}
    cursor = tkp.db.execute(query, qry_params, commit=True)
    n_deleted = cursor.rowcount
    if n_deleted:
        logger.warn("Removed %s bad blind extractions for image %s"
                     "(centred outside extraction region)",
                     n_deleted, image_id)
    return n_deleted


def _empty_temprunningcatalog():
    """Initialize the temporary storage table

    Initialize the temporary table temprunningcatalog which contains
    the current observed sources.
    """
    query = "DELETE FROM temprunningcatalog"
    tkp.db.execute(query, commit=True)



def _check_meridian_wrap(image_id):
    """
    Checks whether an image is close to the meridian ra = 0 or ra = 360

    When so, the association query needs to be rewritten to take into account
    sources across the 0/360 meridian.

    The query returns:

    q_across: true, if the extraction region of the image crosses
              the ra=0/360 border

    ra_min:   the min value of the ra-between for the normal case,
              when the image is outside the ra=0/360 meridian,
              otherwise NULL

    ra_max:   the max value of the ra-between for the normal case,
              when the image is outside the ra=0/360 meridian,
              otherwise NULL

    ra_min1/max1 and ra_min2/max2 are the values which may be used
    for the case of a cross-meridian image.
    F.ex. using a search radius of 5 degrees, and when a source is at
    359.99 the ra-betweens 1 and 2 are :
    ... AND (ra BETWEEN ra_min1 AND ra_max1 OR ra BETWEEN ra_min2 AND ra_max2) ...
    ... AND (ra BETWEEN 354.99 AND 360 OR ra BETWEEN 0 AND 4.99) ...

    ra_min1:  the min value of the high-end ra-between, if the
              extraction region of the image crosses the ra=0/360 border,
              otherwise NULL

    ra_max1:  the min value of the high-end ra-between, if the
              extraction region of the image crosses the ra=0/360 border,
              otherwise NULL

    ra_min2, ra_max2: As ra_min1/max1, but for the low-end ra values.

    These values are not being used in the cross-meridian association query,
    but are merely reported to notice the search area.
    The cross-meridian association query uses the cartesian dot product,
    to get the search area.
    """

    meridian_wrap_query = """\
SELECT CASE WHEN s.centre_ra - alpha(s.xtr_radius, s.centre_decl) < 0 OR
                 s.centre_ra + alpha(s.xtr_radius, s.centre_decl) > 360
            THEN TRUE
            ELSE FALSE
       END AS q_across
      ,CASE WHEN s.centre_ra - alpha(s.xtr_radius, s.centre_decl) > 0 AND
                 s.centre_ra + alpha(s.xtr_radius, s.centre_decl) < 360
            THEN s.centre_ra - alpha(s.xtr_radius, s.centre_decl)
            ELSE NULL
       END AS ra_min
      ,CASE WHEN s.centre_ra - alpha(s.xtr_radius, s.centre_decl) > 0 AND
                 s.centre_ra + alpha(s.xtr_radius, s.centre_decl) < 360
            THEN s.centre_ra + alpha(s.xtr_radius, s.centre_decl)
            ELSE NULL
       END AS ra_max
      ,CASE WHEN s.centre_ra - alpha(s.xtr_radius, s.centre_decl) < 0
            THEN s.centre_ra - alpha(s.xtr_radius, s.centre_decl) + 360.0
            ELSE CASE WHEN s.centre_ra + alpha(s.xtr_radius, s.centre_decl) > 360
                      THEN s.centre_ra - alpha(s.xtr_radius, s.centre_decl)
                      ELSE NULL
                 END
       END AS ra_min1
      ,CASE WHEN s.centre_ra - alpha(s.xtr_radius, s.centre_decl) < 0 OR
                 s.centre_ra + alpha(s.xtr_radius, s.centre_decl) > 360
            THEN 360
            ELSE NULL
       END AS ra_max1
      ,CASE WHEN s.centre_ra - alpha(s.xtr_radius, s.centre_decl) < 0 OR
                 s.centre_ra + alpha(s.xtr_radius, s.centre_decl) > 360
            THEN 0
            ELSE NULL
       END AS ra_min2
      ,CASE WHEN s.centre_ra - alpha(s.xtr_radius, s.centre_decl) < 0
            THEN s.centre_ra + alpha(s.xtr_radius, s.centre_decl)
            ELSE CASE WHEN s.centre_ra + alpha(s.xtr_radius, s.centre_decl) > 360
                      THEN s.centre_ra + alpha(s.xtr_radius, s.centre_decl) - 360
                      ELSE NULL
                 END
       END AS ra_max2
  FROM image i
      ,skyregion s
 WHERE i.skyrgn = s.id
   AND i.id = %(image_id)s
"""
    args = {'image_id': image_id}
    cursor = tkp.db.execute(meridian_wrap_query, args, commit=True)
    results = zip(*cursor.fetchall())

    if len(results) != 0:
        q_across = results[0]
        ra_min = results[1]
        ra_max = results[2]
        ra_min1 = results[3]
        ra_max1 = results[4]
        ra_min2 = results[5]
        ra_max2 = results[6]
        if len(q_across) != 1:
            raise ValueError("More than one FoVs for image '%s'" % image_id)
    else:
        raise ValueError("No FoV information present for image '%s'" % image_id)

    return {
        'q_across': q_across[0],
        'ra_min': ra_min[0],
        'ra_max': ra_max[0],
        'ra_min1': ra_min1[0],
        'ra_max1': ra_max1[0],
        'ra_min2': ra_min2[0],
        'ra_max2': ra_max2[0]
    }


def _insert_temprunningcatalog(image_id, deRuiter_r, beamwidths_limit,
                               meridian_wrap):
    """Select matched sources

    Here we select the extractedsource that have a positional match
    with the sources in the running catalogue table (runningcatalog).
    Those sources which *do* have a potential match, will be inserted into the
    temporary running catalogue table (temprunningcatalog).

    See also:
    http://docs.transientskp.org/tkp/database/schema.html#temprunningcatalog

    Explanation of some column name prefixes/suffixes used in the SQL query:

    - avg_X := average of X
    - avg_X_sq := average of X^2
    - avg_weight_X := average of weight of X, i.e. mean( 1/error^2 )
    - avg_weighted_X := average of weighted X,
         i.e. mean(X/error^2)
    - avg_weighted_X_sq := average of weighted X^2,
         i.e. mean(X^2/error^2)

    This result set might contain multiple associations (1-n,n-1)
    for a single known source in runningcatalog.

    The n-1 assocs will be treated similar as n 1-1 assocs.

    NOTE: Beware of the extra condition on x0.image in the WHERE clause,
    preventing the query to grow exponentially in response time
    """

    # The cross-meridian differs slightly from the normal association query.
    #
    # We removed the wm_ra between statement, because the dot-product of the
    # cartesian coordinates will handle the distance checking in case of
    # meridian wrapping.
    #
    # The RA values for sources with 270 < wm_ra < 90 are translated to the
    # opposite site of the sphere, where we can easily work with the modulo
    # values to calculate the ra position (but this is of course translated
    # back) and de Ruiter radius.
    #
    # Note that a weighted mean RA in the range [-8e-14, 0) is snapped to
    # zero. This accounts for dynamic range issues with doubles: if we end up
    # with a tiny sub-zero RA and add 360 to it, we end up with 360 rather
    # than 359.999..., but, of course, we don't regard an RA of 360 as
    # meaningful.
    q_across_ra0 = """\
INSERT INTO temprunningcatalog
  (runcat
  ,xtrsrc
  ,distance_arcsec
  ,r
  ,dataset
  ,band
  ,stokes
  ,datapoints
  ,zone
  ,wm_ra
  ,wm_decl
  ,wm_uncertainty_ew
  ,wm_uncertainty_ns
  ,avg_ra_err
  ,avg_decl_err
  ,avg_wra
  ,avg_wdecl
  ,avg_weight_ra
  ,avg_weight_decl
  ,x
  ,y
  ,z
  ,f_datapoints
  ,avg_f_peak
  ,avg_f_peak_sq
  ,avg_f_peak_weight
  ,avg_weighted_f_peak
  ,avg_weighted_f_peak_sq
  ,avg_f_int
  ,avg_f_int_sq
  ,avg_f_int_weight
  ,avg_weighted_f_int
  ,avg_weighted_f_int_sq
  )
  SELECT t0.runcat
        ,t0.xtrsrc
        ,t0.distance_arcsec
        ,t0.r
        ,t0.dataset
        ,t0.band
        ,t0.stokes
        ,t0.datapoints
        ,CAST(FLOOR(t0.wm_decl) AS INTEGER) AS zone
        ,CASE WHEN t0.wm_ra < 0
              THEN CASE WHEN ABS(t0.wm_ra) > 8e-14
                        THEN t0.wm_ra + 360
                        ELSE 0.0
                   END
              ELSE t0.wm_ra
         END AS wm_ra
        ,t0.wm_decl
        ,t0.wm_uncertainty_ew
        ,t0.wm_uncertainty_ns
        ,t0.avg_ra_err
        ,t0.avg_decl_err
        ,t0.avg_wra
        ,t0.avg_wdecl
        ,t0.avg_weight_ra
        ,t0.avg_weight_decl
        ,COS(RADIANS(t0.wm_decl)) * COS(RADIANS(t0.wm_ra)) AS x
        ,COS(RADIANS(t0.wm_decl)) * SIN(RADIANS(t0.wm_ra)) AS y
        ,SIN(RADIANS(t0.wm_decl)) AS z
        ,CASE WHEN rf0.f_datapoints IS NULL
              THEN 1
              ELSE rf0.f_datapoints + 1
         END AS f_datapoints
        ,CASE WHEN rf0.f_datapoints IS NULL
              THEN t0.f_peak
              ELSE (rf0.f_datapoints * rf0.avg_f_peak
                    + t0.f_peak)
                   / (rf0.f_datapoints + 1)
         END AS avg_f_peak
        ,CASE WHEN rf0.f_datapoints IS NULL
              THEN t0.f_peak * t0.f_peak
              ELSE (rf0.f_datapoints * rf0.avg_f_peak_sq
                    + t0.f_peak * t0.f_peak)
                   / (rf0.f_datapoints + 1)
         END AS avg_f_peak_sq
        ,CASE WHEN rf0.f_datapoints IS NULL
              THEN 1 / (t0.f_peak_err * t0.f_peak_err)
              ELSE (rf0.f_datapoints * rf0.avg_f_peak_weight
                    + 1 / (t0.f_peak_err * t0.f_peak_err))
                   / (rf0.f_datapoints + 1)
         END AS avg_f_peak_weight
        ,CASE WHEN rf0.f_datapoints IS NULL
              THEN t0.f_peak / (t0.f_peak_err * t0.f_peak_err)
              ELSE (rf0.f_datapoints * rf0.avg_weighted_f_peak
                    + t0.f_peak / (t0.f_peak_err * t0.f_peak_err))
                   / (rf0.f_datapoints + 1)
         END AS avg_weighted_f_peak
        ,CASE WHEN rf0.f_datapoints IS NULL
              THEN t0.f_peak * t0.f_peak / (t0.f_peak_err * t0.f_peak_err)
              ELSE (rf0.f_datapoints * rf0.avg_weighted_f_peak_sq
                    + (t0.f_peak * t0.f_peak) / (t0.f_peak_err * t0.f_peak_err))
                   / (rf0.f_datapoints + 1)
         END AS avg_weighted_f_peak_sq
        ,CASE WHEN rf0.f_datapoints IS NULL
              THEN t0.f_int
              ELSE (rf0.f_datapoints * rf0.avg_f_int
                    + t0.f_int)
                   / (rf0.f_datapoints + 1)
         END AS avg_f_int
        ,CASE WHEN rf0.f_datapoints IS NULL
              THEN t0.f_int * t0.f_int
              ELSE (rf0.f_datapoints * rf0.avg_f_int_sq
                    + t0.f_int * t0.f_int)
                   / (rf0.f_datapoints + 1)
         END AS avg_f_int_sq
        ,CASE WHEN rf0.f_datapoints IS NULL
              THEN 1 / (t0.f_int_err * t0.f_int_err)
              ELSE (rf0.f_datapoints * rf0.avg_f_int_weight
                    + 1 / (t0.f_int_err * t0.f_int_err))
                   / (rf0.f_datapoints + 1)
         END AS avg_f_int_weight
        ,CASE WHEN rf0.f_datapoints IS NULL
              THEN t0.f_int / (t0.f_int_err * t0.f_int_err)
              ELSE (rf0.f_datapoints * rf0.avg_weighted_f_int
                    + t0.f_int / (t0.f_int_err * t0.f_int_err))
                   / (rf0.f_datapoints + 1)
         END AS avg_weighted_f_int
        ,CASE WHEN rf0.f_datapoints IS NULL
              THEN t0.f_int * t0.f_int / (t0.f_int_err * t0.f_int_err)
              ELSE (rf0.f_datapoints * rf0.avg_weighted_f_int_sq
                    + (t0.f_int * t0.f_int) / (t0.f_int_err * t0.f_int_err))
                   / (rf0.f_datapoints + 1)
         END AS avg_weighted_f_int_sq
    FROM (SELECT rc0.id as runcat
                ,x0.id as xtrsrc
                ,3600 * DEGREES(2 * ASIN(SQRT( (rc0.x - x0.x) * (rc0.x - x0.x)
                                             + (rc0.y - x0.y) * (rc0.y - x0.y)
                                             + (rc0.z - x0.z) * (rc0.z - x0.z)
                                             ) / 2)
                               ) AS distance_arcsec
                ,CASE WHEN rc0.wm_ra < 90 OR rc0.wm_ra > 270
                      THEN
                           SQRT(  (MOD(CAST(rc0.wm_ra + 180 AS NUMERIC(11,8)), 360) - MOD(CAST(x0.ra + 180 AS NUMERIC(11,8)), 360)) * COS(RADIANS((rc0.wm_decl + x0.decl)/2))
                                 * (MOD(CAST(rc0.wm_ra + 180 AS NUMERIC(11,8)), 360) - MOD(CAST(x0.ra + 180 AS NUMERIC(11,8)), 360)) * COS(RADIANS((rc0.wm_decl + x0.decl)/2))
                                 / (rc0.wm_uncertainty_ew * rc0.wm_uncertainty_ew + x0.uncertainty_ew * x0.uncertainty_ew)
                                 + (rc0.wm_decl - x0.decl) * (rc0.wm_decl - x0.decl)
                                 / (rc0.wm_uncertainty_ns * rc0.wm_uncertainty_ns + x0.uncertainty_ns * x0.uncertainty_ns)
                               )
                      ELSE
                           SQRT(  (rc0.wm_ra - x0.ra) * COS(RADIANS((rc0.wm_decl + x0.decl)/2))
                                 * (rc0.wm_ra - x0.ra) * COS(RADIANS((rc0.wm_decl + x0.decl)/2))
                                 / (rc0.wm_uncertainty_ew * rc0.wm_uncertainty_ew + x0.uncertainty_ew * x0.uncertainty_ew)
                                 +  (rc0.wm_decl - x0.decl) * (rc0.wm_decl - x0.decl)
                                 / (rc0.wm_uncertainty_ns * rc0.wm_uncertainty_ns + x0.uncertainty_ns * x0.uncertainty_ns)
                                )
                 END AS r
                ,x0.f_peak
                ,x0.f_peak_err
                ,x0.f_int
                ,x0.f_int_err
                ,i0.dataset
                ,i0.band
                ,i0.stokes
                ,rc0.datapoints + 1 AS datapoints
                ,CASE WHEN rc0.wm_ra < 90 OR rc0.wm_ra > 270
                      THEN (datapoints * rc0.avg_weight_ra * MOD(CAST(rc0.wm_ra + 180 AS NUMERIC(11,8)), 360) + MOD(CAST(x0.ra + 180 AS NUMERIC(11,8)), 360) / (x0.uncertainty_ew * x0.uncertainty_ew) )
                           /
                           (datapoints * rc0.avg_weight_ra + 1 / (x0.uncertainty_ew * x0.uncertainty_ew) ) - 180
                      ELSE
                           (datapoints * rc0.avg_wra + x0.ra /(x0.uncertainty_ew * x0.uncertainty_ew) )
                           /
                           (datapoints * rc0.avg_weight_ra + 1 / (x0.uncertainty_ew * x0.uncertainty_ew) )
                 END AS wm_ra
                ,(datapoints * rc0.avg_weight_decl * rc0.wm_decl + x0.decl / (x0.uncertainty_ns * x0.uncertainty_ns))
                 /
                 (datapoints * rc0.avg_weight_decl + 1 / (x0.uncertainty_ns * x0.uncertainty_ns))
                 AS wm_decl
                ,SQRT(1 / ((datapoints + 1) *
                  ((datapoints * rc0.avg_weight_ra +
                    1 / (x0.uncertainty_ew * x0.uncertainty_ew)) / (datapoints + 1))
                          )
                     ) AS wm_uncertainty_ew
                ,SQRT(1 / ((datapoints + 1) *
                  ((datapoints * rc0.avg_weight_decl +
                    1 / (x0.uncertainty_ns * x0.uncertainty_ns)) / (datapoints + 1))
                          )
                     ) AS wm_uncertainty_ns
                ,(datapoints * rc0.avg_ra_err + x0.ra_err) / (datapoints + 1) AS avg_ra_err
                ,(datapoints * rc0.avg_decl_err + x0.decl_err) / (datapoints + 1) AS avg_decl_err
                ,CASE WHEN rc0.wm_ra < 90 OR rc0.wm_ra > 270
                      THEN ((datapoints * rc0.avg_weight_ra * MOD(CAST(rc0.wm_ra + 180 AS NUMERIC(11,8)), 360) + MOD(CAST(x0.ra + 180 AS NUMERIC(11,8)), 360) / (x0.uncertainty_ew * x0.uncertainty_ew)
                              - datapoints * avg_weight_ra * 180 - 180 / (x0.uncertainty_ew * x0.uncertainty_ew))
                              / (datapoints + 1))
                            - 360 * (datapoints * rc0.avg_weight_ra + 1 / (x0.uncertainty_ew * x0.uncertainty_ew)) / (datapoints + 1)
                            * FLOOR(
                               ((datapoints * avg_weight_ra * MOD(CAST(rc0.wm_ra + 180 AS NUMERIC(11,8)), 360) + MOD(CAST(x0.ra + 180 AS NUMERIC(11,8)), 360) / (x0.uncertainty_ew * x0.uncertainty_ew)
                                 - datapoints * avg_weight_ra * 180 - 180 / (x0.uncertainty_ew * x0.uncertainty_ew))
                                 / (datapoints + 1))
                               / (360 * (datapoints * rc0.avg_weight_ra + 1 / (x0.uncertainty_ew * x0.uncertainty_ew)) / (datapoints + 1))
                               )
                      ELSE
                            (datapoints * rc0.avg_wra + x0.ra / (x0.uncertainty_ew * x0.uncertainty_ew))
                             / (datapoints + 1)
                 END AS avg_wra
                ,(datapoints * rc0.avg_wdecl + x0.decl / (x0.uncertainty_ns * x0.uncertainty_ns))
                 / (datapoints + 1) AS avg_wdecl
                ,(datapoints * rc0.avg_weight_ra + 1 / (x0.uncertainty_ew * x0.uncertainty_ew))
                 / (datapoints + 1) AS avg_weight_ra
                ,(datapoints * rc0.avg_weight_decl + 1 / (x0.uncertainty_ns * x0.uncertainty_ns))
                 / (datapoints + 1) AS avg_weight_decl
            FROM extractedsource x0
                ,runningcatalog rc0
                ,image i0
           WHERE i0.id = %(image_id)s
             AND x0.image = i0.id
             AND x0.image = %(image_id)s
             AND i0.dataset = rc0.dataset
             AND rc0.mon_src = FALSE
             AND rc0.zone BETWEEN CAST(FLOOR(x0.decl - %(beamwidths_limit)s * i0.rb_smaj) as INTEGER)
                              AND CAST(FLOOR(x0.decl + %(beamwidths_limit)s * i0.rb_smaj) as INTEGER)
             AND rc0.wm_decl BETWEEN x0.decl - %(beamwidths_limit)s * i0.rb_smaj
                                 AND x0.decl + %(beamwidths_limit)s * i0.rb_smaj
             AND rc0.x*x0.x + rc0.y*x0.y + rc0.z*x0.z > cos(radians(%(beamwidths_limit)s * i0.rb_smaj))
             AND CASE WHEN rc0.wm_ra < 90 OR rc0.wm_ra > 270
                      THEN SQRT(  (MOD(CAST(rc0.wm_ra + 180 AS NUMERIC(11,8)), 360) - MOD(CAST(x0.ra + 180 AS NUMERIC(11,8)), 360)) * COS(RADIANS((rc0.wm_decl + x0.decl)/2))
                          * (MOD(CAST(rc0.wm_ra + 180 AS NUMERIC(11,8)), 360) - MOD(CAST(x0.ra + 180 AS NUMERIC(11,8)), 360)) * COS(RADIANS((rc0.wm_decl + x0.decl)/2))
                          / (x0.uncertainty_ew * x0.uncertainty_ew + rc0.wm_uncertainty_ew * rc0.wm_uncertainty_ew)
                          + (x0.decl - rc0.wm_decl) * (x0.decl - rc0.wm_decl)
                          / (x0.uncertainty_ns * x0.uncertainty_ns + rc0.wm_uncertainty_ns * rc0.wm_uncertainty_ns)
                         )
                      ELSE SQRT(  (rc0.wm_ra - x0.ra) * COS(RADIANS((rc0.wm_decl + x0.decl)/2))
                           * (rc0.wm_ra - x0.ra) * COS(RADIANS((rc0.wm_decl + x0.decl)/2))
                           / (x0.uncertainty_ew * x0.uncertainty_ew + rc0.wm_uncertainty_ew * rc0.wm_uncertainty_ew)
                           + (x0.decl - rc0.wm_decl) * (x0.decl - rc0.wm_decl)
                           / (x0.uncertainty_ns * x0.uncertainty_ns + rc0.wm_uncertainty_ns * rc0.wm_uncertainty_ns)
                          )
                 END < %(deRuiter)s
         ) t0
         LEFT OUTER JOIN runningcatalog_flux rf0
         ON t0.runcat = rf0.runcat
         AND t0.band = rf0.band
         AND t0.stokes = rf0.stokes
"""
    query = """\
INSERT INTO temprunningcatalog
  (runcat
  ,xtrsrc
  ,distance_arcsec
  ,r
  ,dataset
  ,band
  ,stokes
  ,datapoints
  ,zone
  ,wm_ra
  ,wm_decl
  ,wm_uncertainty_ew
  ,wm_uncertainty_ns
  ,avg_ra_err
  ,avg_decl_err
  ,avg_wra
  ,avg_wdecl
  ,avg_weight_ra
  ,avg_weight_decl
  ,x
  ,y
  ,z
  ,f_datapoints
  ,avg_f_peak
  ,avg_f_peak_sq
  ,avg_f_peak_weight
  ,avg_weighted_f_peak
  ,avg_weighted_f_peak_sq
  ,avg_f_int
  ,avg_f_int_sq
  ,avg_f_int_weight
  ,avg_weighted_f_int
  ,avg_weighted_f_int_sq
  )
  SELECT t0.runcat
        ,t0.xtrsrc
        ,t0.distance_arcsec
        ,t0.r
        ,t0.dataset
        ,t0.band
        ,t0.stokes
        ,t0.datapoints
        ,CAST(FLOOR(t0.wm_decl) AS INTEGER) AS zone
        ,t0.wm_ra
        ,t0.wm_decl
        ,t0.wm_uncertainty_ew
        ,t0.wm_uncertainty_ns
        ,t0.avg_ra_err
        ,t0.avg_decl_err
        ,t0.avg_wra
        ,t0.avg_wdecl
        ,t0.avg_weight_ra
        ,t0.avg_weight_decl
        ,COS(RADIANS(t0.wm_decl)) * COS(RADIANS(t0.wm_ra)) AS x
        ,COS(RADIANS(t0.wm_decl)) * SIN(RADIANS(t0.wm_ra)) AS y
        ,SIN(RADIANS(t0.wm_decl)) AS z
        ,CASE WHEN rf0.f_datapoints IS NULL
              THEN 1
              ELSE rf0.f_datapoints + 1
         END AS f_datapoints
        ,CASE WHEN rf0.f_datapoints IS NULL
              THEN t0.f_peak
              ELSE (rf0.f_datapoints * rf0.avg_f_peak
                    + t0.f_peak)
                   / (rf0.f_datapoints + 1)
         END AS avg_f_peak
        ,CASE WHEN rf0.f_datapoints IS NULL
              THEN t0.f_peak * t0.f_peak
              ELSE (rf0.f_datapoints * rf0.avg_f_peak_sq
                    + t0.f_peak * t0.f_peak)
                   / (rf0.f_datapoints + 1)
         END AS avg_f_peak_sq
        ,CASE WHEN rf0.f_datapoints IS NULL
              THEN 1 / (t0.f_peak_err * t0.f_peak_err)
              ELSE (rf0.f_datapoints * rf0.avg_f_peak_weight
                    + 1 / (t0.f_peak_err * t0.f_peak_err))
                   / (rf0.f_datapoints + 1)
         END AS avg_f_peak_weight
        ,CASE WHEN rf0.f_datapoints IS NULL
              THEN t0.f_peak / (t0.f_peak_err * t0.f_peak_err)
              ELSE (rf0.f_datapoints * rf0.avg_weighted_f_peak
                    + t0.f_peak / (t0.f_peak_err * t0.f_peak_err))
                   / (rf0.f_datapoints + 1)
         END AS avg_weighted_f_peak
        ,CASE WHEN rf0.f_datapoints IS NULL
              THEN t0.f_peak * t0.f_peak / (t0.f_peak_err * t0.f_peak_err)
              ELSE (rf0.f_datapoints * rf0.avg_weighted_f_peak_sq
                    + (t0.f_peak * t0.f_peak) / (t0.f_peak_err * t0.f_peak_err))
                   / (rf0.f_datapoints + 1)
         END AS avg_weighted_f_peak_sq
        ,CASE WHEN rf0.f_datapoints IS NULL
              THEN t0.f_int
              ELSE (rf0.f_datapoints * rf0.avg_f_int
                    + t0.f_int)
                   / (rf0.f_datapoints + 1)
         END AS avg_f_int
        ,CASE WHEN rf0.f_datapoints IS NULL
              THEN t0.f_int * t0.f_int
              ELSE (rf0.f_datapoints * rf0.avg_f_int_sq
                    + t0.f_int * t0.f_int)
                   / (rf0.f_datapoints + 1)
         END AS avg_f_int_sq
        ,CASE WHEN rf0.f_datapoints IS NULL
              THEN 1 / (t0.f_int_err * t0.f_int_err)
              ELSE (rf0.f_datapoints * rf0.avg_f_int_weight
                    + 1 / (t0.f_int_err * t0.f_int_err))
                   / (rf0.f_datapoints + 1)
         END AS avg_f_int_weight
        ,CASE WHEN rf0.f_datapoints IS NULL
              THEN t0.f_int / (t0.f_int_err * t0.f_int_err)
              ELSE (rf0.f_datapoints * rf0.avg_weighted_f_int
                    + t0.f_int / (t0.f_int_err * t0.f_int_err))
                   / (rf0.f_datapoints + 1)
         END AS avg_weighted_f_int
        ,CASE WHEN rf0.f_datapoints IS NULL
              THEN t0.f_int * t0.f_int / (t0.f_int_err * t0.f_int_err)
              ELSE (rf0.f_datapoints * rf0.avg_weighted_f_int_sq
                    + (t0.f_int * t0.f_int) / (t0.f_int_err * t0.f_int_err))
                   / (rf0.f_datapoints + 1)
         END AS avg_weighted_f_int_sq
    FROM (SELECT rc0.id as runcat
                ,x0.id as xtrsrc
                ,3600 * DEGREES(2 * ASIN(SQRT( (rc0.x - x0.x) * (rc0.x - x0.x)
                                             + (rc0.y - x0.y) * (rc0.y - x0.y)
                                             + (rc0.z - x0.z) * (rc0.z - x0.z)
                                             ) / 2)
                               ) AS distance_arcsec
                ,SQRT(  (rc0.wm_ra - x0.ra) * COS(RADIANS((rc0.wm_decl + x0.decl)/2))
                      * (rc0.wm_ra - x0.ra) * COS(RADIANS((rc0.wm_decl + x0.decl)/2))
                      / (rc0.wm_uncertainty_ew * rc0.wm_uncertainty_ew + x0.uncertainty_ew * x0.uncertainty_ew)
                     +  (rc0.wm_decl - x0.decl) * (rc0.wm_decl - x0.decl)
                      / (rc0.wm_uncertainty_ns * rc0.wm_uncertainty_ns + x0.uncertainty_ns * x0.uncertainty_ns)
                     ) AS r
                ,x0.f_peak
                ,x0.f_peak_err
                ,x0.f_int
                ,x0.f_int_err
                ,i0.dataset
                ,i0.band
                ,i0.stokes
                ,rc0.datapoints + 1 AS datapoints
                ,(datapoints * rc0.avg_wra + x0.ra /(x0.uncertainty_ew * x0.uncertainty_ew) )
                 /
                 (datapoints * rc0.avg_weight_ra + 1 / (x0.uncertainty_ew * x0.uncertainty_ew) )
                 AS wm_ra
                ,(datapoints * rc0.avg_wdecl + x0.decl /(x0.uncertainty_ns * x0.uncertainty_ns))
                 /
                 (datapoints * rc0.avg_weight_decl + 1 /(x0.uncertainty_ns * x0.uncertainty_ns))
                 AS wm_decl
                , SQRT(1 / ((datapoints + 1)
                           * ((datapoints * rc0.avg_weight_ra + 1 / (x0.uncertainty_ew * x0.uncertainty_ew))
                              / (datapoints + 1)
                             )
                           )
                      ) AS wm_uncertainty_ew
                , SQRT(1 / ((datapoints + 1)
                           * ((datapoints * rc0.avg_weight_decl + 1 / (x0.uncertainty_ns * x0.uncertainty_ns))
                              / (datapoints + 1)
                             )
                           )
                      ) AS wm_uncertainty_ns
                ,(datapoints * rc0.avg_ra_err + x0.ra_err) / (datapoints + 1) AS avg_ra_err
                ,(datapoints * rc0.avg_decl_err + x0.decl_err) / (datapoints + 1) AS avg_decl_err
                ,(datapoints * rc0.avg_wra + x0.ra / (x0.uncertainty_ew * x0.uncertainty_ew))
                 / (datapoints + 1) AS avg_wra
                ,(datapoints * rc0.avg_wdecl + x0.decl / (x0.uncertainty_ns * x0.uncertainty_ns))
                 / (datapoints + 1) AS avg_wdecl
                ,(datapoints * rc0.avg_weight_ra + 1 / (x0.uncertainty_ew * x0.uncertainty_ew))
                 / (datapoints + 1) AS avg_weight_ra
                ,(datapoints * rc0.avg_weight_decl + 1 / (x0.uncertainty_ns * x0.uncertainty_ns))
                 / (datapoints + 1) AS avg_weight_decl
            FROM extractedsource x0
                ,runningcatalog rc0
                ,image i0
           WHERE i0.id = %(image_id)s
             AND x0.image = i0.id
             AND x0.image = %(image_id)s
             AND i0.dataset = rc0.dataset
             AND rc0.mon_src = FALSE
             AND rc0.zone BETWEEN CAST(FLOOR(x0.decl - %(beamwidths_limit)s * i0.rb_smaj) AS INTEGER)
                              AND CAST(FLOOR(x0.decl + %(beamwidths_limit)s * i0.rb_smaj) AS INTEGER)
             AND rc0.wm_decl BETWEEN x0.decl - %(beamwidths_limit)s * i0.rb_smaj
                                 AND x0.decl + %(beamwidths_limit)s * i0.rb_smaj
             AND rc0.wm_ra BETWEEN x0.ra - alpha(%(beamwidths_limit)s * i0.rb_smaj, x0.decl)
                               AND x0.ra + alpha(%(beamwidths_limit)s * i0.rb_smaj, x0.decl)
             AND rc0.x * x0.x + rc0.y * x0.y + rc0.z * x0.z > COS(RADIANS(%(beamwidths_limit)s * i0.rb_smaj))
             AND SQRT(  (rc0.wm_ra - x0.ra) * COS(RADIANS((rc0.wm_decl + x0.decl)/2))
                      * (rc0.wm_ra - x0.ra) * COS(RADIANS((rc0.wm_decl + x0.decl)/2))
                      / (x0.uncertainty_ew * x0.uncertainty_ew + rc0.wm_uncertainty_ew * rc0.wm_uncertainty_ew)
                     + (x0.decl - rc0.wm_decl) * (x0.decl - rc0.wm_decl)
                      / (x0.uncertainty_ns * x0.uncertainty_ns + rc0.wm_uncertainty_ns * rc0.wm_uncertainty_ns)
                     ) < %(deRuiter)s
         ) t0
         LEFT OUTER JOIN runningcatalog_flux rf0
         ON t0.runcat = rf0.runcat
         AND t0.band = rf0.band
         AND t0.stokes = rf0.stokes
"""
    #mw = _check_meridian_wrap(conn, image_id)
    if meridian_wrap['q_across'] == True:
        logger.debug("Search across 0/360 meridian: %s" % meridian_wrap)
        query = q_across_ra0

    args = {'image_id': image_id, 'deRuiter': deRuiter_r,
            'beamwidths_limit' : beamwidths_limit}
    tkp.db.execute(query, args, commit=True)


def _flag_many_to_many_tempruncat():
    """Select the many-to-many association pairs in temprunningcatalog.

    By flagging the many-to-many associations, we reduce the
    processing to one-to-many and many-to-one (identical to one-to-one)
    relationships

    """

    # This one selects the farthest out of the many-to-many assocs
    query = """\
UPDATE temprunningcatalog
   SET inactive = TRUE
 WHERE EXISTS (SELECT runcat
                     ,xtrsrc
                 FROM (SELECT t1.runcat
                             ,t1.xtrsrc
                         FROM (SELECT xtrsrc
                                     ,MIN(r) as min_r
                                 FROM temprunningcatalog
                                WHERE runcat IN (SELECT runcat
                                                   FROM temprunningcatalog
                                                  WHERE runcat IN (SELECT runcat
                                                                     FROM temprunningcatalog
                                                                    WHERE xtrsrc IN (SELECT xtrsrc
                                                                                       FROM temprunningcatalog
                                                                                     GROUP BY xtrsrc
                                                                                     HAVING COUNT(*) > 1
                                                                                    )
                                                                  )
                                                 GROUP BY runcat
                                                 HAVING COUNT(*) > 1
                                                )
                                  AND xtrsrc IN (SELECT xtrsrc
                                                   FROM temprunningcatalog
                                                 GROUP BY xtrsrc
                                                 HAVING COUNT(*) > 1
                                                )
                               GROUP BY xtrsrc
                              ) t0
                             ,(SELECT runcat
                                     ,xtrsrc
                                     ,r
                                 FROM temprunningcatalog
                                WHERE runcat IN (SELECT runcat
                                                   FROM temprunningcatalog
                                                  WHERE runcat IN (SELECT runcat
                                                                     FROM temprunningcatalog
                                                                    WHERE xtrsrc IN (SELECT xtrsrc
                                                                                       FROM temprunningcatalog
                                                                                     GROUP BY xtrsrc
                                                                                     HAVING COUNT(*) > 1
                                                                                    )
                                                                  )
                                                 GROUP BY runcat
                                                 HAVING COUNT(*) > 1
                                                )
                                  AND xtrsrc IN (SELECT xtrsrc
                                                   FROM temprunningcatalog
                                                 GROUP BY xtrsrc
                                                 HAVING COUNT(*) > 1
                                                )
                              ) t1
                        WHERE t0.xtrsrc = t1.xtrsrc
                          AND t0.min_r < t1.r
                      ) t2
                WHERE t2.runcat = temprunningcatalog.runcat
                  AND t2.xtrsrc = temprunningcatalog.xtrsrc
              )
"""

    tkp.db.execute(query, commit=True)


def _insert_1_to_many_runcat():
    """Insert the extracted sources that belong to one-to-many
    associations in the runningcatalog.

    Since for the one-to-many associations (i.e. one runcat source
    associated with multiple extracted sources) we cannot a priori
    decide which counterpart pair is the correct one, or whether all
    are correct (in the case of a higher-resolution image),
    all extracted sources are added as a new source to
    the runningcatalog, and they will replace the (old; lower resolution)
    runcat source of the association.

    As a consequence of this, the resolution of the runningcatalog
    is increasing over time.

    """
    query = """\
INSERT INTO runningcatalog
  (xtrsrc
  ,dataset
  ,datapoints
  ,zone
  ,wm_ra
  ,wm_decl
  ,wm_uncertainty_ew
  ,wm_uncertainty_ns
  ,avg_ra_err
  ,avg_decl_err
  ,avg_wra
  ,avg_wdecl
  ,avg_weight_ra
  ,avg_weight_decl
  ,x
  ,y
  ,z
  )
  SELECT xtrsrc
        ,dataset
        ,datapoints
        ,zone
        ,wm_ra
        ,wm_decl
        ,wm_uncertainty_ew
        ,wm_uncertainty_ns
        ,avg_ra_err
        ,avg_decl_err
        ,avg_wra
        ,avg_wdecl
        ,avg_weight_ra
        ,avg_weight_decl
        ,x
        ,y
        ,z
    FROM (SELECT runcat
            FROM temprunningcatalog
           WHERE inactive = FALSE
          GROUP BY runcat
          HAVING COUNT(*) > 1
         ) one_to_many
        ,temprunningcatalog tmprc
   WHERE tmprc.runcat = one_to_many.runcat
     AND tmprc.inactive = FALSE
"""
    tkp.db.execute(query, commit=True)


def _insert_1_to_many_runcat_flux():
    """Insert the fluxes of the extracted sources that belong
    to a one-to-many association in the runningcatalog.

    Analogous to the runningcatalog, extracted source properties
    are added to the runningcatalog_flux table.
    """

    # NB we pull the new runcat id from the runningcatalog by matching with
    # temprunningcatalog via xtrsrc. (temprunningcatalog.runcat points at old
    # runcat entries).

    query = """\
INSERT INTO runningcatalog_flux
  (runcat
  ,band
  ,stokes
  ,f_datapoints
  ,avg_f_peak
  ,avg_f_peak_sq
  ,avg_f_peak_weight
  ,avg_weighted_f_peak
  ,avg_weighted_f_peak_sq
  ,avg_f_int
  ,avg_f_int_sq
  ,avg_f_int_weight
  ,avg_weighted_f_int
  ,avg_weighted_f_int_sq
  )
  SELECT r.id
        ,tmprc.band
        ,tmprc.stokes
        ,tmprc.f_datapoints
        ,avg_f_peak
        ,avg_f_peak_sq
        ,avg_f_peak_weight
        ,avg_weighted_f_peak
        ,avg_weighted_f_peak_sq
        ,avg_f_int
        ,avg_f_int_sq
        ,avg_f_int_weight
        ,avg_weighted_f_int
        ,avg_weighted_f_int_sq
    FROM (SELECT runcat
            FROM temprunningcatalog
           WHERE inactive = FALSE
          GROUP BY runcat
          HAVING COUNT(*) > 1
         ) one_to_many
        ,temprunningcatalog tmprc
        ,runningcatalog r
   WHERE tmprc.runcat = one_to_many.runcat
     AND tmprc.inactive = FALSE
     AND r.xtrsrc = tmprc.xtrsrc
"""
    tkp.db.execute(query, commit=True)


def _insert_1_to_many_basepoint_assocxtrsource():
    """Insert 'base points' for one-to-many associations

    Before continuing, we have to insert the 'base points' of the associations,
    i.e. the links between the new runningcatalog entries
    and their associated (new) extractedsources.

    We also calculate the variability indices at the timestamp of the
    the current image.
    """

    # NB we pull the new runcat id from the runningcatalog by matching with
    # temprunningcatalog via xtrsrc. (temprunningcatalog.runcat points at old
    # runcat entries).

    query = """\
INSERT INTO assocxtrsource
  (runcat
  ,xtrsrc
  ,type
  ,distance_arcsec
  ,r
  ,v_int
  ,eta_int
  ,f_datapoints
  )
  SELECT t0.new_runcat_id
        ,t0.xtrsrc
        ,2
        ,t0.distance_arcsec
        ,t0.r
        ,t0.v_int_inter / t0.avg_f_int
        ,t0.eta_int_inter / t0.avg_f_int_weight
        ,t0.f_datapoints
    FROM (SELECT runcat.id AS new_runcat_id
                ,tmprc.xtrsrc
                ,tmprc.distance_arcsec
                ,tmprc.r
                ,tmprc.f_datapoints
                ,CASE WHEN tmprc.avg_f_int = 0.0
                      THEN 0.000001
                      ELSE avg_f_int
                 END AS avg_f_int
                ,tmprc.avg_f_int_weight
                ,CASE WHEN tmprc.f_datapoints = 1
                      THEN 0
                      ELSE CASE WHEN ABS(tmprc.avg_f_int_sq - tmprc.avg_f_int * tmprc.avg_f_int) < 8e-14
                                THEN 0
                                ELSE SQRT(CAST(tmprc.f_datapoints AS DOUBLE PRECISION)
                                         * (tmprc.avg_f_int_sq - tmprc.avg_f_int * tmprc.avg_f_int)
                                         / (CAST(tmprc.f_datapoints AS DOUBLE PRECISION) - 1.0)
                                         )
                           END
                 END AS v_int_inter
                ,CASE WHEN tmprc.f_datapoints = 1
                      THEN 0
                      ELSE (CAST(tmprc.f_datapoints AS DOUBLE PRECISION) /
                              (CAST(tmprc.f_datapoints AS DOUBLE PRECISION) - 1.0))
                           * (tmprc.avg_f_int_weight * tmprc.avg_weighted_f_int_sq -
                                  tmprc.avg_weighted_f_int * tmprc.avg_weighted_f_int)
                 END AS eta_int_inter
            FROM (SELECT runcat as old_runcat_id
                    FROM temprunningcatalog
                   WHERE inactive = FALSE
                  GROUP BY runcat
                  HAVING COUNT(*) > 1
                 ) one_to_many
                ,temprunningcatalog tmprc
                ,runningcatalog runcat
           WHERE tmprc.runcat = one_to_many.old_runcat_id
             AND tmprc.inactive = FALSE
             AND runcat.xtrsrc = tmprc.xtrsrc
         ) t0
    """
    tkp.db.execute(query, commit=True)


def _insert_1_to_many_replacement_assocxtrsource():
    """Insert links into the association table between the new runcat
    entries and the old extractedsources.
    (New to New ('basepoint') links have been added earlier).

    In this case, new entries in the runningcatalog and runningcatalog_flux
    were already added (for every extractedsource one), which will replace
    the existing ones in the runningcatalog.
    Therefore, we have to update the references to these new ids as well.
    So, we will append to assocxtrsource and delete the entries from
    runningcatalog_flux.

    NOTE:
    1. We do not update the distance_arcsec and r values of the pairs.

    TODO:
    1. Why not?

    """


    # NB we pull the new runcat id from the runningcatalog by matching with
    # temprunningcatalog via xtrsrc. (temprunningcatalog.runcat points at old
    # runcat entries).

    query = """\
INSERT INTO assocxtrsource
  (runcat
  ,xtrsrc
  ,type
  ,distance_arcsec
  ,r
  ,v_int
  ,eta_int
  ,f_datapoints
  )
  SELECT r.id AS new_runcat_id
        ,a.xtrsrc
        ,6
        ,a.distance_arcsec
        ,a.r
        ,a.v_int
        ,a.eta_int
        ,a.f_datapoints
    FROM (SELECT runcat as old_runcat_id
            FROM temprunningcatalog
           WHERE inactive = FALSE
          GROUP BY runcat
          HAVING COUNT(*) > 1
         ) one_to_many
        ,temprunningcatalog tmprc
        ,runningcatalog r
        ,assocxtrsource a
   WHERE tmprc.runcat = one_to_many.old_runcat_id
     AND tmprc.inactive = FALSE
     AND r.xtrsrc = tmprc.xtrsrc
     AND a.runcat = tmprc.runcat
"""
    tkp.db.execute(query, commit=True)


def _insert_1_to_many_assocskyrgn():
    """
    Copy skyregion associations from old runcat entries for new one-to-many
    runningcatalog entries.
    """
    # NB we pull the new runcat id from the runningcatalog by matching with
    # temprunningcatalog via xtrsrc. (temprunningcatalog.runcat points at old
    # runcat entries).

    query = """\
INSERT INTO assocskyrgn
  (runcat
  ,skyrgn
  ,distance_deg
  )
  SELECT r.id AS new_runcat_id
        ,a.skyrgn
        ,a.distance_deg
    FROM (SELECT runcat as old_runcat_id
            FROM temprunningcatalog
           WHERE inactive = FALSE
          GROUP BY runcat
          HAVING COUNT(*) > 1
         ) one_to_many
        ,temprunningcatalog tmprc
        ,runningcatalog r
        ,assocskyrgn a
   WHERE tmprc.runcat = one_to_many.old_runcat_id
     AND tmprc.inactive = FALSE
     AND r.xtrsrc = tmprc.xtrsrc
     AND a.runcat = tmprc.runcat
"""
    tkp.db.execute(query, commit=True)


def _insert_1_to_many_newsource():
    """Update the runcat id for the one-to-many associations,
    and delete the newsource entries of the old runcat id
    (the new ones have been added earlier).

    In this case, new entries in the runningcatalog and runningcatalog_flux
    were already added (for every extractedsource one), which will replace
    the existing ones in the runningcatalog.
    Therefore, we have to update the references to these new ids as well.
    """
    query = """\
INSERT INTO newsource
  (runcat
  ,trigger_xtrsrc
  ,newsource_type
  ,previous_limits_image
  )
  SELECT r.id as new_runcat_id
        ,tr.trigger_xtrsrc
        ,tr.newsource_type
        ,tr.previous_limits_image
    FROM (SELECT runcat as old_runcat_id
            FROM temprunningcatalog
           WHERE inactive = FALSE
          GROUP BY runcat
          HAVING COUNT(*) > 1
         ) one_to_many
        ,temprunningcatalog tmprc
        ,runningcatalog r
        ,newsource tr
   WHERE tmprc.runcat = one_to_many.old_runcat_id
     AND tmprc.inactive = FALSE
     AND tr.runcat = one_to_many.old_runcat_id
     AND r.xtrsrc = tmprc.xtrsrc
"""
    tkp.db.execute(query, commit=True)


def _delete_1_to_many_inactive_assocskyrgn():
    """Delete the assocskyrgn links of the old runcat

    Since we replaced this runcat.id with multiple new ones, we now
    delete the old links.
    """
    query = """\
DELETE
    FROM assocskyrgn
    WHERE runcat IN (SELECT runcat
                       FROM temprunningcatalog
                       WHERE inactive = FALSE
                       GROUP BY runcat
                       HAVING COUNT(*) > 1
                    )
"""
    tkp.db.execute(query, commit=True)


def _delete_1_to_many_inactive_newsource():
    """Delete the newsource sources of the old runcat

    Since we replaced this runcat.id with multiple new ones, we now
    delete the old one.
    """
    query = """\
DELETE
    FROM newsource
    WHERE runcat IN (SELECT runcat
                       FROM temprunningcatalog
                       WHERE inactive = FALSE
                       GROUP BY runcat
                       HAVING COUNT(*) > 1
                    )
"""
    tkp.db.execute(query, commit=True)


def _delete_1_to_many_inactive_assocxtrsource():
    """Delete the association pairs of the old runcat from assocxtrsource

    NOTE: It might sound confusing, but those are not qualified
    as inactive in tempruncat (read below).
    Since we replaced this runcat.id with multiple new one, we first
    flag it as inactive, after which we delete it from the runningcatalog

    The subselect selects those valid "old" runcat ids (i.e.,
    the ones that were not set to inactive for the many-to-many associations).

    NOTE: We do not have to flag these rows as inactive,
          no furthr processing depends on these in the assoc run
    """

    #NB temprunningcatalog 'runcat' field still refers to old,
    #superceded runcat entries.
    query = """\
DELETE
    FROM assocxtrsource
    WHERE runcat IN (SELECT runcat
                   FROM temprunningcatalog
                   WHERE inactive = FALSE
                   GROUP BY runcat
                   HAVING COUNT(*) > 1
                )
    """
    tkp.db.execute(query, commit=True)


def _delete_1_to_many_inactive_runcat_flux():
    """Flag the old runcat ids in the runningcatalog to inactive

    Since we replaced this runcat.id with multiple new one, we first
    flag it as inactive, after which we delete it from the runningcatalog

    """
    query = """\
DELETE
    FROM runningcatalog_flux
    WHERE runcat IN (SELECT runcat
                   FROM temprunningcatalog
                   WHERE inactive = FALSE
                   GROUP BY runcat
                   HAVING COUNT(*) > 1
                )
"""
    tkp.db.execute(query, commit=True)


def _flag_1_to_many_inactive_runcat():
    """Flag the old runcat ids in the runningcatalog to inactive

    We do not delete them yet, because we still need to clear up all the
    superseded entries in assocskyrgn, etc.
    """
    query = """\
UPDATE runningcatalog
   SET inactive = TRUE
 WHERE id IN (SELECT runcat
                FROM temprunningcatalog
               WHERE inactive = FALSE
              GROUP BY runcat
              HAVING COUNT(*) > 1
             )
"""
    tkp.db.execute(query, commit=True)


def _flag_1_to_many_inactive_tempruncat():
    """
    Flag the one-to-many associations from temprunningcatalog.

    (Since we are done processing them, now.)

    We do not delete them yet- if we did,
    we would not be able to cross-match extractedsources to determine
    which sources did not have a match in temprunningcatalog ('new' sources).

    """
    query = """\
UPDATE temprunningcatalog
   SET inactive = TRUE
 WHERE runcat IN (SELECT runcat
                    FROM temprunningcatalog
                   WHERE inactive = FALSE
                  GROUP BY runcat
                  HAVING COUNT(*) > 1
                 )
"""
    tkp.db.execute(query, commit=True)


# This is the "master" 1-to-1 association query. We reuse it for associating
# both null detections and monitoring list sources, tweaking the type as
# appropriate.
ONE_TO_ONE_ASSOC_QUERY = """\
INSERT INTO assocxtrsource
  (runcat
  ,xtrsrc
  ,type
  ,distance_arcsec
  ,r
  ,v_int
  ,eta_int
  ,f_datapoints
  )
  SELECT t0.runcat
        ,t0.xtrsrc
        ,%(type)s
        ,t0.distance_arcsec
        ,t0.r
        ,t0.v_int_inter / t0.avg_f_int
        ,t0.eta_int_inter / t0.avg_f_int_weight
        ,t0.f_datapoints
    FROM (SELECT tmprc.runcat
                ,tmprc.xtrsrc
                ,tmprc.distance_arcsec
                ,tmprc.r
                ,tmprc.f_datapoints
                ,CASE WHEN tmprc.avg_f_int = 0.0
                      THEN 0.000001
                      ELSE avg_f_int
                 END AS avg_f_int
                ,tmprc.avg_f_int_weight
                ,CASE WHEN tmprc.f_datapoints = 1
                      THEN 0
                      ELSE CASE WHEN ABS(tmprc.avg_f_int_sq - tmprc.avg_f_int * tmprc.avg_f_int) < 8e-14
                                THEN 0
                                ELSE SQRT(CAST(tmprc.f_datapoints AS DOUBLE PRECISION)
                                         * (tmprc.avg_f_int_sq - tmprc.avg_f_int * tmprc.avg_f_int)
                                         / (CAST(tmprc.f_datapoints AS DOUBLE PRECISION) - 1.0)
                                         )
                           END
                 END AS v_int_inter
                ,CASE WHEN tmprc.f_datapoints = 1
                      THEN 0
                      ELSE (CAST(tmprc.f_datapoints AS DOUBLE PRECISION)
                            / (CAST(tmprc.f_datapoints AS DOUBLE PRECISION) - 1.0))
                           * (tmprc.avg_f_int_weight * tmprc.avg_weighted_f_int_sq
                             - tmprc.avg_weighted_f_int * tmprc.avg_weighted_f_int)
                 END AS eta_int_inter
            FROM temprunningcatalog tmprc
           WHERE tmprc.inactive = FALSE
           ) t0
"""

def _insert_1_to_1_assoc():
    """
    Insert remaining associations from temprunningcatalog into assocxtrsource.

    We also calculate the variability indices at the timestamp of the
    the current image.
    """
    tkp.db.execute(ONE_TO_ONE_ASSOC_QUERY, {'type': 3}, commit=True)


def _update_1_to_1_runcat():
    """Update the running catalog with the values in temprunningcatalog"""
    query = """\
        UPDATE runningcatalog
           SET datapoints = (SELECT datapoints
                               FROM temprunningcatalog
                              WHERE temprunningcatalog.runcat = runningcatalog.id
                          AND temprunningcatalog.inactive = FALSE
                            )
              ,zone = (SELECT zone
                         FROM temprunningcatalog
                        WHERE temprunningcatalog.runcat = runningcatalog.id
                          AND temprunningcatalog.inactive = FALSE
                      )
              ,wm_ra = (SELECT wm_ra
                          FROM temprunningcatalog
                         WHERE temprunningcatalog.runcat = runningcatalog.id
                          AND temprunningcatalog.inactive = FALSE
                       )
              ,wm_decl = (SELECT wm_decl
                            FROM temprunningcatalog
                           WHERE temprunningcatalog.runcat = runningcatalog.id
                          AND temprunningcatalog.inactive = FALSE
                         )
              ,avg_ra_err = (SELECT avg_ra_err
                              FROM temprunningcatalog
                             WHERE temprunningcatalog.runcat = runningcatalog.id
                          AND temprunningcatalog.inactive = FALSE
                           )
              ,avg_decl_err = (SELECT avg_decl_err
                                FROM temprunningcatalog
                               WHERE temprunningcatalog.runcat = runningcatalog.id
                          AND temprunningcatalog.inactive = FALSE
                             )
              ,wm_uncertainty_ew = (SELECT wm_uncertainty_ew
                                FROM temprunningcatalog
                               WHERE temprunningcatalog.runcat = runningcatalog.id
                          AND temprunningcatalog.inactive = FALSE
                             )
              ,wm_uncertainty_ns = (SELECT wm_uncertainty_ns
                                FROM temprunningcatalog
                               WHERE temprunningcatalog.runcat = runningcatalog.id
                          AND temprunningcatalog.inactive = FALSE
                             )
              ,avg_wra = (SELECT avg_wra
                            FROM temprunningcatalog
                           WHERE temprunningcatalog.runcat = runningcatalog.id
                          AND temprunningcatalog.inactive = FALSE
                         )
              ,avg_wdecl = (SELECT avg_wdecl
                              FROM temprunningcatalog
                             WHERE temprunningcatalog.runcat = runningcatalog.id
                          AND temprunningcatalog.inactive = FALSE
                           )
              ,avg_weight_ra = (SELECT avg_weight_ra
                                  FROM temprunningcatalog
                                 WHERE temprunningcatalog.runcat = runningcatalog.id
                          AND temprunningcatalog.inactive = FALSE
                               )
              ,avg_weight_decl = (SELECT avg_weight_decl
                                    FROM temprunningcatalog
                                   WHERE temprunningcatalog.runcat = runningcatalog.id
                          AND temprunningcatalog.inactive = FALSE
                                 )
              ,x = (SELECT x
                      FROM temprunningcatalog
                     WHERE temprunningcatalog.runcat = runningcatalog.id
                          AND temprunningcatalog.inactive = FALSE
                   )
              ,y = (SELECT y
                      FROM temprunningcatalog
                     WHERE temprunningcatalog.runcat = runningcatalog.id
                          AND temprunningcatalog.inactive = FALSE
                   )
              ,z = (SELECT z
                      FROM temprunningcatalog
                     WHERE temprunningcatalog.runcat = runningcatalog.id
                          AND temprunningcatalog.inactive = FALSE
                   )
              ,forcedfits_count = 0
         WHERE EXISTS (SELECT runcat
                         FROM temprunningcatalog
                        WHERE temprunningcatalog.runcat = runningcatalog.id
                          AND temprunningcatalog.inactive = FALSE
                      )
"""
    tkp.db.execute(query, commit=True)

def _update_1_to_1_runcat_flux():
    """Updates the fluxes in runningcatalog_flux of an existing band
    for an existing runcat source.

    If the runcat, band, stokes entry does exist in runcat_flux,
    it will be updated with the values from tempruncat.
    """
    query = """\
UPDATE runningcatalog_flux
   SET f_datapoints = (SELECT f_datapoints
                         FROM temprunningcatalog
                        WHERE temprunningcatalog.runcat = runningcatalog_flux.runcat
                          AND temprunningcatalog.band = runningcatalog_flux.band
                          AND temprunningcatalog.stokes = runningcatalog_flux.stokes
                          AND temprunningcatalog.inactive = FALSE
                      )
      ,avg_f_peak = (SELECT avg_f_peak
                       FROM temprunningcatalog
                      WHERE temprunningcatalog.runcat = runningcatalog_flux.runcat
                        AND temprunningcatalog.band = runningcatalog_flux.band
                        AND temprunningcatalog.stokes = runningcatalog_flux.stokes
                        AND temprunningcatalog.inactive = FALSE
                    )
      ,avg_f_peak_sq = (SELECT avg_f_peak_sq
                          FROM temprunningcatalog
                         WHERE temprunningcatalog.runcat = runningcatalog_flux.runcat
                           AND temprunningcatalog.band = runningcatalog_flux.band
                           AND temprunningcatalog.stokes = runningcatalog_flux.stokes
                           AND temprunningcatalog.inactive = FALSE
                       )
      ,avg_f_peak_weight = (SELECT avg_f_peak_weight
                              FROM temprunningcatalog
                             WHERE temprunningcatalog.runcat = runningcatalog_flux.runcat
                               AND temprunningcatalog.band = runningcatalog_flux.band
                               AND temprunningcatalog.stokes = runningcatalog_flux.stokes
                               AND temprunningcatalog.inactive = FALSE
                           )
      ,avg_weighted_f_peak = (SELECT avg_weighted_f_peak
                                FROM temprunningcatalog
                               WHERE temprunningcatalog.runcat = runningcatalog_flux.runcat
                                 AND temprunningcatalog.band = runningcatalog_flux.band
                                 AND temprunningcatalog.stokes = runningcatalog_flux.stokes
                                 AND temprunningcatalog.inactive = FALSE
                             )
      ,avg_weighted_f_peak_sq = (SELECT avg_weighted_f_peak_sq
                                   FROM temprunningcatalog
                                  WHERE temprunningcatalog.runcat = runningcatalog_flux.runcat
                                    AND temprunningcatalog.band = runningcatalog_flux.band
                                    AND temprunningcatalog.stokes = runningcatalog_flux.stokes
                                    AND temprunningcatalog.inactive = FALSE
                                )
      ,avg_f_int = (SELECT avg_f_int
                      FROM temprunningcatalog
                     WHERE temprunningcatalog.runcat = runningcatalog_flux.runcat
                       AND temprunningcatalog.band = runningcatalog_flux.band
                       AND temprunningcatalog.stokes = runningcatalog_flux.stokes
                       AND temprunningcatalog.inactive = FALSE
                   )
      ,avg_f_int_sq = (SELECT avg_f_int_sq
                         FROM temprunningcatalog
                        WHERE temprunningcatalog.runcat = runningcatalog_flux.runcat
                          AND temprunningcatalog.band = runningcatalog_flux.band
                          AND temprunningcatalog.stokes = runningcatalog_flux.stokes
                          AND temprunningcatalog.inactive = FALSE
                      )
      ,avg_f_int_weight = (SELECT avg_f_int_weight
                             FROM temprunningcatalog
                             WHERE temprunningcatalog.runcat = runningcatalog_flux.runcat
                               AND temprunningcatalog.band = runningcatalog_flux.band
                               AND temprunningcatalog.stokes = runningcatalog_flux.stokes
                               AND temprunningcatalog.inactive = FALSE
                          )
      ,avg_weighted_f_int = (SELECT avg_weighted_f_int
                               FROM temprunningcatalog
                              WHERE temprunningcatalog.runcat = runningcatalog_flux.runcat
                                AND temprunningcatalog.band = runningcatalog_flux.band
                                AND temprunningcatalog.stokes = runningcatalog_flux.stokes
                                AND temprunningcatalog.inactive = FALSE
                            )
      ,avg_weighted_f_int_sq = (SELECT avg_weighted_f_int_sq
                                  FROM temprunningcatalog
                                 WHERE temprunningcatalog.runcat = runningcatalog_flux.runcat
                                   AND temprunningcatalog.band = runningcatalog_flux.band
                                   AND temprunningcatalog.stokes = runningcatalog_flux.stokes
                                   AND temprunningcatalog.inactive = FALSE
                               )
 WHERE EXISTS (SELECT runcat
                 FROM temprunningcatalog
                WHERE temprunningcatalog.runcat = runningcatalog_flux.runcat
                  AND temprunningcatalog.band = runningcatalog_flux.band
                  AND temprunningcatalog.stokes = runningcatalog_flux.stokes
                  AND temprunningcatalog.inactive = FALSE
                  AND temprunningcatalog.f_datapoints > 1
              )
"""
    cursor = tkp.db.execute(query, commit=True)
    return cursor.rowcount



def _insert_1_to_1_runcat_flux():
    """Insert the fluxes in runningcatalog_flux of a new band
    for an existing runcat source.

    If the runcat, band, stokes entry does not exist (yet) in runcat_flux,
    we need to insert the new values from tempruncat.
    This might be the case if a source has been observed at other frequencies,
    but not in the current band, so there does not exist an entry
    for this band.

    """

    query = """\
INSERT INTO runningcatalog_flux
  (runcat
  ,band
  ,stokes
  ,f_datapoints
  ,avg_f_peak
  ,avg_f_peak_sq
  ,avg_f_peak_weight
  ,avg_weighted_f_peak
  ,avg_weighted_f_peak_sq
  ,avg_f_int
  ,avg_f_int_sq
  ,avg_f_int_weight
  ,avg_weighted_f_int
  ,avg_weighted_f_int_sq
  )
  SELECT runcat
        ,band
        ,stokes
        ,f_datapoints
        ,avg_f_peak
        ,avg_f_peak_sq
        ,avg_f_peak_weight
        ,avg_weighted_f_peak
        ,avg_weighted_f_peak_sq
        ,avg_f_int
        ,avg_f_int_sq
        ,avg_f_int_weight
        ,avg_weighted_f_int
        ,avg_weighted_f_int_sq
    FROM temprunningcatalog
   WHERE inactive = FALSE
     AND f_datapoints=1
"""
    cursor = tkp.db.execute(query, commit=True)
    return cursor.rowcount



def _insert_new_runcat(image_id):
    """Insert previously unknown sources into the ``runningcatalog`` table.

    Extractedsources for which no counterpart was found in the
    runningcatalog (i.e. no pair exists in tempruncat),
    will be added as a new source to the assocxtrsource,
    runningcatalog and runningcatalog_flux tables.

    """

    # NOTE: Here we select all (inactive TRUE&FALSE) tempruncat entries
    # source in order to exclude all extractedsources that have been associated.
    query = """\
INSERT INTO runningcatalog
  (xtrsrc
  ,dataset
  ,datapoints
  ,zone
  ,wm_ra
  ,wm_decl
  ,avg_ra_err
  ,avg_decl_err
  ,wm_uncertainty_ew
  ,wm_uncertainty_ns
  ,avg_wra
  ,avg_wdecl
  ,avg_weight_ra
  ,avg_weight_decl
  ,x
  ,y
  ,z
  )
  SELECT new_src.xtrsrc
        ,new_src.dataset
        ,new_src.datapoints
        ,new_src.zone
        ,new_src.wm_ra
        ,new_src.wm_decl
        ,new_src.avg_ra_err
        ,new_src.avg_decl_err
        ,new_src.wm_uncertainty_ew
        ,new_src.wm_uncertainty_ns
        ,new_src.avg_wra
        ,new_src.avg_wdecl
        ,new_src.avg_weight_ra
        ,new_src.avg_weight_decl
        ,new_src.x
        ,new_src.y
        ,new_src.z
    FROM (SELECT x0.id AS xtrsrc
                ,i0.dataset
                ,1 AS datapoints
                ,x0.zone
                ,x0.ra AS wm_ra
                ,x0.decl AS wm_decl
                ,x0.ra_err AS avg_ra_err
                ,x0.decl_err AS avg_decl_err
                ,x0.uncertainty_ew AS wm_uncertainty_ew
                ,x0.uncertainty_ns AS wm_uncertainty_ns
                ,x0.ra / (x0.uncertainty_ew * x0.uncertainty_ew) AS avg_wra
                ,x0.decl / (x0.uncertainty_ns * x0.uncertainty_ns) AS avg_wdecl
                ,1 / (x0.uncertainty_ew * x0.uncertainty_ew) AS avg_weight_ra
                ,1 / (x0.uncertainty_ns * x0.uncertainty_ns) AS avg_weight_decl
                ,x0.x
                ,x0.y
                ,x0.z
            FROM extractedsource x0
                ,image i0
           WHERE x0.image = i0.id
             AND x0.image = %s
             AND x0.extract_type = 0
         ) new_src
         LEFT OUTER JOIN temprunningcatalog tmprc
         ON new_src.xtrsrc = tmprc.xtrsrc
   WHERE tmprc.xtrsrc IS NULL
"""
    cursor = tkp.db.execute(query, (image_id,), True)
    ins = cursor.rowcount
    if ins > 0:
        logger.debug("Added %s new sources to runningcatalog" % ins)



def _insert_new_runcat_flux(image_id):
    """
	Insert previously unknown sources into the ``runningcatalog_flux`` table.

	(i.e. those without *any* previous runcat-counterpart)
    """
    query = """\
INSERT INTO runningcatalog_flux
  (runcat
  ,band
  ,stokes
  ,f_datapoints
  ,avg_f_peak
  ,avg_f_peak_sq
  ,avg_f_peak_weight
  ,avg_weighted_f_peak
  ,avg_weighted_f_peak_sq
  ,avg_f_int
  ,avg_f_int_sq
  ,avg_f_int_weight
  ,avg_weighted_f_int
  ,avg_weighted_f_int_sq
  )
  SELECT r0.id
        ,i0.band
        ,i0.stokes
        ,1 AS f_datapoints
        ,x0.f_peak
        ,x0.f_peak * x0.f_peak
        ,1 / (x0.f_peak_err * x0.f_peak_err)
        ,x0.f_peak / (x0.f_peak_err * x0.f_peak_err)
        ,x0.f_peak * x0.f_peak / (x0.f_peak_err * x0.f_peak_err)
        ,x0.f_int
        ,x0.f_int * x0.f_int
        ,1 / (x0.f_int_err * x0.f_int_err)
        ,x0.f_int / (x0.f_int_err * x0.f_int_err)
        ,x0.f_int * x0.f_int / (x0.f_int_err * x0.f_int_err)
    FROM image i0
        ,(SELECT x1.id AS xtrsrc
            FROM extractedsource x1
                 LEFT OUTER JOIN temprunningcatalog tmprc
                 ON x1.id = tmprc.xtrsrc
            WHERE x1.image = %(image_id)s
              AND x1.extract_type = 0
              AND tmprc.xtrsrc IS NULL
          ) new_src
        ,runningcatalog r0
        ,extractedsource x0
   WHERE i0.id = %(image_id)s
     AND r0.xtrsrc = new_src.xtrsrc
     AND x0.id = r0.xtrsrc
"""
    tkp.db.execute(query, {'image_id': image_id}, True)


def _insert_new_runcat_skyrgn_assocs(image_id):
    """
    Process newly created entries from the runningcatalog,
    determine which skyregions they lie within.

    Upon creation of a new runningcatalog entry,
    we need to determine which previous fields of view (skyrgns)
    we expect to see it in.
    This knowledge helps us to make accurate guesses as whether a new
    source is really transient or simply being surveyed for the first time.

    .. note:

        This could be made more efficient, at the cost of added complexity,
        by tracking which skyregions overlap,
        and then only testing for membership of overlapping regions.

    """

    # First, mark membership in the skyregion of the image of initial detection.
    # We look for extracted sources from this image
    # that are not in temprunningcatalog, i.e. have no association candidates.

    # By dealing with these separately, we save a number of radius comparison
    # operations proportional to the number of new sources in this field.
    assocskyrgn_parent_qry = """\
INSERT INTO assocskyrgn
    (runcat
    ,skyrgn
    )
SELECT t0.runcat
      ,t0.skyrgn
  FROM (SELECT ex.id AS xtrsrc
              ,rc.id as runcat
              ,im.skyrgn
          FROM extractedsource ex
              ,runningcatalog rc
              ,image im
         WHERE ex.image = %(img_id)s
           AND rc.xtrsrc = ex.id
           AND ex.image = im.id
       ) t0
       LEFT OUTER JOIN temprunningcatalog tmprc
       ON t0.xtrsrc = tmprc.xtrsrc
WHERE tmprc.xtrsrc IS NULL
"""
    tkp.db.execute(assocskyrgn_parent_qry, {'img_id':image_id}, True)

    #Now search all the other skyregions *in same dataset* to determine matches:
    assocskyrgn_others_qry = """\
INSERT INTO assocskyrgn
    (runcat
    ,skyrgn
    ,distance_deg
    )
SELECT new_src.runcat as runcatid
      ,sky.id as skyrgnid
      ,DEGREES(2 * ASIN(SQRT( (rc1.x - sky.x) * (rc1.x - sky.x)
                         + (rc1.y - sky.y) * (rc1.y - sky.y)
                         + (rc1.z - sky.z) * (rc1.z - sky.z)
                         ) / 2)
           ) AS idistance_deg
  FROM skyregion sky
       ,runningcatalog rc1
      ,(SELECT t0.runcat
              ,t0.self_skyrgn
          FROM (SELECT ex.id AS xtrsrc
                      ,rc0.id as runcat
                      ,im.skyrgn as self_skyrgn
                  FROM extractedsource ex
                      ,runningcatalog rc0
                      ,image im
                 WHERE ex.image = %(img_id)s
                   AND rc0.xtrsrc = ex.id
                   AND ex.image = im.id
               ) t0
               LEFT OUTER JOIN temprunningcatalog tmprc
               ON t0.xtrsrc = tmprc.xtrsrc
        WHERE tmprc.xtrsrc IS NULL
        ) new_src
    WHERE rc1.id = new_src.runcat
      AND sky.dataset = rc1.dataset
      AND sky.id <> new_src.self_skyrgn
      AND  DEGREES(2 * ASIN(SQRT( (rc1.x - sky.x) * (rc1.x - sky.x)
                                     + (rc1.y - sky.y) * (rc1.y - sky.y)
                                     + (rc1.z - sky.z) * (rc1.z - sky.z)
                                    ) / 2)
               ) < sky.xtr_radius
"""
    tkp.db.execute(assocskyrgn_others_qry, {'img_id':image_id}, True)


def _insert_new_assocxtrsource(image_id):
    """
    Insert new associations for previously unknown sources.
    """

    query = """\
INSERT INTO assocxtrsource
  (runcat
  ,xtrsrc
  ,type
  ,distance_arcsec
  ,r
  ,v_int
  ,eta_int
  ,f_datapoints
  )
  SELECT r0.id AS runcat
        ,r0.xtrsrc
        ,4
        ,0
        ,0
        ,0
        ,0
        ,1
    FROM (SELECT x1.id AS xtrsrc
            FROM extractedsource x1
                 LEFT OUTER JOIN temprunningcatalog tmprc
                 ON x1.id = tmprc.xtrsrc
            WHERE x1.image = %(image_id)s
              AND x1.extract_type = 0
              AND tmprc.xtrsrc IS NULL
          ) new_src
        ,runningcatalog r0
   WHERE r0.xtrsrc = new_src.xtrsrc
"""
    tkp.db.execute(query, {'image_id':image_id}, True)

def _determine_newsource_previous_limits(image_id, new_source_sigma_margin):
    """
    Determines which new-runcat sources are also probably transient.

    Looks up previous images relevant to this source-position, using the
    following criteria - images must:

     - overlap the new-source position, according to the skyregion
       information;
     - be in the same dataset;
     - be in the same frequency band;
     - have an earlier timestamp than the current image;
     - have not been rejected.

    For those images we calculate the per-previous-image detection-thresholds,
    which are defined as follows.

    A new source is 'possibly transient' (type 0) if it
    passes the following tests:

     - Was not detected in a skyregion being surveyed for the first time.
     - Has a flux-value such that:

        flux > MIN_OVER_I [ (rms_min_I*(det_I + new_source_sigma_margin) ]

      (where I indexes the images)
      i.e. if it was a steady-source, it should have been already detected if
      it was in the *low-RMS* area of the previous image with best detection
      threshold, even allowing for noise fluctuations.

    Furthermore, a new source is 'likely transient' (type 1) if it is additionally
    bright enough that, if it were a steady source, it should have been detected
    even if it was in the *high-RMS* area of the aforementioned 'low rms_min'
    image, i.e.

        flux > (rms_max_I*(det_I + new_source_sigma_margin))

    Note that, once we have located the image with best 'low rms threshold',
    we then use that image to *also* generate the 'high rms threshold'.
    Strictly speaking, this is non-optimal - we should run a fresh search
    against all images to find the best 'high rms threshold'. However, I'm
    working on the assumption that most of
    the time the image with best low-threshold will also have best
    high-threshold, and even when that is not the case we won't lose too much
    accuracy. The benefits of this assumption are simplicity, and possibly
    faster performance, but this might need to be re-examined in future,
    especially if we start ingesting images of wildly differing sizes and
    noise non-uniformity characteristics (e.g. single pointings vs mosaics) etc.

    We use peak flux (f_peak) as the flux value here, since that is likely
    to be the deciding factor in whether a source gets blindly extracted or not.
    (NB This is a hunch, rigorous investigation welcome.)

    """

    # This is another hairy query, but it breaks down like so:
    #
    # The innermost SELECT (unassoc_xtr) is a standard query
    # that we use to grab extractedsources from the current image that
    # do not have a candidate  runcat counterpart from previous images.
    # Note that, by the time this query is run, a new runningcatalog entry has
    # been inserted for them, and the skyregion matching has been done.
    #
    # Next, we match those new sources with previous images overlapping
    # their position according to the criteria in the docstring above,
    # and calculate detection thresholds for each of those images.
    #
    # We then thinly wrap the resulting 'matched_imgs' set in a query
    # to sort them by low_flux_threshold, with high_flux_threshold as the
    # secondary criteria in case of a tie ('ordered_matched_imgs').
    #
    # Finally, we pull out the results we want - new source flux above the low
    # threshold, image ID of the 'best' previous image according to the sorting,
    # and run a final CASE to determine if the new source also passes the
    # high flux threshold.
    #


    query = """\
INSERT INTO newsource
  (runcat
  ,trigger_xtrsrc
  ,newsource_type
  ,previous_limits_image
  )
  SELECT new_src_runcat_id AS runcat
         ,new_src_xtr_id AS trigger_xtrsrc
         ,CASE WHEN new_src_flux > high_flux_threshold
               THEN 1
               ELSE 0
          END as newsource_type
         ,prev_img_id AS previous_limits_image
  FROM ( SELECT  new_src_runcat_id
                ,new_src_xtr_id
                ,new_src_flux
                ,prev_img_id
                ,low_flux_threshold
                ,high_flux_threshold
                ,ROW_NUMBER() OVER (
                         PARTITION BY new_src_xtr_id
                         ORDER BY low_flux_threshold ASC,
                                  high_flux_threshold ASC
                         ) AS row_num
         FROM ( SELECT runcat1.id as new_src_runcat_id
                      ,unassoc_xtr.xtrsrc_id as new_src_xtr_id
                      ,unassoc_xtr.f_peak as new_src_flux
                      ,prev_imgs.id as prev_img_id
                      ,(prev_imgs.rms_min *
                            (prev_imgs.detection_thresh + %(sigma_margin)s))
                        AS low_flux_threshold
                      ,(prev_imgs.rms_max *
                            (prev_imgs.detection_thresh + %(sigma_margin)s))
                        AS high_flux_threshold
                FROM (SELECT x1.id AS xtrsrc_id
                          ,x1.f_peak
                      FROM extractedsource x1
                      WHERE x1.image = %(image_id)s
                      AND x1.id NOT IN (SELECT xtrsrc FROM temprunningcatalog)
                      AND x1.extract_type = 0
                    ) unassoc_xtr
                   ,runningcatalog runcat1
                   ,assocskyrgn asky1
                   ,image this_img
                   ,image prev_imgs
                WHERE this_img.id = %(image_id)s
                AND runcat1.xtrsrc = unassoc_xtr.xtrsrc_id
                AND asky1.runcat = runcat1.id
                AND prev_imgs.dataset = this_img.dataset
                AND prev_imgs.skyrgn = asky1.skyrgn
                AND prev_imgs.band = this_img.band
                AND this_img.taustart_ts > prev_imgs.taustart_ts
                AND prev_imgs.id NOT IN (select image from rejection)
         ) matched_imgs
  ) ordered_matched_imgs
  WHERE row_num = 1
    AND new_src_flux > low_flux_threshold
"""
    params = {'image_id': image_id,
              'sigma_margin': new_source_sigma_margin}
    cursor = tkp.db.execute(query, params, commit=True)
    ins = cursor.rowcount
    if ins > 0:
        logger.debug("Added %s new sources to newsource table" % (ins,))


def _update_ff_runcat_extractedsource():
    """
    We are about to delete the runcats that are inactivated, and
    therefore have to set the ff_runcat reference in extractedsource to NULL.
    """
    query = """\
UPDATE extractedsource
   SET ff_runcat = NULL
 WHERE EXISTS (SELECT id
                 FROM runningcatalog
                WHERE runningcatalog.id = extractedsource.ff_runcat
                  AND runningcatalog.inactive = TRUE
              )
"""
    cursor = tkp.db.execute(query, commit=True)
    cnt = cursor.rowcount
    if cnt > 0:
        logger.debug("Unset ff_runcat for %s extractedsources" % cnt)

def _delete_inactive_runcat():
    """Delete the one-to-many associations from temprunningcatalog,
    and delete the inactive rows from runningcatalog.

    After the one-to-many associations have been processed,
    they can be deleted from the temporary table and
    the runningcatalog.
    """
    query = """\
DELETE
  FROM runningcatalog
 WHERE inactive = TRUE
"""
    tkp.db.execute(query, commit=True)

