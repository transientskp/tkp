#
# LOFAR Transients Key Project
#

# Local tkp_lib functionality
import monetdb.sql as db
import logging
from tkp.config import config


DERUITER_R = config['source_association']['deruiter_radius']


def load_LSM(ira_min, ira_max, idecl_min, idecl_max, cn1, cn2, cn3, conn):
    raise NotImplementedError

    ##try:
    ##    cursor = conn.cursor()
    ##    procLoadLSM = "CALL LoadLSM(%s,%s,%s,%s,%s,%s,%s)" % (
    ##            ira_min,ira_max,idecl_min,idecl_max,cn1,cn2,cn3)
    ##    cursor.execute(procLoadLSM)
    ##except db.Error, e:
    ##    logging.warn("Failed to insert lsm by procedure LoadLSM")
    ##    raise
    ##finally:
    ##    cursor.close()
    ##conn.commit()


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
    try:
        cursor = conn.cursor()
        query = "INSERT INTO detections VALUES "
        i = 0
        if len(results) > 0:
            for det in results:
                if i < len(results) - 1:
                    query += str(det.serialize()) + ","
                else:
                    query += str(det.serialize())
                i += 1
            cursor.execute(query)
            conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()


def _insert_extractedsources(conn, image_id):
    """Insert all extracted sources with their properties

    Insert all detected sources and some derived properties into the
    extractedsources table.

    """

    try:
        cursor = conn.cursor()
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
  SELECT %s
        ,CAST(FLOOR(ldecl) AS INTEGER)
        ,lra
        ,ldecl
        ,lra_err * 3600
        ,ldecl_err * 3600
        ,COS(rad(ldecl)) * COS(rad(lra))
        ,COS(rad(ldecl)) * SIN(rad(lra))
        ,SIN(rad(ldecl))
        ,ldet_sigma
        ,lI_peak
        ,lI_peak_err
        ,lI_int
        ,lI_int_err
    FROM detections
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
    procedures into the"extractedsources" table.

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
             AND SQRT((x0.ra - b0.wm_ra) * COS(rad(x0.decl))
                      * (x0.ra - b0.wm_ra) * COS(rad(x0.decl))
                      /(x0.ra_err * x0.ra_err +
                        b0.wm_ra_err * b0.wm_ra_err)
                     +(x0.decl - b0.wm_decl) * (x0.decl - b0.wm_decl)
                      /(x0.decl_err * x0.decl_err +
                        b0.wm_decl_err * b0.wm_decl_err)
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
          )
          SELECT assoc_xtrsrc_id
                ,xtrsrc_id
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
          )
          SELECT assoc_xtrsrc_id
                ,assoc_xtrsrc_id
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

    try:
        cursor = conn.cursor()
        query = """\
        INSERT INTO assocxtrsources
          (xtrsrc_id
          ,assoc_xtrsrc_id
          )
          SELECT xtrsrc_id
                ,assoc_xtrsrc_id
            FROM temprunningcatalog
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

    # Since Jun2010 version we cannot use the massive (but simple) update
    # statement anymore.
    # Therefore, unfortunately, we cursor through the tempsources table
    # TODO: However, it has not been checked yet, whether it is working again
    # in the latest version.
    ##+--------------------------------------------
    ##UPDATE multcatbasesources
    ##  SET zone = (
    ##      SELECT zone
    ##      FROM tempmultcatbasesources
    ##      WHERE tempmultcatbasesources.xtrsrc_id =
    ##            multcatbasesources.xtrsrc_id
    ##      )
    ##     ,ra_avg = (
    ##         SELECT ra_avg
    ##         FROM tempmultcatbasesources
    ##         WHERE tempmultcatbasesources.xtrsrc_id =
    ##               multcatbasesources.xtrsrc_id
    ##         )
    ##     ,decl_avg = (
    ##         SELECT decl_avg
    ##         FROM tempmultcatbasesources
    ##         WHERE tempmultcatbasesources.xtrsrc_id =
    ##               multcatbasesources.xtrsrc_id
    ##         )
    ##     ,ra_err_avg = (
    ##         SELECT ra_err_avg
    ##         FROM tempmultcatbasesources
    ##         WHERE tempmultcatbasesources.xtrsrc_id =
    ##               multcatbasesources.xtrsrc_id
    ##                   )
    ##     ,decl_err_avg = (
    ##         SELECT decl_err_avg
    ##         FROM tempmultcatbasesources
    ##         WHERE tempmultcatbasesources.xtrsrc_id =
    ##               multcatbasesources.xtrsrc_id
    ##                     )
    ##     ,x = (SELECT x
    ##             FROM tempmultcatbasesources
    ##            WHERE tempmultcatbasesources.xtrsrc_id =
    ##                  multcatbasesources.xtrsrc_id
    ##          )
    ##     ,y = (SELECT y
    ##             FROM tempmultcatbasesources
    ##            WHERE tempmultcatbasesources.xtrsrc_id =
    ##                  multcatbasesources.xtrsrc_id
    ##          )
    ##     ,z = (SELECT z
    ##             FROM tempmultcatbasesources
    ##            WHERE tempmultcatbasesources.xtrsrc_id =
    ##                  multcatbasesources.xtrsrc_id
    ##          )
    ##     ,datapoints = (
    ##         SELECT datapoints
    ##         FROM tempmultcatbasesources
    ##         WHERE tempmultcatbasesources.xtrsrc_id =
    ##               multcatbasesources.xtrsrc_id
    ##                   )
    ##     ,avg_weighted_ra = (
    ##         SELECT avg_weighted_ra
    ##         FROM tempmultcatbasesources
    ##         WHERE tempmultcatbasesources.xtrsrc_id =
    ##               multcatbasesources.xtrsrc_id
    ##                        )
    ##     ,avg_weighted_decl = (
    ##         SELECT avg_weighted_decl
    ##         FROM tempmultcatbasesources
    ##         WHERE tempmultcatbasesources.xtrsrc_id =
    ##               multcatbasesources.xtrsrc_id
    ##                          )
    ##     ,avg_ra_weight = (
    ##         SELECT avg_ra_weight
    ##         FROM tempmultcatbasesources
    ##         WHERE tempmultcatbasesources.xtrsrc_id =
    ##               multcatbasesources.xtrsrc_id
    ##                      )
    ##     ,avg_decl_weight = (
    ##         SELECT avg_decl_weight
    ##         FROM tempmultcatbasesources
    ##         WHERE tempmultcatbasesources.xtrsrc_id =
    ##         multcatbasesources.xtrsrc_id
    ##                        )
    ##WHERE EXISTS (
    ##    SELECT xtrsrc_id
    ##    FROM tempmultcatbasesources
    ##    WHERE tempmultcatbasesources.xtrsrc_id =
    ##    multcatbasesources.xtrsrc_id
    ##             )
    ##+--------------------------------------------

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
        y = cursor.fetchall()
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
        for k in range(len(y)):
            #print y[k][0], y[k][1], y[k][2]
            cursor.execute(query, (y[k][0],
                                   y[k][1],
                                   y[k][2],
                                   y[k][3],
                                   y[k][4],
                                   y[k][5],
                                   y[k][6],
                                   y[k][7],
                                   y[k][8],
                                   y[k][9],
                                   y[k][10],
                                   y[k][11],
                                   y[k][12],
                                   y[k][13],
                                   y[k][14],
                                   y[k][15],
                                   y[k][16],
                                   y[k][17],
                                   y[k][18]
                                 ))
            if (k % 100 == 0):
                print "\t\tUpdate iter:", k
        conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()


def _count_known_sources(conn, image_id, deRuiter_r):
    """Count number of extracted sources that are know in the running
    catalog"""

    try:
        cursor = conn.cursor()
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
   AND SQRT((x0.ra - b0.wm_ra) * COS(rad(x0.decl))
            * (x0.ra - b0.wm_ra) * COS(rad(x0.decl))
            / (x0.ra_err * x0.ra_err + b0.wm_ra_err * b0.wm_ra_err)
           + (x0.decl - b0.wm_decl) * (x0.decl - b0.wm_decl)
            / (x0.decl_err * x0.decl_err + b0.wm_decl_err *
               b0.wm_decl_err)
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

    try:
        cursor = conn.cursor()
        query = """\
        INSERT INTO assocxtrsources
          (xtrsrc_id
          ,assoc_xtrsrc_id
          )
          SELECT x1.xtrsrcid as xtrsrc_id
                ,x1.xtrsrcid as assoc_xtrsrc_id
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
                   AND SQRT((x0.ra - b0.wm_ra) * COS(rad(x0.decl))
                            * (x0.ra - b0.wm_ra) * COS(rad(x0.decl))
                            /(x0.ra_err * x0.ra_err
                             + b0.wm_ra_err * b0.wm_ra_err
                             )
                           +(x0.decl - b0.wm_decl) * (x0.decl - b0.wm_decl)
                            /(x0.decl_err * x0.decl_err
                             + b0.wm_decl_err * b0.wm_decl_err
                             )
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
           AND b0.x * x0.x + b0.y * x0.y + b0.z * x0.z >
                     COS(rad(0.025))
           AND SQRT((x0.ra - b0.wm_ra) * COS(rad(x0.decl))
                    * (x0.ra - b0.wm_ra) * COS(rad(x0.decl))
                    /(x0.ra_err * x0.ra_err
                     + b0.wm_ra_err * b0.wm_ra_err
                     )
                   +(x0.decl - b0.wm_decl) * (x0.decl - b0.wm_decl)
                    /(x0.decl_err * x0.decl_err
                     + b0.wm_decl_err * b0.wm_decl_err
                     )
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


def associate_extracted_sources(conn, image_id, deRuiter_r=DERUITER_R):
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

    try:
        cursor = conn.cursor()
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
   AND datapoints > 1
   AND (sqrt(datapoints*(avg_I_peak_sq - avg_I_peak*avg_I_peak) /
             (datapoints-1)) / avg_I_peak > %s
        OR (datapoints/(datapoints-1)) *
            (avg_weighted_I_peak_sq -
             avg_weighted_I_peak * avg_weighted_I_peak /
             avg_weight_peak) > %s
       )
"""
        cursor.execute(query, (dsid, V_lim, eta_lim))
        y = cursor.fetchall()
        if len(y) > 0:
            print "Alert!"
        for i in range(len(y)):
            print "xtrsrc_id =", y[i][0]
            print "\tdatapoints =", y[i][2]
            print "\tv_nu =", y[i][7]
            print "\teta_nu =", y[i][8]
        conn.commit()
    except db.Error, e:
        logging.warn("Failed on query %s" % query)
        raise
    finally:
        cursor.close()


def variability_detection(conn, dsid, V_lim, eta_lim):
    """Detect variability in extracted sources compared to the previous
    detections"""

    #sources = _select_variability_indices(conn, dsid, V_lim, eta_lim)
    _select_variability_indices(conn, dsid, V_lim, eta_lim)


def associate_catalogued_sources_in_area(conn, ra, dec, search_radius):
    """Detection of variability in the extracted sources as
    compared their previous detections.
    """
    pass
    # the sources in the current image need to be matched to the
    # list of sources from the merged cross-correlated catalogues
