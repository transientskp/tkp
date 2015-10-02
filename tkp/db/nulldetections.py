"""
A collection of back end subroutines (mostly SQL queries).

This module contains the routines to deal with null detections.
"""
import logging
from tkp.db import execute as execute
from tkp.db.associations import _empty_temprunningcatalog as _del_tempruncat
from tkp.db.associations import (
    ONE_TO_ONE_ASSOC_QUERY, _insert_1_to_1_runcat_flux,
    _update_1_to_1_runcat_flux)

logger = logging.getLogger(__name__)


def get_nulldetections(image_id, expiration=10):
    """
    Returns the runningcatalog sources which:

      * Are associated with the skyregion of the current image.
      * Do not have a counterpart in the extractedsources of the current
        image after source association has run.
      * Have been seen (in any band) at a timestamp earlier than that of the
        current image.

    NB This runs *after* the source association.

    We determine null detections only as those sources which have been
    seen at earlier times which don't appear in the current image.
    Sources which have not been seen earlier, and which appear in
    different bands at the current timestep, are *not* null detections,
    but are considered as "new" sources.

    args:
        image_id (int): database ID of image
        expiration (int): number of forced fits performed after a blind fit):

    Returns: list of tuples [(runcatid, ra, decl)]
    """

    # The first temptable t0 looks for runcat sources that have been seen
    # in the same sky region as the current image,
    # but at an earlier timestamp, irrespective of the band.
    # The second temptable t1 returns the runcat source ids for those sources
    # that have an association with the current extracted sources.
    # The left outer join in combination with the t1.runcat IS NULL then
    # returns the runcat sources that could not be associated.

    query = """\
SELECT t0.id
      ,t0.wm_ra
      ,t0.wm_decl
  FROM (SELECT r0.id
              ,r0.wm_ra
              ,r0.wm_decl
          FROM image i0
              ,assocskyrgn a0
              ,runningcatalog r0
              ,extractedsource x0
              ,image i1
         WHERE i0.id = %(image_id)s
           AND a0.skyrgn = i0.skyrgn
           AND r0.id = a0.runcat
           AND r0.forcedfits_count < %(expiration)s
           AND x0.id = r0.xtrsrc
           AND i1.id = x0.image
           AND i0.taustart_ts > i1.taustart_ts
       ) t0
       LEFT OUTER JOIN (SELECT a.runcat
                          FROM extractedsource x
                              ,assocxtrsource a
                         WHERE x.image = %(image_id)s
                           AND a.xtrsrc = x.id
                       ) t1
       ON t0.id = t1.runcat
 WHERE t1.runcat IS NULL
"""
    qry_params = {'image_id': image_id, 'expiration': expiration}
    cursor = execute(query, qry_params)
    res = cursor.fetchall()
    return res


def associate_nd(image_id):
    """
    Associate the null detections (ie forced fits) of the current image.

    They will be inserted in a temporary table, which contains the
    associations of the forced fits with the running catalog sources.
    Also, the forced fits are appended to the assocxtrsource (light-curve)
    table. The runcat_flux table is updated with the new datapoints if it
    already existed, otherwise it is inserted as a new datapoint.
    (We leave the runcat table unchanged.)
    After all this, the temporary table is emptied again.
    """

    _del_tempruncat()
    _insert_tempruncat(image_id)
    _insert_1_to_1_assoc()
    _increment_forcedfits_count()

    n_updated = _update_1_to_1_runcat_flux()
    if n_updated:
        logger.debug("Updated flux for %s null_detections" % n_updated)
    n_inserted = _insert_1_to_1_runcat_flux()
    if n_inserted:
        logger.debug("Inserted new-band flux measurement for %s null_detections"
                    % n_inserted)
    _del_tempruncat()


def _increment_forcedfits_count():
    """
    Increment the forcedfits count for every runningcatalog entry in the
    temprunningcatalog table.
    """
    query = """\
UPDATE
    runningcatalog
SET
    forcedfits_count = forcedfits_count + 1
WHERE id IN (
    SELECT
        t.runcat
    FROM
        temprunningcatalog t,
        runningcatalog r
    WHERE
        t.runcat = r.id
)
"""
    execute(query)


def _insert_tempruncat(image_id):
    """
    Here the associations of forced fits and their runningcatalog counterparts
    are inserted into the temporary table.

    We follow the analogies of the normal association procedure.
    The difference here is that we know what the runcat ids are for the
    extractedsource.extract_type = 1 (ff_nd) sources are, since these
    were inserted at the same time as well.

    This is why subtable t0 looks simpler than in the normal case. We
    still have to do a left outer join with the runcat_flux table (rf),
    because fluxes might not be detected in other bands.
    Before being inserted the additional properties are calculated.

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
        ,0 AS distance_arcsec
        ,0 AS r
        ,t0.dataset
        ,t0.band
        ,t0.stokes
        ,t0.datapoints
        ,t0.zone
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
        ,t0.x
        ,t0.y
        ,t0.z
        ,CASE WHEN rf.f_datapoints IS NULL
              THEN 1
              ELSE rf.f_datapoints + 1
         END AS f_datapoints
        ,CASE WHEN rf.f_datapoints IS NULL
              THEN t0.f_peak
              ELSE (rf.f_datapoints * rf.avg_f_peak
                    + t0.f_peak)
                   / (rf.f_datapoints + 1)
         END AS avg_f_peak
        ,CASE WHEN rf.f_datapoints IS NULL
              THEN t0.f_peak * t0.f_peak
              ELSE (rf.f_datapoints * rf.avg_f_peak_sq
                    + t0.f_peak * t0.f_peak)
                   / (rf.f_datapoints + 1)
         END AS avg_f_peak_sq
        ,CASE WHEN rf.f_datapoints IS NULL
              THEN 1 / (t0.f_peak_err * t0.f_peak_err)
              ELSE (rf.f_datapoints * rf.avg_f_peak_weight
                    + 1 / (t0.f_peak_err * t0.f_peak_err))
                   / (rf.f_datapoints + 1)
         END AS avg_f_peak_weight
        ,CASE WHEN rf.f_datapoints IS NULL
              THEN t0.f_peak / (t0.f_peak_err * t0.f_peak_err)
              ELSE (rf.f_datapoints * rf.avg_weighted_f_peak
                    + t0.f_peak / (t0.f_peak_err * t0.f_peak_err))
                   / (rf.f_datapoints + 1)
         END AS avg_weighted_f_peak
        ,CASE WHEN rf.f_datapoints IS NULL
              THEN t0.f_peak * t0.f_peak / (t0.f_peak_err * t0.f_peak_err)
              ELSE (rf.f_datapoints * rf.avg_weighted_f_peak_sq
                    + (t0.f_peak * t0.f_peak) / (t0.f_peak_err * t0.f_peak_err))
                   / (rf.f_datapoints + 1)
         END AS avg_weighted_f_peak_sq
        ,CASE WHEN rf.f_datapoints IS NULL
              THEN t0.f_int
              ELSE (rf.f_datapoints * rf.avg_f_int
                    + t0.f_int)
                   / (rf.f_datapoints + 1)
         END AS avg_f_int
        ,CASE WHEN rf.f_datapoints IS NULL
              THEN t0.f_int * t0.f_int
              ELSE (rf.f_datapoints * rf.avg_f_int_sq
                    + t0.f_int * t0.f_int)
                   / (rf.f_datapoints + 1)
         END AS avg_f_int_sq
        ,CASE WHEN rf.f_datapoints IS NULL
              THEN 1 / (t0.f_int_err * t0.f_int_err)
              ELSE (rf.f_datapoints * rf.avg_f_int_weight
                    + 1 / (t0.f_int_err * t0.f_int_err))
                   / (rf.f_datapoints + 1)
         END AS avg_f_int_weight
        ,CASE WHEN rf.f_datapoints IS NULL
              THEN t0.f_int / (t0.f_int_err * t0.f_int_err)
              ELSE (rf.f_datapoints * rf.avg_weighted_f_int
                    + t0.f_int / (t0.f_int_err * t0.f_int_err))
                   / (rf.f_datapoints + 1)
         END AS avg_weighted_f_int
        ,CASE WHEN rf.f_datapoints IS NULL
              THEN t0.f_int * t0.f_int / (t0.f_int_err * t0.f_int_err)
              ELSE (rf.f_datapoints * rf.avg_weighted_f_int_sq
                    + (t0.f_int * t0.f_int) / (t0.f_int_err * t0.f_int_err))
                   / (rf.f_datapoints + 1)
         END AS avg_weighted_f_int_sq
    FROM (SELECT r.id AS runcat
                ,x.id AS xtrsrc
                ,x.f_peak
                ,x.f_peak_err
                ,x.f_int
                ,x.f_int_err
                ,i.dataset
                ,i.band
                ,i.stokes
                ,r.datapoints
                ,r.zone
                ,r.wm_ra
                ,r.wm_decl
                ,r.wm_uncertainty_ew
                ,r.wm_uncertainty_ns
                ,r.avg_ra_err
                ,r.avg_decl_err
                ,r.avg_wra
                ,r.avg_wdecl
                ,r.avg_weight_ra
                ,r.avg_weight_decl
                ,r.x
                ,r.y
                ,r.z
            FROM extractedsource x
                ,image i
                ,runningcatalog r
           WHERE x.image = %(image_id)s
             AND x.extract_type = 1
             AND i.id = x.image
             AND r.id = x.ff_runcat
             AND r.mon_src = FALSE
         ) t0
         LEFT OUTER JOIN runningcatalog_flux rf
         ON t0.runcat = rf.runcat
         AND t0.band = rf.band
         AND t0.stokes = rf.stokes
"""
    qry_params = {'image_id': image_id}
    cursor = execute(query, qry_params, commit=True)
    cnt = cursor.rowcount
    logger.debug("Inserted %s null detections in tempruncat" % cnt)


def _insert_1_to_1_assoc():
    """
    The null detection forced fits are appended to the assocxtrsource
    (light-curve) table as a type = 7 datapoint.
    Subtable t1 has to take care of the cases where values and
    differences might get too small to cause divisions by zero.

    """
    cursor = execute(ONE_TO_ONE_ASSOC_QUERY, {'type': 7}, commit=True)
    cnt = cursor.rowcount
    logger.debug("Inserted %s 1-to-1 null detections in assocxtrsource" % cnt)
