# -*- coding: utf-8 -*-

#
# LOFAR Transients Key Project
#
import sys
# Local tkp_lib functionality
import monetdb.sql as db
import logging
from tkp.config import config

DERUITER_R = config['source_association']['deruiter_radius']

def cross_associate_cataloged_sources(conn 
                                     ,ra_min 
                                     ,ra_max 
                                     ,decl_min 
                                     ,decl_max 
                                     ,deRuiter_r=None 
                                     ):

    if not deRuiter_r:
        deRuiter_r = DERUITER_R
        
    # I know the cat_id's of the VLSS, WENSSm, WENSSp and NVSS, resp.
    #c = [4, 5, 6, 3]
    c = [4, 5]
    for i in range(len(c)):
        print "Busy with cat_id = ", c[i]
        _empty_selected_catsources(conn)
        _empty_tempmergedcatalogs(conn)
        _insert_selected_catsources(conn, c[i], ra_min, ra_max, decl_min, decl_max)
        _insert_tempmergedcatalogs(conn, c[i], ra_min, ra_max, decl_min, decl_max, deRuiter_r)
        if i > 0:
            sys.exit('Stopppp')
        #_flag_multiple_counterparts_in_runningcatalog(conn)
        #_insert_multiple_assocs(conn)
        #_insert_first_of_assocs(conn)
        #_flag_swapped_assocs(conn)
        #_insert_multiple_assocs_runcat(conn)
        #_flag_old_assocs_runcat(conn)
        #_flag_multiple_assocs(conn)
        #+-----------------------------------------------------+
        #| After all this, we are now left with the 1-1 assocs |
        #+-----------------------------------------------------+
        #_insert_single_assocs(conn)
        #_update_runningcatalog(conn)
        #_empty_temprunningcatalog(conn)
        #_count_known_sources(conn, image_id, deRuiter_r)
        #_insert_new_assocs(conn, image_id, deRuiter_r)
        _insert_new_source_mergedcatalogs(conn, c[i], ra_min, ra_max, decl_min, decl_max, deRuiter_r)

def _empty_selected_catsources(conn):
    """Initialize the temporary storage table

    Initialize the temporary table temprunningcatalog which contains
    the current observed sources.
    """

    try:
        cursor = conn.cursor()
        query = """DELETE FROM selectedcatsources"""
        cursor.execute(query)
        conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()

def _empty_tempmergedcatalogs(conn):
    """Initialize the temporary storage table

    Initialize the temporary table temprunningcatalog which contains
    the current observed sources.
    """

    try:
        cursor = conn.cursor()
        query = """DELETE FROM tempmergedcatalogs"""
        cursor.execute(query)
        conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()

def _insert_selected_catsources(conn, cat_id, ra_min, ra_max, decl_min, decl_max):
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
INSERT INTO selectedcatsources
  (catsrc_id
  ,cat_id
  ,zone
  ,ra
  ,decl
  ,ra_err
  ,decl_err
  ,x
  ,y
  ,z
  ,i_peak
  ,i_peak_err
  ,i_int
  ,i_int_err
  )
  SELECT c0.catsrcid
        ,c0.cat_id
        ,c0.zone
        ,c0.ra
        ,c0.decl
        ,c0.ra_err
        ,c0.decl_err
        ,c0.x
        ,c0.y
        ,c0.z
        ,c0.i_peak_avg
        ,c0.i_peak_avg_err
        ,c0.i_int_avg
        ,c0.i_int_avg_err
    FROM catalogedsources c0
   WHERE c0.cat_id = %s
     AND c0.zone BETWEEN CAST(FLOOR(CAST(%s AS DOUBLE) - 0.025) as INTEGER)
                     AND CAST(FLOOR(CAST(%s AS DOUBLE) + 0.025) as INTEGER)
     AND c0.decl BETWEEN CAST(%s AS DOUBLE) - 0.025
                     AND CAST(%s AS DOUBLE) + 0.025
     AND c0.ra BETWEEN CAST(%s AS DOUBLE) - alpha(0.025, %s)
                   AND CAST(%s AS DOUBLE) + alpha(0.025, %s)
"""
        cursor.execute(query, (cat_id 
                              ,decl_min 
                              ,decl_max
                              ,decl_min
                              ,decl_max
                              ,ra_min
                              ,decl_max
                              ,ra_max
                              ,decl_max
                              ))
        conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()

def _insert_tempmergedcatalogs(conn, cat_id, ra_min, ra_max, decl_min, decl_max, deRuiter_r):
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
INSERT INTO tempmergedcatalogs
  (catsrc_id
  ,assoc_catsrc_id
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
  ,i_int_vlss
  ,i_peak_vlss
  ,i_int_wenssm
  ,i_peak_wenssm
  ,i_int_wenssp
  ,i_peak_wenssp
  ,i_peak_nvss
  ,i_int_nvss
  )
  SELECT t0.catsrc_id
        ,t0.assoc_catsrc_id
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
        ,i_int_vlss
        ,i_peak_vlss
        ,i_int_wenssm
        ,i_peak_wenssm
        ,i_int_wenssp
        ,i_peak_wenssp
        ,i_peak_nvss
        ,i_int_nvss
    FROM (SELECT m0.catsrc_id as catsrc_id
                ,s0.catsrc_id as assoc_catsrc_id
                ,m0.datapoints + 1 AS datapoints
                ,((m0.datapoints * m0.avg_wra + s0.ra /
                  (s0.ra_err * s0.ra_err)) / (datapoints + 1))
                 /
                 ((datapoints * m0.avg_weight_ra + 1 /
                   (s0.ra_err * s0.ra_err)) / (datapoints + 1))
                 AS wm_ra
                ,((datapoints * m0.avg_wdecl + s0.decl /
                  (s0.decl_err * s0.decl_err)) / (datapoints + 1))
                 /
                 ((datapoints * m0.avg_weight_decl + 1 /
                   (s0.decl_err * s0.decl_err)) / (datapoints + 1))
                 AS wm_decl
                ,SQRT(1 / ((datapoints + 1) *
                  ((datapoints * m0.avg_weight_ra +
                    1 / (s0.ra_err * s0.ra_err)) / (datapoints + 1))
                          )
                     ) AS wm_ra_err
                ,SQRT(1 / ((datapoints + 1) *
                  ((datapoints * m0.avg_weight_decl +
                    1 / (s0.decl_err * s0.decl_err)) / (datapoints + 1))
                          )
                     ) AS wm_decl_err
                ,(datapoints * m0.avg_wra + s0.ra / (s0.ra_err * s0.ra_err))
                 / (datapoints + 1) AS avg_wra
                ,(datapoints * m0.avg_wdecl + s0.decl / (s0.decl_err * s0.decl_err))
                 / (datapoints + 1) AS avg_wdecl
                ,(datapoints * m0.avg_weight_ra + 1 /
                  (s0.ra_err * s0.ra_err))
                 / (datapoints + 1) AS avg_weight_ra
                ,(datapoints * m0.avg_weight_decl + 1 /
                  (s0.decl_err * s0.decl_err))
                 / (datapoints + 1) AS avg_weight_decl
                ,CASE WHEN cat_id = 4
                      THEN s0.I_peak
                      ELSE NULL
                 END AS i_peak_vlss
                ,CASE WHEN cat_id = 4
                      THEN s0.I_int
                      ELSE NULL
                 END AS i_int_vlss
                ,CASE WHEN cat_id = 5
                      THEN s0.I_peak
                      ELSE NULL
                 END AS i_peak_wenssm
                ,CASE WHEN cat_id = 5
                      THEN s0.I_int
                      ELSE NULL
                 END AS i_int_wenssm
                ,CASE WHEN cat_id = 6
                      THEN s0.I_peak
                      ELSE NULL
                 END AS i_peak_wenssp
                ,CASE WHEN cat_id = 6
                      THEN s0.I_int
                      ELSE NULL
                 END AS i_int_wenssp
                ,CASE WHEN cat_id = 3
                      THEN s0.I_peak
                      ELSE NULL
                 END AS i_peak_nvss
                ,CASE WHEN cat_id = 3
                      THEN s0.I_int
                      ELSE NULL
                 END AS i_int_nvss
            FROM mergedcatalogs m0
                ,selectedcatsources s0
           WHERE s0.cat_id = %s
             AND s0.zone BETWEEN CAST(FLOOR(CAST(%s AS DOUBLE) - 0.025) as INTEGER)
                             AND CAST(FLOOR(CAST(%s AS DOUBLE) + 0.025) as INTEGER)
             AND s0.decl BETWEEN CAST(%s AS DOUBLE) - 0.025
                             AND CAST(%s AS DOUBLE) + 0.025
             AND s0.ra BETWEEN CAST(%s AS DOUBLE) - alpha(0.025, %s)
                           AND CAST(%s AS DOUBLE) + alpha(0.025, %s)
             AND m0.zone BETWEEN CAST(FLOOR(CAST(%s AS DOUBLE) - 0.025) as INTEGER)
                             AND CAST(FLOOR(CAST(%s AS DOUBLE) + 0.025) as INTEGER)
             AND m0.wm_decl BETWEEN CAST(%s AS DOUBLE) - 0.025
                                AND CAST(%s AS DOUBLE) + 0.025
             AND m0.wm_ra BETWEEN CAST(%s AS DOUBLE) - alpha(0.025, %s)
                              AND CAST(%s AS DOUBLE) + alpha(0.025, %s)
             AND m0.x * s0.x + m0.y * s0.y + m0.z * s0.z > COS(rad(0.025))
             AND SQRT(  (s0.ra * COS(rad(s0.decl)) - m0.wm_ra * COS(rad(m0.wm_decl)))
                      * (s0.ra * COS(rad(s0.decl)) - m0.wm_ra * COS(rad(m0.wm_decl)))
                      / (s0.ra_err * s0.ra_err + m0.wm_ra_err * m0.wm_ra_err)
                     + (s0.decl - m0.wm_decl) * (s0.decl - m0.wm_decl)
                      / (s0.decl_err * s0.decl_err + m0.wm_decl_err * m0.wm_decl_err)
                     ) < %s
         ) t0
"""
        cursor.execute(query, (cat_id \
                              ,decl_min
                              ,decl_max
                              ,decl_min
                              ,decl_max
                              ,ra_min
                              ,decl_max
                              ,ra_max
                              ,decl_max
                              ,decl_min
                              ,decl_max
                              ,decl_min
                              ,decl_max
                              ,ra_min
                              ,decl_max
                              ,ra_max
                              ,decl_max
                              ,deRuiter_r \
                              ))
        #if image_id == 2:
        #    raise
        conn.commit()
        print "Query executed"
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
        SELECT t1.catsrc_id
              ,t1.assoc_catsrc_id
          FROM (SELECT tm0.assoc_catsrc_id
                      ,MIN(SQRT((s0.ra - m0.wm_ra) * COS(rad(s0.decl))
                                * (s0.ra - m0.wm_ra) * COS(rad(s0.decl))
                                / (s0.ra_err * s0.ra_err + m0.wm_ra_err *
                                   m0.wm_ra_err)
                               + (s0.decl - m0.wm_decl) *
                                 (s0.decl - m0.wm_decl)
                                / (s0.decl_err * s0.decl_err +
                                   m0.wm_decl_err * m0.wm_decl_err)
                               )
                          ) AS min_r1
                  FROM tempmergedcatalogs tm0
                      ,mergedcatalogs m0
                      ,selectedcatsources s0
                 WHERE tm0.assoc_catsrc_id IN (SELECT assoc_catsrc_id
                                                 FROM tempmergedcatalog
                                               GROUP BY assoc_catsrc_id
                                               HAVING COUNT(*) > 1
                                              )
                   AND tm0.xtrsrc_id = m0.xtrsrc_id
                   AND tm0.assoc_xtrsrc_id = s0.xtrsrcid
                GROUP BY tb0.assoc_xtrsrc_id
               ) t0
              ,(SELECT tm1.catsrc_id
                      ,tm1.assoc_catsrc_id
                      ,SQRT( (s1.ra - m1.wm_ra) * COS(rad(s1.decl))
                            *(s1.ra - m1.wm_ra) * COS(rad(s1.decl))
                            / (s1.ra_err * s1.ra_err +
                               m1.wm_ra_err * m1.wm_ra_err)
                           + (s1.decl - m1.wm_decl) * (s1.decl - m1.wm_decl)
                             / (s1.decl_err * s1.decl_err + m1.wm_decl_err *
                                m1.wm_decl_err)
                           ) AS r1
                  FROM tempmergedcatalogs tm1
                      ,mergedcatalogs m1
                      ,selectedcatsources s1
                 WHERE tm1.assoc_catsrc_id IN (SELECT assoc_catsrc_id
                                                 FROM tempmergedcatalog
                                               GROUP BY assoc_catsrc_id
                                               HAVING COUNT(*) > 1
                                              )
                   AND tm1.catsrc_id = m1.catsrc_id
                   AND tm1.assoc_catsrc_id = s1.catsrcid
               ) t1
         WHERE t1.assoc_xtrsrc_id = t0.assoc_xtrsrc_id
           AND t1.r1 > t0.min_r1
        """
        cursor.execute(query)
        results = zip(*cursor.fetchall())
        if len(results) != 0:
            catsrc_id = results[0]
            assoc_catsrc_id = results[1]
            # TODO: Consider setting row to inactive instead of deleting
            query = """\
            DELETE
              FROM tempmergedcatalog
             WHERE catsrc_id = %s
               AND assoc_catsrc_id = %s
            """
            for j in range(len(catsrc_id)):
                cursor.execute(query, (catsrc_id[j], assoc_catsrc_id[j]))
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
        INSERT INTO assoccrosscatsources
          (catsrc_id
          ,assoc_catsrc_id
          ,assoc_distance_arcsec
          ,assoc_r
          ,assoc_lr_method
          )
          SELECT t.assoc_catsrc_id
                ,t.catsrc_id
                ,3600 * deg(2 * ASIN(SQRT((m.x - s.x) * (m.x - s.x)
                                          + (m.y - s.y) * (m.y - s.y)
                                          + (m.z - s.z) * (m.z - s.z)
                                          ) / 2) ) AS assoc_distance_arcsec
                ,3600 * sqrt(
                    ( (m.wm_ra * cos(rad(m.wm_decl)) - s.ra * cos(rad(s.decl)))
                     *(m.wm_ra * cos(rad(m.wm_decl)) - s.ra * cos(rad(s.decl)))
                    ) 
                    / (m.wm_ra_err * m.wm_ra_err + s.ra_err * s.ra_err)
                    + ((m.wm_decl - s.decl) * (m.wm_decl - s.decl)) 
                    / (m.wm_decl_err * m.wm_decl_err + s.decl_err * s.decl_err)
                            ) as assoc_r
                ,7
            FROM tempmergedcatalogs t
                ,mergedcatalogs r
                ,selectedcatsources x
           WHERE t.catsrc_id = m.catsrc_id
             AND t.catsrc_id = s.catsrc_id
             AND t.catsrc_id IN (SELECT catsrc_id
                                   FROM tempmergedcatalog
                                 GROUP BY catsrc_id
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
        INSERT INTO assoccrosscatsources
          (catsrc_id
          ,assoc_catsrc_id
          ,assoc_distance_arcsec
          ,assoc_r
          ,assoc_lr_method
          )
          SELECT assoc_catsrc_id
                ,assoc_catsrc_id
                ,0
                ,0
                ,2
            FROM tempmergedcatalog
           WHERE catsrc_id IN (SELECT catsrc_id
                                 FROM tempmeregdcatalog
                               GROUP BY catsrc_id
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
          FROM assoccrosscatsources
         WHERE catsrc_id IN (SELECT catsrc_id
                               FROM tempmergedcatalogs
                             GROUP BY catsrc_id
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
        INSERT INTO mergedcatalogs
          (catsrc_id
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
          ,I_peak_vlss
          ,I_int_vlss
          ,I_peak_wenssm
          ,I_int_wenssm
          ,I_peak_wenssp
          ,I_int_wenssp
          ,I_peak_nvss
          ,I_int_nvss
          )
          SELECT assoc_catsrc_id
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
                ,I_peak_vlss
                ,I_int_vlss
                ,I_peak_wenssm
                ,I_int_wenssm
                ,I_peak_wenssp
                ,I_int_wenssp
                ,I_peak_nvss
                ,I_int_nvss
            FROM tempmergedcatalogs
           WHERE catsrc_id IN (SELECT catsrc_id
                                 FROM tempmergedcatalog
                               GROUP BY catsrc_id
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
          FROM mergedcatalog
         WHERE catsrc_id IN (SELECT catsrc_id
                               FROM tempmergedcatalog
                             GROUP BY catsrc_id
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
          FROM tempmergedcatalog
         WHERE catsrc_id IN (SELECT catsrc_id
                               FROM tempmergedcatalog
                             GROUP BY catsrc_id
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


def _insert_new_source_mergedcatalogs(conn, cat_id, ra_min, ra_max, decl_min, decl_max, deRuiter_r):
    """Insert new sources into the running catalog"""

    try:
        cursor = conn.cursor()
        query = """\
INSERT INTO mergedcatalogs
  (catsrc_id
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
  ,i_int_vlss
  ,i_peak_vlss
  ,i_int_wenssm
  ,i_peak_wenssm
  ,i_int_wenssp
  ,i_peak_wenssp
  ,i_peak_nvss
  ,i_int_nvss
  )
  SELECT s1.catsrc_id
        ,1
        ,s1.zone
        ,s1.ra
        ,s1.decl
        ,s1.ra_err
        ,s1.decl_err
        ,s1.ra / (s1.ra_err * s1.ra_err)
        ,s1.decl / (s1.decl_err * s1.decl_err)
        ,1 / (s1.ra_err * s1.ra_err)
        ,1 / (s1.decl_err * s1.decl_err)
        ,s1.x
        ,s1.y
        ,s1.z
        ,CASE WHEN cat_id = 4
              THEN s1.I_peak
              ELSE NULL
         END AS i_peak_vlss
        ,CASE WHEN cat_id = 4
              THEN s1.I_int
              ELSE NULL
         END AS i_int_vlss
        ,CASE WHEN cat_id = 5
              THEN s1.I_peak
              ELSE NULL
         END AS i_peak_wenssm
        ,CASE WHEN cat_id = 5
              THEN s1.I_int
              ELSE NULL
         END AS i_int_wenssm
        ,CASE WHEN cat_id = 6
              THEN s1.I_peak
              ELSE NULL
         END AS i_peak_wenssp
        ,CASE WHEN cat_id = 6
              THEN s1.I_int
              ELSE NULL
         END AS i_int_wenssp
        ,CASE WHEN cat_id = 3
              THEN s1.I_peak
              ELSE NULL
         END AS i_peak_nvss
        ,CASE WHEN cat_id = 3
              THEN s1.I_int
              ELSE NULL
         END AS i_int_nvss
    FROM selectedcatsources s1
   WHERE s1.cat_id = %s
     AND s1.catsrc_id NOT IN (SELECT s0.catsrc_id
                              FROM selectedcatsources s0
                                  ,mergedcatalogs m0
                             WHERE s0.cat_id = %s
                               AND s0.zone BETWEEN CAST(FLOOR(CAST(%s AS DOUBLE) - 0.025) as INTEGER)
                                               AND CAST(FLOOR(CAST(%s AS DOUBLE) + 0.025) as INTEGER)
                               AND s0.decl BETWEEN CAST(%s AS DOUBLE) - 0.025
                                               AND CAST(%s AS DOUBLE) + 0.025
                               AND s0.ra BETWEEN CAST(%s AS DOUBLE) - alpha(0.025, %s)
                                             AND CAST(%s AS DOUBLE) + alpha(0.025, %s)
                               AND m0.zone BETWEEN CAST(FLOOR(CAST(%s AS DOUBLE) - 0.025) as INTEGER)
                                               AND CAST(FLOOR(CAST(%s AS DOUBLE) + 0.025) as INTEGER)
                               AND m0.wm_decl BETWEEN CAST(%s AS DOUBLE) - 0.025
                                                  AND CAST(%s AS DOUBLE) + 0.025
                               AND m0.wm_ra BETWEEN CAST(%s AS DOUBLE) - alpha(0.025, %s)
                                                AND CAST(%s AS DOUBLE) + alpha(0.025, %s)
                               AND m0.x * s0.x + m0.y * s0.y + m0.z * s0.z > COS(rad(0.025))
                               AND SQRT(  (s0.ra * COS(rad(s0.decl)) - m0.wm_ra * COS(rad(m0.wm_decl)))
                                        * (s0.ra * COS(rad(s0.decl)) - m0.wm_ra * COS(rad(m0.wm_decl)))
                                        / (s0.ra_err * s0.ra_err + m0.wm_ra_err * m0.wm_ra_err)
                                       + (s0.decl - m0.wm_decl) * (s0.decl - m0.wm_decl)
                                        / (s0.decl_err * s0.decl_err + m0.wm_decl_err * m0.wm_decl_err)
                                       ) < %s
                            )
"""
        cursor.execute(query, (cat_id \
                              ,cat_id \
                              ,decl_min \
                              ,decl_max \
                              ,decl_min \
                              ,decl_max \
                              ,ra_min \
                              ,decl_max \
                              ,ra_max \
                              ,decl_max \
                              ,decl_min \
                              ,decl_max \
                              ,decl_min \
                              ,decl_max \
                              ,ra_min \
                              ,decl_max \
                              ,ra_max \
                              ,decl_max \
                              ,deRuiter_r \
                              ))
        conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()



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
