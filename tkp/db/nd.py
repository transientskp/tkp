"""
A collection of back end subroutines (mostly SQL queries).

This module contains the routines to deal with null detections.
"""
import logging, sys
from collections import namedtuple

from tkp.db import general
#import tkp.db
from tkp.db import execute as execute
from tkp.db.associations import _empty_temprunningcatalog as _del_tempruncat

logger = logging.getLogger(__name__)


def get_nulldetections(image_id, deRuiter_r):
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

    Output: list of tuples [(runcatid, ra, decl)]
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
    qry_params = {'image_id':image_id}
    cursor = execute(query, qry_params)
    results = zip(*cursor.fetchall())
    if len(results) != 0:
        return zip(list(results[1]), list(results[2]))
        #maxbeam = max(results[3][0],results[4][0]) # all bmaj & bmin are the same
    else:
        return []

def associate_nd(image_id):
    """
    Also take into account the ra=360 wrapping
    
    Mmm, how do we associate with the runcats...
    """
    
    # Here we select the forced fit null detections in the current image
    # and associate them with the runningcatalog sources
    print "assoc_nd, im:", image_id
    _del_tempruncat()
    # Check meridian wrapping...?
    _insert_tempruncat(image_id)
    _insert_1_to_1_assoc(image_id)
    # We have to update the runcat_fluxes or insert
    _update_runcat_flux(image_id)
    _insert_runcat_flux(image_id)
    _del_tempruncat()

def _insert_tempruncat(image_id):
    """
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
             AND r.zone BETWEEN CAST(FLOOR(x.decl - x.error_radius/3600) AS INTEGER)
                              AND CAST(FLOOR(x.decl + x.error_radius/3600) AS INTEGER)
             AND r.wm_decl BETWEEN x.decl - x.error_radius/3600
                               AND x.decl + x.error_radius/3600
             AND r.wm_ra BETWEEN x.ra - alpha(x.error_radius/3600, x.decl)
                             AND x.ra + alpha(x.error_radius/3600, x.decl)
             /*AND r.x * x.x + r.y * x.y + r.z * x.z > COS(RADIANS(r.wm_uncertainty_ew/3600))*/
             AND r.x * x.x + r.y * x.y + r.z * x.z > COS(RADIANS(x.error_radius/3600))
         ) t0
         LEFT OUTER JOIN runningcatalog_flux rf
         ON t0.runcat = rf.runcat
         AND t0.band = rf.band
         AND t0.stokes = rf.stokes
"""    
    qry_params = {'image_id': image_id}
    #print "QQQ:", query % qry_params
    #if image_id == 771:
    #    sys.exit()
    cursor = execute(query, qry_params, commit=True)
    cnt = cursor.rowcount
    print "# tempruncat_inserts:", cnt
    logger.info("Inserted %s null detections in tempruncat" % cnt)

def _insert_1_to_1_assoc(image_id):
    """
    Insert remaining associations from temprunningcatalog into assocxtrsource.
    """
    query = """\
INSERT INTO assocxtrsource
  (runcat
  ,xtrsrc
  ,distance_arcsec
  ,r
  ,type
  )
  SELECT runcat
        ,xtrsrc
        ,distance_arcsec
        ,r
        ,7
    FROM temprunningcatalog
"""
    cursor = execute(query, commit=True)
    cnt = cursor.rowcount
    print "# assocxtrsrc_inserts:", cnt
    logger.info("Inserted %s 1-to-1 null detections in assocxtrsource" % cnt)


def _update_runcat_flux(image_id):
    """We only have to update those runcat sources that had already a detection, so 
    their f_datapoints is larger than 1.
        
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
    
def _insert_runcat_flux(image_id):
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
    
