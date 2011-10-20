# -*- coding: utf-8 -*-

#
# LOFAR Transients Key Project
#

# Local tkp_lib functionality
import math
import logging
import monetdb.sql as db
from tkp.config import config
from tkp.sourcefinder.extract import Detection
from .database import ENGINE


DERUITER_R = config['source_association']['deruiter_radius']
BG_DENSITY = config['source_association']['bg-density']


def insert_dataset(conn, description):
    """Insert dataset with discription as given by argument.
    DB function insertDataset() sets default values.
    """

    newdsid = None
    try:
        cursor = conn.cursor()
        query = """\
        SELECT insertDataset(%s)
        """
        cursor.execute(query, (description,))
        newdsid = cursor.fetchone()[0]
        conn.commit()
    except db.Error, e:
        logging.warn("Failed on query: %s." % query)
        raise
    finally:
        conn.cursor().close()
    return newdsid


def insert_image(conn, dsid, freq_eff, freq_bw, taustart_ts, url):
    """Insert an image for a given dataset with the column values
    set in data discriptor
    """

    newimgid = None
    try:
        cursor = conn.cursor()
        query = """\
        SELECT insertImage(%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (dsid
                              ,freq_eff
                              ,freq_bw
                              ,taustart_ts
                              ,url
                              ))
        newimgid = cursor.fetchone()[0]
        conn.commit()
    except db.Error, e:
        logging.warn("Failed on query: %s." % query)
        raise
    finally:
        cursor.close()
    return newimgid

def load_LSM(conn, ira_min, ira_max, idecl_min, idecl_max, cat1="NVSS", cat2="VLSS", cat3="WENSS"):
    #raise NotImplementedError

    try:
        cursor = conn.cursor()
        query = """\
        CALL LoadLSM(%s, %s, %s, %s, %s, %s, %s)
        /*CALL LoadLSM(47, 59, 50, 58, 'NVSS', 'VLSS', 'WENSS')*/
        """
        cursor.execute(query, (ira_min,ira_max,idecl_min,idecl_max,cat1,cat2,cat3))
        #cursor.execute(query)
        conn.commit()
    except db.Error, e:
        logging.warn("Failed to insert lsm by procedure LoadLSM: %s" % e)
        raise
    finally:
        cursor.close()


def _empty_detections(conn):
    """Empty the detections table

    Initialize the detections table by
    deleting all entries.

    It is used at the beginning and the end.
    """

    try:
        cursor = conn.cursor()
        query = """\
        DELETE FROM detections
        """
        cursor.execute(query)
        conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()


def _insert_into_detections(conn, results):
    """Insert all detections

    Insert all detections, as they are,
    straight into the detection table.

    """

    # TODO: COPY INTO is faster.
    if not results:
        return
    try:
        query = [str(det.serialize()) if isinstance(det, Detection) else
                 str(tuple(det)) for det in results]
        query = "INSERT INTO detections VALUES " + ",".join(query)
        conn.cursor().execute(query)
        conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        conn.cursor().close()


def _insert_extractedsources(conn, image_id):
    """Insert all extracted sources with their properties

    Insert all detected sources and some derived properties into the
    extractedsources table.

    """

    cursor = conn.cursor()
    try:
        query = """\
        INSERT INTO extractedsources
          (image_id
          ,zone
          ,ra
          ,decl
          ,ra_err
          ,decl_err
          ,x
          ,y
          ,z
          ,det_sigma
          ,I_peak
          ,I_peak_err
          ,I_int
          ,I_int_err
          )
          SELECT image_id
                ,zone
                ,ra
                ,decl
                ,ra_err
                ,decl_err
                ,x
                ,y
                ,z
                ,det_sigma
                ,I_peak
                ,I_peak_err
                ,I_int
                ,I_int_err
           FROM (SELECT %s AS image_id
                       ,CAST(FLOOR(ldecl) AS INTEGER) AS zone
                       ,lra AS ra
                       ,ldecl AS decl
                       ,lra_err * 3600 AS ra_err
                       ,ldecl_err * 3600 AS decl_err
                       ,COS(rad(ldecl)) * COS(rad(lra)) AS x
                       ,COS(rad(ldecl)) * SIN(rad(lra)) AS y
                       ,SIN(rad(ldecl)) AS z
                       ,ldet_sigma AS det_sigma
                       ,lI_peak AS I_peak 
                       ,lI_peak_err AS I_peak_err
                       ,lI_int AS I_int
                       ,lI_int_err AS I_int_err
                   FROM detections
                ) t0
          /*     ,node n
          WHERE n.zone = t0.zone*/
        """
        cursor.execute(query, (image_id,))
        conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()


def insert_extracted_sources(conn, image_id, results):
    """Insert all extracted sources

    Insert the sources that were detected by the Source Extraction
    procedures into the extractedsources table.

    Therefore, we use a temporary table containing the"raw" detections,
    from which the sources will then be inserted into extractedsourtces.
    """

    _empty_detections(conn)
    _insert_into_detections(conn, results)
    _insert_extractedsources(conn, image_id)
    _empty_detections(conn)


def _empty_temprunningcatalog(conn):
    """Initialize the temporary storage table

    Initialize the temporary table temprunningcatalog which contains
    the current observed sources.
    """

    try:
        cursor = conn.cursor()
        query = """DELETE FROM temprunningcatalog"""
        cursor.execute(query)
        conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()


def _insert_temprunningcatalog(conn, image_id, deRuiter_r):
    """Select matched sources

    Here we select the extractedsources that have a positional match
    with the sources in the running catalogue table (runningcatalog)
    and those who have will be inserted into the temporary running
    catalogue table (temprunningcatalog).

    Explanation of some columns used in the SQL query:

    - avg_I_peak := average of I_peak
    - avg_I_peak_sq := average of I_peak^2
    - avg_weight_I_peak := average of weight of I_peak, i.e. 1/error^2
    - avg_weighted_I_peak := average of weighted i_peak,
         i.e. average of I_peak/error^2
    - avg_weighted_I_peak_sq := average of weighted i_peak^2,
         i.e. average of I_peak^2/error^2

    This result set might contain multiple associations (1-n,n-1)
    for a single known source in runningcatalog.

    The n-1 assocs will be treated similar as the 1-1 assocs.
    """

    try:
        cursor = conn.cursor()
        # !!TODO!!: Add columns for previous weighted averaged values,
        # otherwise the assoc_r will be biased.
        query = """\
INSERT INTO temprunningcatalog
  (xtrsrc_id
  ,assoc_xtrsrc_id
  ,ds_id
  ,datapoints
  ,zone
  ,wm_ra
  ,wm_decl
  ,wm_ra_err
  ,wm_decl_err
  ,avg_wra
  ,avg_wdecl
  ,avg_weight_ra
  ,avg_weight_decl
  ,x
  ,y
  ,z
  ,avg_I_peak
  ,avg_I_peak_sq
  ,avg_weight_peak
  ,avg_weighted_I_peak
  ,avg_weighted_I_peak_sq
  )
  SELECT t0.xtrsrc_id
        ,t0.assoc_xtrsrc_id
        ,t0.ds_id
        ,t0.datapoints
        ,CAST(FLOOR(t0.wm_decl/1) AS INTEGER)
        ,t0.wm_ra
        ,t0.wm_decl
        ,t0.wm_ra_err
        ,t0.wm_decl_err
        ,t0.avg_wra
        ,t0.avg_wdecl
        ,t0.avg_weight_ra
        ,t0.avg_weight_decl
        ,COS(rad(t0.wm_decl)) * COS(rad(t0.wm_ra))
        ,COS(rad(t0.wm_decl)) * SIN(rad(t0.wm_ra))
        ,SIN(rad(t0.wm_decl))
        ,t0.avg_I_peak
        ,t0.avg_I_peak_sq
        ,t0.avg_weight_peak
        ,t0.avg_weighted_I_peak
        ,t0.avg_weighted_I_peak_sq
    FROM (SELECT b0.xtrsrc_id as xtrsrc_id
                ,x0.xtrsrcid as assoc_xtrsrc_id
                ,im0.ds_id
                ,b0.datapoints + 1 AS datapoints
                ,((datapoints * b0.avg_wra + x0.ra /
                  (x0.ra_err * x0.ra_err)) / (datapoints + 1))
                 /
                 ((datapoints * b0.avg_weight_ra + 1 /
                   (x0.ra_err * x0.ra_err)) / (datapoints + 1))
                 AS wm_ra
                ,((datapoints * b0.avg_wdecl + x0.decl /
                  (x0.decl_err * x0.decl_err)) / (datapoints + 1))
                 /
                 ((datapoints * b0.avg_weight_decl + 1 /
                   (x0.decl_err * x0.decl_err)) / (datapoints + 1))
                 AS wm_decl
                ,SQRT(1 / ((datapoints + 1) *
                  ((datapoints * b0.avg_weight_ra +
                    1 / (x0.ra_err * x0.ra_err)) / (datapoints + 1))
                          )
                     ) AS wm_ra_err
                ,SQRT(1 / ((datapoints + 1) *
                  ((datapoints * b0.avg_weight_decl +
                    1 / (x0.decl_err * x0.decl_err)) / (datapoints + 1))
                          )
                     ) AS wm_decl_err
                ,(datapoints * b0.avg_wra + x0.ra / (x0.ra_err * x0.ra_err))
                 / (datapoints + 1) AS avg_wra
                ,(datapoints * b0.avg_wdecl + x0.decl /
                  (x0.decl_err * x0.decl_err))
                 / (datapoints + 1) AS avg_wdecl
                ,(datapoints * b0.avg_weight_ra + 1 /
                  (x0.ra_err * x0.ra_err))
                 / (datapoints + 1) AS avg_weight_ra
                ,(datapoints * b0.avg_weight_decl + 1 /
                  (x0.decl_err * x0.decl_err))
                 / (datapoints + 1) AS avg_weight_decl
                ,(datapoints * b0.avg_I_peak + x0.I_peak)
                 / (datapoints + 1)
                 AS avg_I_peak
                ,(datapoints * b0.avg_I_peak_sq +
                  x0.I_peak * x0.I_peak)
                 / (datapoints + 1)
                 AS avg_I_peak_sq
                ,(datapoints * b0.avg_weight_peak + 1 /
                  (x0.I_peak_err * x0.I_peak_err))
                 / (datapoints + 1)
                 AS avg_weight_peak
                ,(datapoints * b0.avg_weighted_I_peak + x0.I_peak /
                  (x0.I_peak_err * x0.I_peak_err))
                 / (datapoints + 1)
                 AS avg_weighted_I_peak
                ,(datapoints * b0.avg_weighted_I_peak_sq
                  + (x0.I_peak * x0.I_peak) /
                     (x0.I_peak_err * x0.I_peak_err))
                 / (datapoints + 1) AS avg_weighted_I_peak_sq
            FROM runningcatalog b0
                ,extractedsources x0
                ,images im0
           WHERE x0.image_id = %s
             AND x0.image_id = im0.imageid
             AND im0.ds_id = b0.ds_id
             AND b0.zone BETWEEN CAST(FLOOR(x0.decl - 0.025) as INTEGER)
                             AND CAST(FLOOR(x0.decl + 0.025) as INTEGER)
             AND b0.wm_decl BETWEEN x0.decl - 0.025
                                AND x0.decl + 0.025
             AND b0.wm_ra BETWEEN x0.ra - alpha(0.025,x0.decl)
                              AND x0.ra + alpha(0.025,x0.decl)
             AND SQRT(  (x0.ra * COS(rad(x0.decl)) - b0.wm_ra * COS(rad(b0.wm_decl)))
                      * (x0.ra * COS(rad(x0.decl)) - b0.wm_ra * COS(rad(b0.wm_decl)))
                      / (x0.ra_err * x0.ra_err + b0.wm_ra_err * b0.wm_ra_err)
                     + (x0.decl - b0.wm_decl) * (x0.decl - b0.wm_decl)
                      / (x0.decl_err * x0.decl_err + b0.wm_decl_err * b0.wm_decl_err)
                     ) < %s
         ) t0
"""
        cursor.execute(query, (image_id, deRuiter_r))
        #if image_id == 2:
        #    raise
        conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()


def _flag_multiple_counterparts_in_runningcatalog(conn):
    """Flag source with multiple associations

    Before we continue, we first take care of the sources that have
    multiple associations in both directions.

    -1- running-catalogue sources  <- extracted source

    An extracted source has multiple counterparts in the running
    catalogue.  We only keep the ones with the lowest deRuiter_r
    value, the rest we throw away.

    NOTE:

    It is worth considering whether this might be changed to selecting
    the brightest neighbour source, instead of just the closest
    neighbour.

    (There are case [when flux_lim > 10Jy] that the nearest source has
    a lower flux level, causing unexpected spectral indices)
    """

    try:
        cursor = conn.cursor()
        query = """\
        SELECT t1.xtrsrc_id
              ,t1.assoc_xtrsrc_id
          FROM (SELECT tb0.assoc_xtrsrc_id
                      ,MIN(SQRT((x0.ra - b0.wm_ra) * COS(rad(x0.decl))
                                * (x0.ra - b0.wm_ra) * COS(rad(x0.decl))
                                / (x0.ra_err * x0.ra_err + b0.wm_ra_err *
                                   b0.wm_ra_err)
                               + (x0.decl - b0.wm_decl) *
                                 (x0.decl - b0.wm_decl)
                                / (x0.decl_err * x0.decl_err +
                                   b0.wm_decl_err * b0.wm_decl_err)
                               )
                          ) AS min_r1
                  FROM temprunningcatalog tb0
                      ,runningcatalog b0
                      ,extractedsources x0
                 WHERE tb0.assoc_xtrsrc_id IN (SELECT assoc_xtrsrc_id
                                                 FROM temprunningcatalog
                                               GROUP BY assoc_xtrsrc_id
                                               HAVING COUNT(*) > 1
                                              )
                   AND tb0.xtrsrc_id = b0.xtrsrc_id
                   AND tb0.assoc_xtrsrc_id = x0.xtrsrcid
                GROUP BY tb0.assoc_xtrsrc_id
               ) t0
              ,(SELECT tb1.xtrsrc_id
                      ,tb1.assoc_xtrsrc_id
                      ,SQRT( (x1.ra - b1.wm_ra) * COS(rad(x1.decl))
                            *(x1.ra - b1.wm_ra) * COS(rad(x1.decl))
                            / (x1.ra_err * x1.ra_err +
                               b1.wm_ra_err * b1.wm_ra_err)
                           + (x1.decl - b1.wm_decl) * (x1.decl - b1.wm_decl)
                             / (x1.decl_err * x1.decl_err + b1.wm_decl_err *
                                b1.wm_decl_err)
                           ) AS r1
                  FROM temprunningcatalog tb1
                      ,runningcatalog b1
                      ,extractedsources x1
                 WHERE tb1.assoc_xtrsrc_id IN (SELECT assoc_xtrsrc_id
                                                 FROM temprunningcatalog
                                               GROUP BY assoc_xtrsrc_id
                                               HAVING COUNT(*) > 1
                                              )
                   AND tb1.xtrsrc_id = b1.xtrsrc_id
                   AND tb1.assoc_xtrsrc_id = x1.xtrsrcid
               ) t1
         WHERE t1.assoc_xtrsrc_id = t0.assoc_xtrsrc_id
           AND t1.r1 > t0.min_r1
        """
        cursor.execute(query)
        results = zip(*cursor.fetchall())
        if len(results) != 0:
            xtrsrc_id = results[0]
            assoc_xtrsrc_id = results[1]
            # TODO: Consider setting row to inactive instead of deleting
            query = """\
            DELETE
              FROM temprunningcatalog
             WHERE xtrsrc_id = %s
               AND assoc_xtrsrc_id = %s
            """
            for j in range(len(xtrsrc_id)):
                cursor.execute(query, (xtrsrc_id[j], assoc_xtrsrc_id[j]))
            conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()


def _insert_multiple_assocs(conn):
    """Insert sources with multiple associations

    -2- Now, we take care of the sources in the running catalogue that
    have more than one counterpart among the extracted sources.

    We now make two entries in the running catalogue, in stead of the
    one we had before. Therefore, we 'swap' the ids.
    """

    try:
        cursor = conn.cursor()
        query = """\
        INSERT INTO assocxtrsources
          (xtrsrc_id
          ,assoc_xtrsrc_id
          ,assoc_distance_arcsec
          ,assoc_r
          ,assoc_lr_method
          )
          SELECT t.assoc_xtrsrc_id
                ,t.xtrsrc_id
                ,3600 * deg(2 * ASIN(SQRT((r.x - x.x) * (r.x - x.x)
                                          + (r.y - x.y) * (r.y - x.y)
                                          + (r.z - x.z) * (r.z - x.z)
                                          ) / 2) ) AS assoc_distance_arcsec
                ,3600 * sqrt(
                    ( (r.wm_ra * cos(rad(r.wm_decl)) - x.ra * cos(rad(x.decl)))
                     *(r.wm_ra * cos(rad(r.wm_decl)) - x.ra * cos(rad(x.decl)))
                    ) 
                    / (r.wm_ra_err * r.wm_ra_err + x.ra_err * x.ra_err)
                    + ((r.wm_decl - x.decl) * (r.wm_decl - x.decl)) 
                    / (r.wm_decl_err * r.wm_decl_err + x.decl_err * x.decl_err)
                            ) as assoc_r
                ,1
            FROM temprunningcatalog t
                ,runningcatalog r
                ,extractedsources x
           WHERE t.xtrsrc_id = r.xtrsrc_id
             AND t.xtrsrc_id = x.xtrsrcid
             AND t.xtrsrc_id IN (SELECT xtrsrc_id
                                   FROM temprunningcatalog
                                 GROUP BY xtrsrc_id
                                 HAVING COUNT(*) > 1
                                )
        """
        cursor.execute(query)
        conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()


def _insert_first_of_assocs(conn):
    """Insert identical ids

    -3- And, we have to insert identical ids to identify a light-curve
    starting point.
    """

    try:
        cursor = conn.cursor()
        query = """\
        INSERT INTO assocxtrsources
          (xtrsrc_id
          ,assoc_xtrsrc_id
          ,assoc_distance_arcsec
          ,assoc_r
          ,assoc_lr_method
          )
          SELECT assoc_xtrsrc_id
                ,assoc_xtrsrc_id
                ,0
                ,0
                ,2
            FROM temprunningcatalog
           WHERE xtrsrc_id IN (SELECT xtrsrc_id
                                 FROM temprunningcatalog
                               GROUP BY xtrsrc_id
                               HAVING COUNT(*) > 1
                              )
        """
        cursor.execute(query)
        conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()


def _flag_swapped_assocs(conn):
    """Throw away swapped ids

    -4- And, we throw away the swapped id.

    It might be better to flag this record: consider setting rows to
    inactive instead of deleting
    """
    try:
        cursor = conn.cursor()
        query = """\
        DELETE
          FROM assocxtrsources
         WHERE xtrsrc_id IN (SELECT xtrsrc_id
                               FROM temprunningcatalog
                             GROUP BY xtrsrc_id
                             HAVING COUNT(*) > 1
                            )
        """
        cursor.execute(query)
        conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()


def _insert_multiple_assocs_runcat(conn):
    """Insert new ids of the sources in the running catalogue"""

    try:
        cursor = conn.cursor()
        query = """\
        INSERT INTO runningcatalog
          (xtrsrc_id
          ,ds_id
          ,datapoints
          ,zone
          ,wm_ra
          ,wm_decl
          ,wm_ra_err
          ,wm_decl_err
          ,avg_wra
          ,avg_wdecl
          ,avg_weight_ra
          ,avg_weight_decl
          ,x
          ,y
          ,z
          ,avg_I_peak
          ,avg_I_peak_sq
          ,avg_weight_peak
          ,avg_weighted_I_peak
          ,avg_weighted_I_peak_sq
          )
          SELECT assoc_xtrsrc_id
                ,ds_id
                ,datapoints
                ,zone
                ,wm_ra
                ,wm_decl
                ,wm_ra_err
                ,wm_decl_err
                ,avg_wra
                ,avg_wdecl
                ,avg_weight_ra
                ,avg_weight_decl
                ,x
                ,y
                ,z
                ,avg_I_peak
                ,avg_I_peak_sq
                ,avg_weight_peak
                ,avg_weighted_I_peak
                ,avg_weighted_I_peak_sq
            FROM temprunningcatalog
           WHERE xtrsrc_id IN (SELECT xtrsrc_id
                                 FROM temprunningcatalog
                               GROUP BY xtrsrc_id
                               HAVING COUNT(*) > 1
                              )
        """
        cursor.execute(query)
        conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()


def _flag_old_assocs_runcat(conn):
    """Here the old assocs in runcat will be deleted."""

    # TODO: Consider setting row to inactive instead of deleting
    try:
        cursor = conn.cursor()
        query = """\
        DELETE
          FROM runningcatalog
         WHERE xtrsrc_id IN (SELECT xtrsrc_id
                               FROM temprunningcatalog
                             GROUP BY xtrsrc_id
                             HAVING COUNT(*) > 1
                            )
        """
        cursor.execute(query)
        conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()


def _flag_multiple_assocs(conn):
    """Delete the multiple assocs from the temporary running catalogue table"""

    try:
        cursor = conn.cursor()
        query = """\
        DELETE
          FROM temprunningcatalog
         WHERE xtrsrc_id IN (SELECT xtrsrc_id
                               FROM temprunningcatalog
                             GROUP BY xtrsrc_id
                             HAVING COUNT(*) > 1
                            )
        """
        cursor.execute(query)
        conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()


def _insert_single_assocs(conn):
    """Insert remaining 1-1 associations into assocxtrsources table"""
    #TODO: check whether last row (t.xtrsrc_id = x.xtrsrcid) should be
    #      t.assocxtrsrc_id = ...)
    try:
        cursor = conn.cursor()
        query = """\
        INSERT INTO assocxtrsources
          (xtrsrc_id
          ,assoc_xtrsrc_id
          ,assoc_distance_arcsec
          ,assoc_r
          ,assoc_lr_method
          )
          SELECT t.xtrsrc_id
                ,t.assoc_xtrsrc_id
                ,3600 * deg(2 * ASIN(SQRT((r.x - x.x) * (r.x - x.x)
                                          + (r.y - x.y) * (r.y - x.y)
                                          + (r.z - x.z) * (r.z - x.z)
                                          ) / 2) ) AS assoc_distance_arcsec
                ,3600 * sqrt(
                    ((r.wm_ra * cos(rad(r.wm_decl)) 
                     - x.ra * cos(rad(x.decl))) 
                    * (r.wm_ra * cos(rad(r.wm_decl)) 
                     - x.ra * cos(rad(x.decl)))) 
                    / (r.wm_ra_err * r.wm_ra_err + x.ra_err*x.ra_err)
                    +
                    ((r.wm_decl - x.decl) * (r.wm_decl - x.decl)) 
                    / (r.wm_decl_err * r.wm_decl_err + x.decl_err*x.decl_err)
                            ) as assoc_r
                ,3
            FROM temprunningcatalog t
                ,runningcatalog r
                ,extractedsources x
           WHERE t.xtrsrc_id = r.xtrsrc_id
             AND t.xtrsrc_id = x.xtrsrcid
        """
        cursor.execute(query)
        conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()


def _update_runningcatalog(conn):
    """Update the running catalog"""

    try:
        cursor = conn.cursor()
        query = """\
SELECT datapoints
      ,zone
      ,wm_ra
      ,wm_decl
      ,wm_ra_err
      ,wm_decl_err
      ,avg_wra
      ,avg_wdecl
      ,avg_weight_ra
      ,avg_weight_decl
      ,x
      ,y
      ,z
      ,avg_I_peak
      ,avg_I_peak_sq
      ,avg_weight_peak
      ,avg_weighted_I_peak
      ,avg_weighted_I_peak_sq
      ,xtrsrc_id
  FROM temprunningcatalog
        """
        cursor.execute(query)
        results = cursor.fetchall()
        query = """\
UPDATE runningcatalog
  SET datapoints = %s
     ,zone = %s
     ,wm_ra = %s
     ,wm_decl = %s
     ,wm_ra_err = %s
     ,wm_decl_err = %s
     ,avg_wra = %s
     ,avg_wdecl = %s
     ,avg_weight_ra = %s
     ,avg_weight_decl = %s
     ,x = %s
     ,y = %s
     ,z = %s
     ,avg_I_peak = %s
     ,avg_I_peak_sq = %s
     ,avg_weight_peak = %s
     ,avg_weighted_I_peak = %s
     ,avg_weighted_I_peak_sq = %s
WHERE xtrsrc_id = %s
"""
        for result in results:
            cursor.execute(query, tuple(result))
        conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()


def _count_known_sources(conn, image_id, deRuiter_r):
    """Count number of extracted sources that are know in the running
    catalog"""

    cursor = conn.cursor()
    try:
        query = """\
SELECT COUNT(*)
  FROM extractedsources x0
      ,images im0
      ,runningcatalog b0
 WHERE x0.image_id = %s
   AND x0.image_id = im0.imageid
   AND im0.ds_id = b0.ds_id
   AND b0.zone BETWEEN x0.zone - cast(0.025 as integer)
                   AND x0.zone + cast(0.025 as integer)
   AND b0.wm_decl BETWEEN x0.decl - 0.025
                      AND x0.decl + 0.025
   AND b0.wm_ra BETWEEN x0.ra - alpha(0.025,x0.decl)
                    AND x0.ra + alpha(0.025,x0.decl)
   AND SQRT(  (x0.ra * COS(rad(x0.decl)) - b0.wm_ra * COS(rad(b0.wm_decl)))
            * (x0.ra * COS(rad(x0.decl)) - b0.wm_ra * COS(rad(b0.wm_decl)))
            / (x0.ra_err * x0.ra_err + b0.wm_ra_err * b0.wm_ra_err)
           + (x0.decl - b0.wm_decl) * (x0.decl - b0.wm_decl)
            / (x0.decl_err * x0.decl_err + b0.wm_decl_err * b0.wm_decl_err)
           ) < %s
"""
        cursor.execute(query, (image_id, deRuiter_r))
        y = cursor.fetchall()
        #print "\t\tNumber of known sources (or sources in NOT IN): ", y[0][0]
        conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()


def _insert_new_assocs(conn, image_id, deRuiter_r):
    """Insert new associations for unknown sources

    This inserts new associations for the sources that were not known
    in the running catalogue (i.e. they did not have an entry in the
    runningcatalog table).
    """

    cursor = conn.cursor()
    try:
        query = """\
        INSERT INTO assocxtrsources
          (xtrsrc_id
          ,assoc_xtrsrc_id
          ,assoc_distance_arcsec
          ,assoc_r
          ,assoc_lr_method
          )
          SELECT x1.xtrsrcid as xtrsrc_id
                ,x1.xtrsrcid as assoc_xtrsrc_id
                ,0
                ,0
                ,4
            FROM extractedsources x1
           WHERE x1.image_id = %s
             AND x1.xtrsrcid NOT IN (
                 SELECT x0.xtrsrcid
                  FROM extractedsources x0
                      ,runningcatalog b0
                      ,images im0
                 WHERE x0.image_id = %s
                   AND x0.image_id = im0.imageid
                   AND im0.ds_id = b0.ds_id
                   AND b0.zone BETWEEN x0.zone - cast(0.025 as integer)
                                   AND x0.zone + cast(0.025 as integer)
                   AND b0.wm_decl BETWEEN x0.decl - 0.025
                                            AND x0.decl + 0.025
                   AND b0.wm_ra BETWEEN x0.ra - alpha(0.025,x0.decl)
                                          AND x0.ra + alpha(0.025,x0.decl)
                   AND SQRT(  (x0.ra * COS(rad(x0.decl)) - b0.wm_ra * COS(rad(b0.wm_decl)))
                            * (x0.ra * COS(rad(x0.decl)) - b0.wm_ra * COS(rad(b0.wm_decl)))
                            / (x0.ra_err * x0.ra_err + b0.wm_ra_err * b0.wm_ra_err)
                           + (x0.decl - b0.wm_decl) * (x0.decl - b0.wm_decl)
                            / (x0.decl_err * x0.decl_err + b0.wm_decl_err * b0.wm_decl_err)
                           ) < %s
                                    )
        """
        cursor.execute(query, (image_id, image_id, deRuiter_r))
        conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()


def _insert_new_source_runcat(conn, image_id, deRuiter_r):
    """Insert new sources into the running catalog"""
    # TODO: check zone cast in search radius!
    cursor = conn.cursor()
    try:
        query = """\
INSERT INTO runningcatalog
  (xtrsrc_id
  ,ds_id
  ,datapoints
  ,zone
  ,wm_ra
  ,wm_decl
  ,wm_ra_err
  ,wm_decl_err
  ,avg_wra
  ,avg_wdecl
  ,avg_weight_ra
  ,avg_weight_decl
  ,x
  ,y
  ,z
  ,avg_I_peak
  ,avg_I_peak_sq
  ,avg_weight_peak
  ,avg_weighted_I_peak
  ,avg_weighted_I_peak_sq
  )
  SELECT x1.xtrsrcid
        ,im1.ds_id
        ,1
        ,x1.zone
        ,x1.ra
        ,x1.decl
        ,x1.ra_err
        ,x1.decl_err
        ,x1.ra / (x1.ra_err * x1.ra_err)
        ,x1.decl / (x1.decl_err * x1.decl_err)
        ,1 / (x1.ra_err * x1.ra_err)
        ,1 / (x1.decl_err * x1.decl_err)
        ,x1.x
        ,x1.y
        ,x1.z
        ,I_peak
        ,I_peak * I_peak
        ,1 / (I_peak_err * I_peak_err)
        ,I_peak / (I_peak_err * I_peak_err)
        ,I_peak * I_peak / (I_peak_err * I_peak_err)
    FROM extractedsources x1
        ,images im1
   WHERE x1.image_id = %s
     AND x1.image_id = im1.imageid
     AND x1.xtrsrcid NOT IN (
         SELECT x0.xtrsrcid
          FROM extractedsources x0
              ,runningcatalog b0
              ,images im0
         WHERE x0.image_id = %s
           AND x0.image_id = im0.imageid
           AND im0.ds_id = b0.ds_id
           AND b0.zone BETWEEN x0.zone - cast(0.025 as integer)
                           AND x0.zone + cast(0.025 as integer)
           AND b0.wm_decl BETWEEN x0.decl - 0.025
                                    AND x0.decl + 0.025
           AND b0.wm_ra BETWEEN x0.ra - alpha(0.025,x0.decl)
                                  AND x0.ra + alpha(0.025,x0.decl)
           AND b0.x * x0.x + b0.y * x0.y + b0.z * x0.z > COS(rad(0.025))
           AND SQRT(  (x0.ra * COS(rad(x0.decl)) - b0.wm_ra * COS(rad(b0.wm_decl)))
                    * (x0.ra * COS(rad(x0.decl)) - b0.wm_ra * COS(rad(b0.wm_decl)))
                    / (x0.ra_err * x0.ra_err + b0.wm_ra_err * b0.wm_ra_err)
                   + (x0.decl - b0.wm_decl) * (x0.decl - b0.wm_decl)
                    / (x0.decl_err * x0.decl_err + b0.wm_decl_err * b0.wm_decl_err)
                   ) < %s
           )
"""
        cursor.execute(query, (image_id, image_id, deRuiter_r))
        conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()


def associate_extracted_sources(conn, image_id, deRuiter_r=DERUITER_R/3600.):
    """Associate extracted sources with sources detected in the running
    catalog

    The dimensionless distance between two sources is given by the
    "De Ruiter radius", see Ch2&3 of thesis Scheers.

    Here we use a default value of deRuiter_r = 3.717/3600. for a
    reliable association.
    """

    #if image_id == 2:
    #    raise
    _empty_temprunningcatalog(conn)
    _insert_temprunningcatalog(conn, image_id, deRuiter_r)
    _flag_multiple_counterparts_in_runningcatalog(conn)
    _insert_multiple_assocs(conn)
    _insert_first_of_assocs(conn)
    _flag_swapped_assocs(conn)
    _insert_multiple_assocs_runcat(conn)
    _flag_old_assocs_runcat(conn)
    _flag_multiple_assocs(conn)
    #+-----------------------------------------------------+
    #| After all this, we are now left with the 1-1 assocs |
    #+-----------------------------------------------------+
    _insert_single_assocs(conn)
    _update_runningcatalog(conn)
    _empty_temprunningcatalog(conn)
    _count_known_sources(conn, image_id, deRuiter_r)
    _insert_new_assocs(conn, image_id, deRuiter_r)
    _insert_new_source_runcat(conn, image_id, deRuiter_r)


def _select_variability_indices(conn, dsid, V_lim, eta_lim):
    """Select sources and variability indices in the running catalog"""

    results = []
    cursor = conn.cursor()
    try:
        query = """\
SELECT
     xtrsrc_id
    ,ds_id
    ,datapoints
    ,wm_ra
    ,wm_decl
    ,wm_ra_err
    ,wm_decl_err
    ,t1.V_inter / t1.avg_i_peak as V
    ,t1.eta_inter / t1.avg_weight_peak as eta
  FROM
    (SELECT
          xtrsrc_id
         ,ds_id
         ,datapoints
         ,wm_ra
         ,wm_decl
         ,wm_ra_err
         ,wm_decl_err
         ,avg_i_peak
         ,avg_weight_peak
         ,CASE WHEN datapoints = 1
               THEN 0
               ELSE sqrt(cast(datapoints as double precision) * (avg_I_peak_sq - avg_I_peak*avg_I_peak) / (cast(datapoints as double precision) - 1.0))
               END
          AS V_inter
         ,CASE WHEN datapoints = 1
               THEN 0
               ELSE (cast(datapoints as double precision) / (cast(datapoints as double precision)-1.0)) * (avg_weight_peak*avg_weighted_I_peak_sq - avg_weighted_I_peak * avg_weighted_I_peak )
               END
          AS eta_inter
      FROM runningcatalog
      WHERE ds_id = %s
      ) t1
  WHERE t1.V_inter / t1.avg_i_peak > %s
  AND t1.eta_inter / t1.avg_weight_peak > %s
"""
        cursor.execute(query, (dsid, V_lim, eta_lim))
        results = cursor.fetchall()
        results = [dict(srcid=x[0], npoints=x[2], v_nu=x[7], eta_nu=x[8])
                   for x in results]
        #conn.commit()
    except db.Error:
        query = query % (dsid, V_lim, eta_lim)
        logging.warn("Failed on query:\n%s", query)
        raise
    finally:
        cursor.close()
    return results


def select_single_epoch_detection(conn, dsid):
    """Select sources and variability indices in the running catalog"""

    results = []
    cursor = conn.cursor()
    try:
        query = """\
SELECT xtrsrc_id
      ,ds_id
      ,datapoints
      ,wm_ra
      ,wm_decl
      ,wm_ra_err
      ,wm_decl_err
      ,sqrt(datapoints*(avg_I_peak_sq - avg_I_peak*avg_I_peak) /
            (datapoints-1)) / avg_I_peak as V
      ,(datapoints/(datapoints-1)) *
       (avg_weighted_I_peak_sq -
        avg_weighted_I_peak * avg_weighted_I_peak / avg_weight_peak)
       as eta
  FROM runningcatalog
 WHERE ds_id = %s
   AND datapoints = 1
"""
        cursor.execute(query, (dsid, ))
        results = cursor.fetchall()
        results = [dict(srcid=x[0], npoints=x[2], v_nu=x[7], eta_nu=x[8])
                   for x in results]
        #conn.commit()
    except db.Error:
        logging.warn("Failed on query %s", query)
        raise
    finally:
        cursor.close()
    return results


def lightcurve(conn, xtrsrcid):
    """Obtain a light curve for a specific source"""

    cursor = conn.cursor()
    try:
        query = """\
SELECT im.taustart_ts, im.tau_time, ex.i_peak, ex.i_peak_err, ex.xtrsrcid
FROM extractedsources ex, assocxtrsources ax, images im
WHERE ax.xtrsrc_id = %s
  AND ex.xtrsrcid = ax.assoc_xtrsrc_id
  AND ex.image_id = im.imageid
ORDER BY im.taustart_ts"""
        cursor.execute(query, (xtrsrcid,))
        results = cursor.fetchall()
    except db.Error:
        query = query % xtrsrcid
        logging.warn("Failed to obtain light curve")
        logging.warn("Failed on query:\n%s", query)
        raise
    finally:
        cursor.close()
    return results

        
def detect_variable_sources(conn, dsid, V_lim, eta_lim):
    """Detect variability in extracted sources compared to the previous
    detections"""

    #sources = _select_variability_indices(conn, dsid, V_lim, eta_lim)
    return _select_variability_indices(conn, dsid, V_lim, eta_lim)


def associate_with_catalogedsources(conn, image_id, radius=0.025, deRuiter_r=DERUITER_R/3600.):
    """Associate extracted sources in specified image with known sources 
    in the external catalogues

    radius (typical 90arcsec=0.025deg), is the radius of the area centered
    at the extracted source which are searched for counterparts in the catalogues.
    
    The dimensionless distance between two sources is given by the
    "De Ruiter radius", see Ch2&3 of thesis Scheers.

    Here we use a default value of deRuiter_r = 3.717/3600. for a
    reliable association.

    Every found candidate is added to the assoccatsources table.
    """

    _insert_cat_assocs(conn, image_id, radius, deRuiter_r)

def _insert_cat_assocs(conn, image_id, radius, deRuiter_r):
    """Insert found xtrsrc--catsrc associations into assoccatsources table.

    The search for cataloged counterpart sources is done in the lsm
    table, which should have been preloaded with a selection of 
    the catalogedsources, depending on the expected field of view.
    
    """
    
    try:
        cursor = conn.cursor()
        query = """\
        INSERT INTO assoccatsources
          (xtrsrc_id
          ,assoc_catsrc_id
          ,assoc_distance_arcsec
          ,assoc_lr_method
          ,assoc_r
          ,assoc_loglr
          )
          SELECT xtrsrcid AS xtrsrc_id
                ,lsmid AS assoc_catsrc_id
                ,3600 * deg(2 * ASIN(SQRT((x0.x - c0.x) * (x0.x - c0.x)
                                          + (x0.y - c0.y) * (x0.y - c0.y)
                                          + (x0.z - c0.z) * (x0.z - c0.z)
                                          ) / 2) ) AS assoc_distance_arcsec
                ,3
                ,3600 * sqrt(
                    ((x0.ra * cos(rad(x0.decl)) 
                     - c0.ra * cos(rad(c0.decl))) 
                    * (x0.ra * cos(rad(x0.decl)) 
                     - c0.ra * cos(rad(c0.decl)))) 
                    / (x0.ra_err * x0.ra_err + c0.ra_err*c0.ra_err)
                    +
                    ((x0.decl - c0.decl) * (x0.decl - c0.decl)) 
                    / (x0.decl_err * x0.decl_err + c0.decl_err*c0.decl_err)
                            ) as assoc_r
                ,LOG10(EXP((( (x0.ra - c0.ra) * COS(rad(x0.decl)) * (x0.ra - c0.ra) * COS(rad(x0.decl)) 
                              / (x0.ra_err * x0.ra_err + c0.ra_err * c0.ra_err)
                             + (x0.decl - c0.decl) * COS(rad(x0.decl)) * (x0.decl - c0.decl) * COS(rad(x0.decl)) 
                               / (x0.decl_err * x0.decl_err + c0.decl_err * c0.decl_err)
                            )
                           ) / 2
                          )
                       /
                       (2 * PI() * SQRT(x0.ra_err * x0.ra_err + c0.ra_err * c0.ra_err) 
                                 * SQRT(x0.decl_err * x0.decl_err + c0.decl_err * c0.decl_err) * 4.02439375E-06)
                       ) AS assoc_loglr
            FROM extractedsources x0
                ,lsm c0
           WHERE x0.image_id = %s
             AND c0.zone BETWEEN CAST(FLOOR(x0.decl - %s) as INTEGER)
                             AND CAST(FLOOR(x0.decl + %s) as INTEGER)
             AND c0.decl BETWEEN x0.decl - %s
                             AND x0.decl + %s
             AND c0.ra BETWEEN x0.ra - alpha(%s, x0.decl)
                           AND x0.ra + alpha(%s, x0.decl)
             AND SQRT(  (x0.ra * COS(rad(x0.decl)) - c0.ra * COS(rad(c0.decl)))
                      * (x0.ra * COS(rad(x0.decl)) - c0.ra * COS(rad(c0.decl)))
                      / (x0.ra_err * x0.ra_err + c0.ra_err * c0.ra_err)
                     + (x0.decl - c0.decl) * (x0.decl - c0.decl)
                      / (x0.decl_err * x0.decl_err + c0.decl_err * c0.decl_err)
                     ) < %s
        """
        cursor.execute(query, (image_id,radius,radius,radius,radius,radius,radius,deRuiter_r))
        conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()

def associate_catalogued_sources_in_area(conn, ra, dec, radius, deRuiter_r=DERUITER_R/3600.):
    pass


def store_transient_source(conn, srcid, siglevel, t_start):
    cursor = conn.cursor()
    try:
        query = """\
INSERT INTO transients
(xtrsrc_id, siglevel, t_start)
  SELECT rc.xtrsrc_id, '%s', '%s' FROM runningcatalog rc
  WHERE rc.xtrsrc_id = %%s
  AND rc.xtrsrc_id NOT IN
  (SELECT xtrsrc_id FROM transients)""" % (str(siglevel), str(t_start))
        cursor.execute(query, (srcid,))
        conn.commit()
    except db.Error:
        logging.warn("Query %s failed", query)
        raise
    finally:
        cursor.close()

def concurrency_test_fixedalpha(conn):
    """Unit test function to test concuurency
    """

    theta = 0.025
    decl = 80.
    alpha = None
    try:
        cursor = conn.cursor()
        query = """\
        SELECT alpha(%s, %s)
        """
        cursor.execute(query, (theta, decl))
        alpha = cursor.fetchone()[0]
        conn.commit()
    except db.Error, e:
        logging.warn("Failed on query: %s." % query)
        raise
    finally:
        conn.cursor().close()
    return alpha

def concurrency_test_randomalpha(conn):
    """Unit test function to test concuurency
    """

    import random
    theta = 0.025
    decl = random.random() * 90
    alpha = None
    try:
        cursor = conn.cursor()
        query = """\
        SELECT alpha(%s, %s)
        """
        cursor.execute(query, (theta, decl))
        alpha = cursor.fetchone()[0]
        conn.commit()
    except db.Error, e:
        logging.warn("Failed on query: %s." % query)
        raise
    finally:
        conn.cursor().close()
    return alpha


def columns_from_table(conn, table, keywords=None, where=None):
    """Obtain specific column (keywords) values from 'table', with
    kwargs limitations.

    A very simple helper function, that builds an SQL query to obtain
    the specified columns from 'table', and then executes that
    query. Optionally, the WHERE clause can be specified using the
    where dictionary. It returns a list of a
    dict (with the originally supplied keywords as dictionary keys),
    which can be empty.

    Example:
    
        >>> columns_from_table(conn, 'images',
            keywords=['taustart_ts', 'tau_time', 'freq_eff', 'freq_bw'], imageid=1)
            [{'freq_eff': 133984375.0, 'taustart_ts': datetime.datetime(2010, 10, 9, 9, 4, 2), 'tau_time': 14400.0, 'freq_bw': 1953125.0}]

        This builds the SQL query:
        "SELECT taustart_ts, tau_time, freq_eff, freq_bw FROM images WHERE imageid=1"

    This function is implemented mainly to abstract and hide the SQL
    functionality from the Python interface.
    """

    # Note from the Python docs: If items(), keys(), values(),
    # iteritems(), iterkeys(), and itervalues() are called with no
    # intervening modifications to the dictionary, the lists will
    # directly correspond.
    results = []
    if keywords is None:
        query = "SELECT * FROM " + table
    else:
        query = "SELECT " + ", ".join(keywords) + " FROM " + table
    if where is None:
        where = {}
    where_args = tuple(where.itervalues())
    where = " AND ".join(["%s=%%s" % key for key in where.iterkeys()])
    if where:
        query += " WHERE " + where
    try:
        cursor = conn.cursor()
        cursor.execute(query, where_args)
        results = cursor.fetchall()
        if keywords is None:
            keywords = [desc[0] for desc in cursor.description]
        results = [dict([(keyword, value) for keyword, value in zip(keywords, result)]) for result in results]
    except db.Error, exc:
        query = query % where_args
        logging.warn("Failed on query: %s" % query)
        raise
    finally:
        conn.cursor().close()
    return results


def set_columns_for_table(conn, table, data=None, where=None):
    """Set specific columns (keywords) for 'table', with 'where'
    limitations.

    A simple helper function, that builds an SQL query to update the
    specified columns given by data for 'table', and then executes
    that query. Optionally, the WHERE clause can be specified using
    the 'where' dictionary.

    The data argument is a dictionary with the names and corresponding
    values of the columns that need to be updated.
    """

    # Note from the Python docs: If items(), keys(), values(),
    # iteritems(), iterkeys(), and itervalues() are called with no
    # intervening modifications to the dictionary, the lists will
    # directly correspond.
    query = "UPDATE " + table + " SET " + ", ".join(["%s=%%s" % key for key in data.iterkeys()])
    if where is None:
        where = {}
    where_args = tuple(where.itervalues())
    where = " AND ".join(["%s=%%s" % key for key in where.iterkeys()])
    values = tuple(data.itervalues())
    if where:
        query += " WHERE " + where
    try:
        cursor = conn.cursor()
        cursor.execute(query, values + where_args)
        conn.commit()
    except db.Error, e:
        query = query % (values + where_args)
        logging.warn("Failed on query: %s" % query)
        raise
    finally:
        conn.cursor().close()



def match_nearest_in_catalogs(conn, ra, decl, ra_err, decl_err, radius=1.0,
                              catalogid=None, assoc_r=DERUITER_R/3600.):
    """Match a source with position ra, decl with catalogedsources
    within radius

    Args:

        ra, decl, ra_err, decl_err (float): position of the source

    Kwargs:
    
        radius (float): search radius around the source to search, in
        degrees

        catalogid (int or list of ints): the catalog(s) to search. If
        none, all catalogs are searched for. A single integer
        specifies one catalog, while a list of integers specifies
        multiple catalogs.

        assoc_r (float): dimensionless search radius, in units of the
        De Ruiter radius. 3.7/3600. is a good value, though the
        default is 180 (which will match all sources). Assoc_r sets a
        cut off for the found sources.
        
    The return values are ordered first by catalog, then by
    assoc_r. So the first source in the list is the closest match for
    a catalog.
    """
    zoneheight = 1.0
    x = math.cos(decl/180.*math.pi) * math.cos(ra/180.*math.pi);
    y = math.cos(decl/180.*math.pi) * math.sin(ra/180.*math.pi);
    z = math.sin(decl/180.*math.pi);

    catalog_filter = ""
    if catalogid is None:
        catalog_filter = ""
    else:
        try:
            iter(catalogid)
            # Note: cast to int, to ensure proper type
            catalog_filter = (
                "c.catid in (%s) AND " % ", ".join(
                [str(int(catid)) for catid in catalogid]))
        except TypeError:
            catalog_filter = "c.catid = %d AND " % catalogid
    
    subquery = """\
SELECT
    cs.catsrcid
   ,c.catid
   ,c.catname
   ,cs.catsrcname
   ,cs.ra
   ,cs.decl
   ,cs.ra_err
   ,cs.decl_err
   ,3600 * deg(2 * ASIN(SQRT(
       (%%s - cs.x) * (%%s - cs.x)
       + (%%s - cs.y) * (%%s - cs.y)
       + (%%s - cs.z) * (%%s - cs.z)
       ) / 2)
   ) AS assoc_distance_arcsec
   ,SQRT( (%%s - cs.ra) * COS(rad(%%s)) * (%%s - cs.ra) * COS(rad(%%s))
   / (cast(%%s as double precision) * %%s + cs.ra_err * cs.ra_err)
   + (%%s - cs.decl) * (%%s - cs.decl)
   / (cast(%%s as double precision) * %%s + cs.decl_err * cs.decl_err)
   ) AS assoc_r
FROM
     catalogedsources cs
    ,catalogs c
WHERE
      %(catalog_filter)s
  cs.cat_id = c.catid
  AND cs.x * %%s + cs.y * %%s + cs.z * %%s > COS(rad(%%s))
  AND cs.zone BETWEEN CAST(FLOOR(cast(%%s - %%s as double precision) / %%s) AS INTEGER)
                  AND CAST(FLOOR(cast(%%s + %%s as double precision) / %%s) AS INTEGER)
  AND cs.ra BETWEEN %%s - alpha(%%s, %%s)
                AND %%s + alpha(%%s, %%s)
  AND cs.decl BETWEEN %%s - %%s
                  AND %%s + %%s
""" % {'catalog_filter': catalog_filter}
    query = """\
SELECT 
    t.catsrcid
   ,t.catsrcname
   ,t.catid
   ,t.catname
   ,t.ra
   ,t.decl
   ,t.ra_err
   ,t.decl_err
   ,t.assoc_distance_arcsec
   ,t.assoc_r
FROM (%(subquery)s) as t
WHERE t.assoc_r < %%s
ORDER BY t.catid ASC, t.assoc_r ASC
""" % {'subquery': subquery}
    results = []
    try:
        cursor = conn.cursor()
        cursor.execute(query,  (
            x, x, y, y, z, z, ra, decl, ra, decl, ra_err, ra_err, decl, decl,
            decl_err, decl_err, x, y, z, radius, decl, radius,
            zoneheight, decl, radius, zoneheight, ra, radius, decl, ra, radius,
            decl, decl, radius, decl, radius, assoc_r))
        results = cursor.fetchall()
        results = [
            {'catsrcid': result[0], 'catsrcname': result[1],
             'catid': result[2], 'catname': result[3],
             'ra': result[4], 'decl': result[5],
             'ra_err': result[6], 'decl_err': result[7],
             'dist_arcsec': result[8], 'assoc_r': result[9]}
            for result in results]
    except db.Error, e:
        query = query % (
            x, x, y, y, z, z, ra, decl, ra, decl, ra_err, ra_err, decl, decl,
            decl_err, decl_err, x, y, z, radius, decl, radius,
            zoneheight, decl, radius, zoneheight, ra, radius, decl, ra, radius,
            decl, decl, radius, decl, radius, assoc_r)
        logging.warn("Failed on query %s:", query)
        raise
    finally:
        cursor.close()
    return results
