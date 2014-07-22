"""
A collection of back end subroutines (mostly SQL queries).

This module contains the routines to deal with the monitoring
sources, provided by the user via the command line.
"""
import logging, sys

from tkp.db import execute as execute
from tkp.db.associations import _empty_temprunningcatalog as _del_tempruncat
from tkp.db.associations import ONE_TO_ONE_ASSOC_QUERY

logger = logging.getLogger(__name__)


def associate_ms(image_id):
    """
    Associate the monitoring sources, i.e., their forced fits,
    of the current image with the ones in the running catalog.
    These associations are treated separately from the normal
    associations and there will only be 1-to-1 associations.

    The runcat-monitoring source pairs will be inserted in a
    temporary table.
    Of these, the runcat and runcat_flux tables are updated with
    the new datapoints if the (monitoring) source already existed,
    otherwise they are inserted as a new source.
    The source pair is appended to the light-curve table
    (assocxtrsource), with a type = 8 (for the first occurence)
    or type = 9 (for existing runcat sources).
    After all this, the temporary table is emptied again.
    """

    _del_tempruncat()
    _insert_tempruncat(image_id)
    #+-------------------------------------------------------------+
    #| First, we process the monitoring sources that are already   |
    #| known by position in the runningcatalog. Note that a source |
    #| might be known by position, but is new in a frequency band. |
    #+-------------------------------------------------------------+
    _update_runcat()
    _update_runcat_flux() # update flux in existing band
    _insert_runcat_flux() # insert flux for new band
    _insert_1_to_1_assoc()
    #+-------------------------------------------------------------+
    #| Then we process the new sources, i.e., those that           |
    #| were fitted for the first time.                             |
    #+-------------------------------------------------------------+
    _insert_new_runcat(image_id)
    _insert_new_runcat_flux(image_id)
    _insert_new_1_to_1_assoc(image_id)
    _del_tempruncat()

def _insert_tempruncat(image_id):
    """
    Here the associations of forced fits of the monitoring sources
    and their runningcatalog counterparts are inserted into the
    temporary table.

    We follow the implementation of the normal association procedure,
    except that we don't need to match with a De Ruiter radius, since
    the counterpart pairs are from the same runningcatalog source.
    """

    # The query is as follows:
    # t0 searches for matches between the monitoring sources
    # (extract_type = 2) in the current image that have
    # a counterpart among the runningcatalog sources. This
    # matching is done by zone, decl, ra (corrected for alpha
    # infaltion towards the poles) and the dot product by
    # using the Cartesian coordinates. Note that the conical
    # distance is not determined by the De Ruiter radius,
    # since all these sources have identical positions.
    # t0 has a left outer join with the runningcatalog_flux table,
    # since the image might be of a new frequency band. In that case
    # all the rf.values are NULL.
    # The select then determines all the new (statistical) properties
    # for the runcat-monitoring pairs, which are inserted in the
    # tempruncat table.
    # Note that a first image does not have any matches,
    # but that is taken into account by the second part of
    # the associate_ms() function.
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
                ,r.datapoints + 1 AS datapoints
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
             AND x.extract_type = 2
             AND r.mon_src = TRUE
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
    if cnt > 0:
        logger.info("Inserted %s monitoring-runcat candidate pairs in tempruncat" % cnt)

def _update_runcat():
    """Update the running catalog (positional) properties of the
    monitoring sources with the values in temprunningcatalog"""

    query = """\
        UPDATE runningcatalog
           SET datapoints = (SELECT datapoints
                               FROM temprunningcatalog
                              WHERE temprunningcatalog.runcat = runningcatalog.id
                            )
              ,zone = (SELECT zone
                         FROM temprunningcatalog
                        WHERE temprunningcatalog.runcat = runningcatalog.id
                      )
              ,wm_ra = (SELECT wm_ra
                          FROM temprunningcatalog
                         WHERE temprunningcatalog.runcat = runningcatalog.id
                       )
              ,wm_decl = (SELECT wm_decl
                            FROM temprunningcatalog
                           WHERE temprunningcatalog.runcat = runningcatalog.id
                         )
              ,avg_ra_err = (SELECT avg_ra_err
                              FROM temprunningcatalog
                             WHERE temprunningcatalog.runcat = runningcatalog.id
                           )
              ,avg_decl_err = (SELECT avg_decl_err
                                FROM temprunningcatalog
                               WHERE temprunningcatalog.runcat = runningcatalog.id
                             )
              ,wm_uncertainty_ew = (SELECT wm_uncertainty_ew
                                FROM temprunningcatalog
                               WHERE temprunningcatalog.runcat = runningcatalog.id
                             )
              ,wm_uncertainty_ns = (SELECT wm_uncertainty_ns
                                FROM temprunningcatalog
                               WHERE temprunningcatalog.runcat = runningcatalog.id
                             )
              ,avg_wra = (SELECT avg_wra
                            FROM temprunningcatalog
                           WHERE temprunningcatalog.runcat = runningcatalog.id
                         )
              ,avg_wdecl = (SELECT avg_wdecl
                              FROM temprunningcatalog
                             WHERE temprunningcatalog.runcat = runningcatalog.id
                           )
              ,avg_weight_ra = (SELECT avg_weight_ra
                                  FROM temprunningcatalog
                                 WHERE temprunningcatalog.runcat = runningcatalog.id
                               )
              ,avg_weight_decl = (SELECT avg_weight_decl
                                    FROM temprunningcatalog
                                   WHERE temprunningcatalog.runcat = runningcatalog.id
                                 )
              ,x = (SELECT x
                      FROM temprunningcatalog
                     WHERE temprunningcatalog.runcat = runningcatalog.id
                   )
              ,y = (SELECT y
                      FROM temprunningcatalog
                     WHERE temprunningcatalog.runcat = runningcatalog.id
                   )
              ,z = (SELECT z
                      FROM temprunningcatalog
                     WHERE temprunningcatalog.runcat = runningcatalog.id
                   )
         WHERE EXISTS (SELECT runcat
                         FROM temprunningcatalog
                        WHERE temprunningcatalog.runcat = runningcatalog.id
                      )
"""
    cursor = execute(query, commit=True)
    cnt = cursor.rowcount
    if cnt > 0:
        logger.info("Updated %s monitoring sources in runcat" % cnt)

def _update_runcat_flux():
    """We only have to update those runcat fluxes that already had a fit,
    so their f_datapoints is larger than 1. The ones had a fit in
    another band, but not in this are handled by the _insert_runcat_flux().

    """
    query = """\
UPDATE runningcatalog_flux
   SET f_datapoints = (SELECT f_datapoints
                         FROM temprunningcatalog
                        WHERE temprunningcatalog.runcat = runningcatalog_flux.runcat
                          AND temprunningcatalog.band = runningcatalog_flux.band
                          AND temprunningcatalog.stokes = runningcatalog_flux.stokes
                          AND temprunningcatalog.f_datapoints > 1
                      )
      ,avg_f_peak = (SELECT avg_f_peak
                       FROM temprunningcatalog
                      WHERE temprunningcatalog.runcat = runningcatalog_flux.runcat
                        AND temprunningcatalog.band = runningcatalog_flux.band
                        AND temprunningcatalog.stokes = runningcatalog_flux.stokes
                        AND temprunningcatalog.f_datapoints > 1
                    )
      ,avg_f_peak_sq = (SELECT avg_f_peak_sq
                          FROM temprunningcatalog
                         WHERE temprunningcatalog.runcat = runningcatalog_flux.runcat
                           AND temprunningcatalog.band = runningcatalog_flux.band
                           AND temprunningcatalog.stokes = runningcatalog_flux.stokes
                           AND temprunningcatalog.f_datapoints > 1
                       )
      ,avg_f_peak_weight = (SELECT avg_f_peak_weight
                              FROM temprunningcatalog
                             WHERE temprunningcatalog.runcat = runningcatalog_flux.runcat
                               AND temprunningcatalog.band = runningcatalog_flux.band
                               AND temprunningcatalog.stokes = runningcatalog_flux.stokes
                               AND temprunningcatalog.f_datapoints > 1
                           )
      ,avg_weighted_f_peak = (SELECT avg_weighted_f_peak
                                FROM temprunningcatalog
                               WHERE temprunningcatalog.runcat = runningcatalog_flux.runcat
                                 AND temprunningcatalog.band = runningcatalog_flux.band
                                 AND temprunningcatalog.stokes = runningcatalog_flux.stokes
                                 AND temprunningcatalog.f_datapoints > 1
                             )
      ,avg_weighted_f_peak_sq = (SELECT avg_weighted_f_peak_sq
                                   FROM temprunningcatalog
                                  WHERE temprunningcatalog.runcat = runningcatalog_flux.runcat
                                    AND temprunningcatalog.band = runningcatalog_flux.band
                                    AND temprunningcatalog.stokes = runningcatalog_flux.stokes
                                    AND temprunningcatalog.f_datapoints > 1
                                )
      ,avg_f_int = (SELECT avg_f_int
                      FROM temprunningcatalog
                     WHERE temprunningcatalog.runcat = runningcatalog_flux.runcat
                       AND temprunningcatalog.band = runningcatalog_flux.band
                       AND temprunningcatalog.stokes = runningcatalog_flux.stokes
                       AND temprunningcatalog.f_datapoints > 1
                   )
      ,avg_f_int_sq = (SELECT avg_f_int_sq
                         FROM temprunningcatalog
                        WHERE temprunningcatalog.runcat = runningcatalog_flux.runcat
                          AND temprunningcatalog.band = runningcatalog_flux.band
                          AND temprunningcatalog.stokes = runningcatalog_flux.stokes
                          AND temprunningcatalog.f_datapoints > 1
                      )
      ,avg_f_int_weight = (SELECT avg_f_int_weight
                             FROM temprunningcatalog
                             WHERE temprunningcatalog.runcat = runningcatalog_flux.runcat
                               AND temprunningcatalog.band = runningcatalog_flux.band
                               AND temprunningcatalog.stokes = runningcatalog_flux.stokes
                               AND temprunningcatalog.f_datapoints > 1
                          )
      ,avg_weighted_f_int = (SELECT avg_weighted_f_int
                               FROM temprunningcatalog
                              WHERE temprunningcatalog.runcat = runningcatalog_flux.runcat
                                AND temprunningcatalog.band = runningcatalog_flux.band
                                AND temprunningcatalog.stokes = runningcatalog_flux.stokes
                                AND temprunningcatalog.f_datapoints > 1
                            )
      ,avg_weighted_f_int_sq = (SELECT avg_weighted_f_int_sq
                                  FROM temprunningcatalog
                                 WHERE temprunningcatalog.runcat = runningcatalog_flux.runcat
                                   AND temprunningcatalog.band = runningcatalog_flux.band
                                   AND temprunningcatalog.stokes = runningcatalog_flux.stokes
                                   AND temprunningcatalog.f_datapoints > 1
                               )
 WHERE EXISTS (SELECT runcat
                 FROM temprunningcatalog
                WHERE temprunningcatalog.runcat = runningcatalog_flux.runcat
                  AND temprunningcatalog.band = runningcatalog_flux.band
                  AND temprunningcatalog.stokes = runningcatalog_flux.stokes
                  AND temprunningcatalog.f_datapoints > 1
              )
"""
    cursor = execute(query, commit=True)
    cnt = cursor.rowcount
    if cnt > 0:
        logger.info("Updated fluxes for %s monitoring sources in runcat_flux" % cnt)

def _insert_runcat_flux():
    """Monitoring sources that were not yet fitted in this frequency band before,
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
        logger.info("Inserted new-band fluxes for %s monitoring sources in runcat_flux" % cnt)


def _insert_1_to_1_assoc():
    """
    The runcat-monitoring pairs are appended to the assocxtrsource
    (light-curve) table as a type = 9 datapoint.
    """
    cursor = execute(ONE_TO_ONE_ASSOC_QUERY, {'type': 9}, commit=True)
    cnt = cursor.rowcount
    if cnt > 0:
        logger.info("Inserted %s runcat-monitoring source pairs in assocxtrsource" % cnt)


def _insert_new_runcat(image_id):
    """Insert the fits of the monitoring sources as new sources
    into the runningcatalog
    """

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
  ,mon_src
  )
  SELECT x.id AS xtrsrc
        ,i.dataset
        ,1 AS datapoints
        ,x.zone
        ,x.ra AS wm_ra
        ,x.decl AS wm_decl
        ,x.ra_err AS avg_ra_err
        ,x.decl_err AS avg_decl_err
        ,x.uncertainty_ew AS wm_uncertainty_ew
        ,x.uncertainty_ns AS wm_uncertainty_ns
        ,x.ra / (x.uncertainty_ew * x.uncertainty_ew) AS avg_wra
        ,x.decl / (x.uncertainty_ns * x.uncertainty_ns) AS avg_wdecl
        ,1 / (x.uncertainty_ew * x.uncertainty_ew) AS avg_weight_ra
        ,1 / (x.uncertainty_ns * x.uncertainty_ns) AS avg_weight_decl
        ,x.x
        ,x.y
        ,x.z
        ,TRUE
    FROM image i
        ,extractedsource x
         LEFT OUTER JOIN temprunningcatalog t
         ON t.xtrsrc = x.id
   WHERE i.id = %(image_id)s
     AND x.image = i.id
     AND x.extract_type = 2
     AND t.xtrsrc IS NULL
"""
    cursor = execute(query, {'image_id': image_id}, commit=True)
    ins = cursor.rowcount
    if ins > 0:
        logger.info("Added %s new monitoring sources to runningcatalog" % ins)


def _insert_new_runcat_flux(image_id):
    """Insert the fitted fluxes of the monitoring sources as new datapoints
    into the runningcatalog_flux.

    Extractedsources for which not a counterpart was found in the
    runningcatalog, i.e., those that do not have an entry in the
    tempruncat table (t0) will be added as a new source in the
    runningcatalog_flux table.

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
                 LEFT OUTER JOIN temprunningcatalog trc1
                 ON x1.id = trc1.xtrsrc
            WHERE x1.image = %(image_id)s
              AND x1.extract_type = 2
              AND trc1.xtrsrc IS NULL
          ) t0
        ,runningcatalog r0
        ,extractedsource x0
   WHERE i0.id = %(image_id)s
     AND r0.xtrsrc = t0.xtrsrc
     AND x0.id = r0.xtrsrc
     AND x0.extract_type = 2
"""
    cursor = execute(query, {'image_id': image_id}, commit=True)
    ins = cursor.rowcount
    if ins > 0:
        logger.info("Added %s new monitoring fluxes to runningcatalog_flux" % ins)


def _insert_new_1_to_1_assoc(image_id):
    """
    The forced fits of the monitoring sources which are new
    are appended to the assocxtrsource (light-curve) table
    as a type = 8 datapoint.
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
        ,8 AS type
        ,0 AS distance_arcsec
        ,0 AS r
        ,0 AS v_int
        ,0 AS eta_int
        ,1 as f_datapoints
    FROM (SELECT x1.id AS xtrsrc
            FROM extractedsource x1
                 LEFT OUTER JOIN temprunningcatalog trc1
                 ON x1.id = trc1.xtrsrc
            WHERE x1.image = %(image_id)s
              AND x1.extract_type = 2
              AND trc1.xtrsrc IS NULL
         ) t0
        ,runningcatalog r0
   WHERE r0.xtrsrc = t0.xtrsrc
    """
    cursor = execute(query, {'image_id': image_id}, commit=True)
    cnt = cursor.rowcount
    if cnt > 0:
        logger.info("Inserted %s new runcat-monitoring source pairs in assocxtrsource" % cnt)



