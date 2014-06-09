"""
A collection of back end subroutines (mostly SQL queries).

This module contains the routines to deal with null detections.
"""
import logging
from tkp.db import execute as execute
from tkp.db.associations import _empty_temprunningcatalog as _del_tempruncat

logger = logging.getLogger(__name__)


def get_nulldetections(image_id):
    """
    Returns the runningcatalog sources which:

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
    qry_params = {'image_id': image_id}
    cursor = execute(query, qry_params)
    results = zip(*cursor.fetchall())
    if len(results) != 0:
        return zip(list(results[1]), list(results[2]))
    else:
        return []


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
    _update_runcat_flux()
    _insert_runcat_flux()
    _del_tempruncat()


def _insert_tempruncat(image_id):
    """
    Here the associations of forced fits and their runningcatalog counterparts
    are inserted into the temporary table.

    We follow the implementation of the normal association procedure,
    except that we don't need to match with a De Ruiter radius, since
    the counterpart pairs are from the same runningcatalog source.
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
        ,0 as distance_arcsec
        ,0 as r
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
            FROM runningcatalog r
                ,image i
                ,extractedsource x
           WHERE i.id = %(image_id)s
             AND r.dataset = i.dataset
             AND x.image = i.id
             AND x.image = %(image_id)s
             AND x.extract_type = 1
             AND r.mon_src = FALSE
             AND r.zone BETWEEN CAST(FLOOR(x.decl - x.error_radius/3600) AS INTEGER)
                              AND CAST(FLOOR(x.decl + x.error_radius/3600) AS INTEGER)
             AND r.wm_decl BETWEEN x.decl - x.error_radius/3600
                               AND x.decl + x.error_radius/3600
             AND r.wm_ra BETWEEN x.ra - alpha(x.error_radius/3600, x.decl)
                             AND x.ra + alpha(x.error_radius/3600, x.decl)
             AND r.x * x.x + r.y * x.y + r.z * x.z > COS(RADIANS(r.wm_uncertainty_ew))
         ) t0
         LEFT OUTER JOIN runningcatalog_flux rf
         ON t0.runcat = rf.runcat
         AND t0.band = rf.band
         AND t0.stokes = rf.stokes
"""
    qry_params = {'image_id': image_id}
    cursor = execute(query, qry_params, commit=True)
    cnt = cursor.rowcount
    logger.info("Inserted %s null detections in tempruncat" % cnt)


def _insert_1_to_1_assoc():
    """
    The null detection forced fits are appended to the assocxtrsource
    (light-curve) table as a type = 7 datapoint.
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
  )
  SELECT t.runcat
        ,t.xtrsrc
        ,7 AS type
        ,0 AS distance_arcsec
        ,0 AS r
        ,t.v_int_inter / t.avg_f_int
        ,t.eta_int_inter / t.avg_f_int_weight
    FROM (SELECT runcat
                ,xtrsrc
                ,CASE WHEN avg_f_int = 0.0
                      THEN 0.000001
                      ELSE avg_f_int
                 END AS avg_f_int
                ,avg_f_int_weight
                ,CASE WHEN f_datapoints = 1
                      THEN 0
                      ELSE CASE WHEN ABS(avg_f_int_sq - avg_f_int * avg_f_int) < 8e-14
                                THEN 0
                                ELSE SQRT(CAST(f_datapoints AS DOUBLE PRECISION)
                                         * (avg_f_int_sq - avg_f_int * avg_f_int)
                                         / (CAST(f_datapoints AS DOUBLE PRECISION) - 1.0)
                                         )
                           END
                 END AS v_int_inter
                ,CASE WHEN f_datapoints = 1
                      THEN 0
                      ELSE (CAST(f_datapoints AS DOUBLE PRECISION)
                            / (CAST(f_datapoints AS DOUBLE PRECISION) - 1.0))
                           * (avg_f_int_weight * avg_weighted_f_int_sq
                             - avg_weighted_f_int * avg_weighted_f_int)
                 END AS eta_int_inter
            FROM temprunningcatalog
           ) t
"""
    cursor = execute(query, commit=True)
    cnt = cursor.rowcount
    logger.info("Inserted %s 1-to-1 null detections in assocxtrsource" % cnt)


def _update_runcat_flux():
    """We only have to update those runcat sources that already had a detection,
    so their f_datapoints is larger than 1.

    """
    query = """\
UPDATE runningcatalog_flux
   SET f_datapoints = (SELECT f_datapoints
                         FROM temprunningcatalog
                        WHERE temprunningcatalog.runcat = runningcatalog_flux.runcat
                          AND temprunningcatalog.band = runningcatalog_flux.band
                          AND temprunningcatalog.stokes = runningcatalog_flux.stokes
                          AND temprunningcatalog.inactive = FALSE
                          AND temprunningcatalog.f_datapoints > 1
                      )
      ,avg_f_peak = (SELECT avg_f_peak
                       FROM temprunningcatalog
                      WHERE temprunningcatalog.runcat = runningcatalog_flux.runcat
                        AND temprunningcatalog.band = runningcatalog_flux.band
                        AND temprunningcatalog.stokes = runningcatalog_flux.stokes
                        AND temprunningcatalog.inactive = FALSE
                        AND temprunningcatalog.f_datapoints > 1
                    )
      ,avg_f_peak_sq = (SELECT avg_f_peak_sq
                          FROM temprunningcatalog
                         WHERE temprunningcatalog.runcat = runningcatalog_flux.runcat
                           AND temprunningcatalog.band = runningcatalog_flux.band
                           AND temprunningcatalog.stokes = runningcatalog_flux.stokes
                           AND temprunningcatalog.inactive = FALSE
                           AND temprunningcatalog.f_datapoints > 1
                       )
      ,avg_f_peak_weight = (SELECT avg_f_peak_weight
                              FROM temprunningcatalog
                             WHERE temprunningcatalog.runcat = runningcatalog_flux.runcat
                               AND temprunningcatalog.band = runningcatalog_flux.band
                               AND temprunningcatalog.stokes = runningcatalog_flux.stokes
                               AND temprunningcatalog.inactive = FALSE
                               AND temprunningcatalog.f_datapoints > 1
                           )
      ,avg_weighted_f_peak = (SELECT avg_weighted_f_peak
                                FROM temprunningcatalog
                               WHERE temprunningcatalog.runcat = runningcatalog_flux.runcat
                                 AND temprunningcatalog.band = runningcatalog_flux.band
                                 AND temprunningcatalog.stokes = runningcatalog_flux.stokes
                                 AND temprunningcatalog.inactive = FALSE
                                 AND temprunningcatalog.f_datapoints > 1
                             )
      ,avg_weighted_f_peak_sq = (SELECT avg_weighted_f_peak_sq
                                   FROM temprunningcatalog
                                  WHERE temprunningcatalog.runcat = runningcatalog_flux.runcat
                                    AND temprunningcatalog.band = runningcatalog_flux.band
                                    AND temprunningcatalog.stokes = runningcatalog_flux.stokes
                                    AND temprunningcatalog.inactive = FALSE
                                    AND temprunningcatalog.f_datapoints > 1
                                )
      ,avg_f_int = (SELECT avg_f_int
                      FROM temprunningcatalog
                     WHERE temprunningcatalog.runcat = runningcatalog_flux.runcat
                       AND temprunningcatalog.band = runningcatalog_flux.band
                       AND temprunningcatalog.stokes = runningcatalog_flux.stokes
                       AND temprunningcatalog.inactive = FALSE
                       AND temprunningcatalog.f_datapoints > 1
                   )
      ,avg_f_int_sq = (SELECT avg_f_int_sq
                         FROM temprunningcatalog
                        WHERE temprunningcatalog.runcat = runningcatalog_flux.runcat
                          AND temprunningcatalog.band = runningcatalog_flux.band
                          AND temprunningcatalog.stokes = runningcatalog_flux.stokes
                          AND temprunningcatalog.inactive = FALSE
                          AND temprunningcatalog.f_datapoints > 1
                      )
      ,avg_f_int_weight = (SELECT avg_f_int_weight
                             FROM temprunningcatalog
                             WHERE temprunningcatalog.runcat = runningcatalog_flux.runcat
                               AND temprunningcatalog.band = runningcatalog_flux.band
                               AND temprunningcatalog.stokes = runningcatalog_flux.stokes
                               AND temprunningcatalog.inactive = FALSE
                               AND temprunningcatalog.f_datapoints > 1
                          )
      ,avg_weighted_f_int = (SELECT avg_weighted_f_int
                               FROM temprunningcatalog
                              WHERE temprunningcatalog.runcat = runningcatalog_flux.runcat
                                AND temprunningcatalog.band = runningcatalog_flux.band
                                AND temprunningcatalog.stokes = runningcatalog_flux.stokes
                                AND temprunningcatalog.inactive = FALSE
                                AND temprunningcatalog.f_datapoints > 1
                            )
      ,avg_weighted_f_int_sq = (SELECT avg_weighted_f_int_sq
                                  FROM temprunningcatalog
                                 WHERE temprunningcatalog.runcat = runningcatalog_flux.runcat
                                   AND temprunningcatalog.band = runningcatalog_flux.band
                                   AND temprunningcatalog.stokes = runningcatalog_flux.stokes
                                   AND temprunningcatalog.inactive = FALSE
                                   AND temprunningcatalog.f_datapoints > 1
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
    cursor = execute(query, commit=True)
    cnt = cursor.rowcount
    if cnt > 0:
        logger.info("Updated flux for %s null_detections" % cnt)


def _insert_runcat_flux():
    """Sources that were not yet detected in this frequency band before,
    will be appended to it. Those have their first f_datapoint.
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
   WHERE f_datapoints = 1
    """
    cursor = execute(query, commit=True)
    cnt = cursor.rowcount
    if cnt > 0:
        logger.info("Inserted fluxes for %s null_detections" % cnt)

