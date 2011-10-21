# -*- coding: utf-8 -*-

#
# LOFAR Transients Key Project
#
import sys, pylab, time
from scipy import *
from scipy import optimize
import numpy as np
# Local tkp_lib functionality
import monetdb.sql as db
import logging
from tkp.config import config

DERUITER_R = config['source_association']['deruiter_radius']/3600.
print "DERUITER_R =",DERUITER_R

def cross_associate_cataloged_sources(conn 
                                     ,c
                                     ,zone_min 
                                     ,zone_max 
                                     ,deRuiter_r=None 
                                     ):

    if not deRuiter_r:
        deRuiter_r = DERUITER_R
        
    # I know the cat_id's of the VLSS, WENSSm, WENSSp and NVSS, resp.
    #c = [4, 5, 6, 3]
    #c = [3, 4, 5, 6]
    #c = [4, 5, 6, 3]
    
    ra_lims = [[0.0, 90.0], [90.0, 180.0], [180.0, 270.0], [270.0, 360.0]]
    # Here we override the ra_min/max
    zones = range(zone_min, zone_max, 1)
    for zone in zones:
        print "Working in zone =", zone
        for i in range(len(c)):
            print "\tBusy with cat_id = ", c[i]
            for j in range(len(ra_lims)):
                ra_min, ra_max = ra_lims[j]
                print "\t\tBusy with ra_lims = [", ra_min, ",", ra_max, ")"
                print "\t\t\t(1): " + time.strftime("%Y-%m-%d %H:%M:%S")
                _empty_selected_catsources(conn)
                print "\t\t\t(2): " + time.strftime("%Y-%m-%d %H:%M:%S")
                _empty_tempmergedcatalogs(conn)
                print "\t\t\t(3): " + time.strftime("%Y-%m-%d %H:%M:%S")
                _insert_selected_catsources(conn, c[i], zone, ra_min, ra_max)
                print "\t\t\t\tNumber of seletedcatsources: ", _count_selectedcatsources(conn)
                print "\t\t\t\tNumber of merged cataloged sources in this area: ", _count_mergedcatalogs(conn, zone, ra_min,ra_max)
                print "\t\t\t(4): " + time.strftime("%Y-%m-%d %H:%M:%S")
                _insert_tempmergedcatalogs(conn, c[i], zone, ra_min, ra_max, deRuiter_r)
                print "\t\t\t(5): " + time.strftime("%Y-%m-%d %H:%M:%S")
                _flag_multiple_counterparts_in_mergedcatalogs(conn)
                print "\t\t\t(6): " + time.strftime("%Y-%m-%d %H:%M:%S")
                _insert_multiple_crossassocs(conn)
                print "\t\t\t(7): " + time.strftime("%Y-%m-%d %H:%M:%S")
                _insert_first_of_multiple_crossassocs(conn)
                print "\t\t\t(8): " + time.strftime("%Y-%m-%d %H:%M:%S")
                _flag_swapped_multiple_crossassocs(conn)
                print "\t\t\t(9): " + time.strftime("%Y-%m-%d %H:%M:%S")
                _insert_multiple_crossassocs_mergedcat(conn)
                print "\t\t\t(10): " + time.strftime("%Y-%m-%d %H:%M:%S")
                _flag_old_multiple_assocs_mergedcat(conn)
                print "\t\t\t(11): " + time.strftime("%Y-%m-%d %H:%M:%S")
                _flag_multiple_assocs(conn)
                print "\t\t\t(12): " + time.strftime("%Y-%m-%d %H:%M:%S")
                #+-----------------------------------------------------+
                #| After all this, we are now left with the 1-1 assocs |
                #+-----------------------------------------------------+
                _insert_single_crossassocs(conn)
                print "\t\t\t(13): " + time.strftime("%Y-%m-%d %H:%M:%S")
                _update_mergedcatalogs(conn)
                print "\t\t\t(14): " + time.strftime("%Y-%m-%d %H:%M:%S")
                _empty_tempmergedcatalogs(conn)
                print "\t\t\t(15): " + time.strftime("%Y-%m-%d %H:%M:%S")
                _count_known_sources(conn, zone, ra_min, ra_max, deRuiter_r)
                print "\t\t\t(16): " + time.strftime("%Y-%m-%d %H:%M:%S")
                _insert_new_assocs(conn, zone, ra_min, ra_max, deRuiter_r)
                print "\t\t\t(17): " + time.strftime("%Y-%m-%d %H:%M:%S")
                _insert_new_source_mergedcatalogs(conn, c[i], zone, ra_min, ra_max, deRuiter_r)
                print "\t\t\t(18): " + time.strftime("%Y-%m-%d %H:%M:%S")
                _empty_selected_catsources(conn)
                print "\t\t\t(19): " + time.strftime("%Y-%m-%d %H:%M:%S")
                _update_fluxes_mergedcatalogs(conn, c, zone, ra_min, ra_max)
                print "\t\t\t(20): " + time.strftime("%Y-%m-%d %H:%M:%S")
                _update_spectralindices_mergedcatalogs(conn, c, zone, ra_min, ra_max)
                print "\t\t\t(21): " + time.strftime("%Y-%m-%d %H:%M:%S")
        print "Number of merged cataloged sources in this zone: ", _count_mergedcatalogs(conn, zone)
    print "Number of merged cataloged sources: ", _count_mergedcatalogs(conn)

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

def _insert_selected_catsources(conn, cat_id, zone, ra_min, ra_max):
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
     AND c0.zone = %s
     AND c0.ra >= %s 
     AND c0.ra < %s
        """
     # Taken out to work by zones
     #AND c0.zone BETWEEN CAST(FLOOR(CAST(%s AS DOUBLE) - 0.025) as INTEGER)
     #                AND CAST(FLOOR(CAST(%s AS DOUBLE) + 0.025) as INTEGER)
     #AND c0.decl BETWEEN CAST(%s AS DOUBLE) - 0.025
     #                AND CAST(%s AS DOUBLE) + 0.025
     #AND c0.ra BETWEEN CAST(%s AS DOUBLE) - alpha(0.025, %s)
     #              AND CAST(%s AS DOUBLE) + alpha(0.025, %s)
        cursor.execute(query, (cat_id 
                              ,zone
                              ,ra_min
                              ,ra_max
                              ))
        conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()

def _insert_tempmergedcatalogs(conn, cat_id, zone, ra_min, ra_max, deRuiter_r):
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
  ,assoc_cat_id
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
  ,i_peak
  ,i_int
  )
  SELECT catsrc_id
        ,assoc_catsrc_id
        ,assoc_cat_id
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
        ,i_peak
        ,i_int
    FROM (SELECT t0.catsrc_id
                ,t0.assoc_catsrc_id
                ,t0.assoc_cat_id
                ,t0.datapoints
                ,CAST(FLOOR(t0.wm_decl/1.0) AS INTEGER) AS zone
                ,t0.wm_ra
                ,t0.wm_decl
                ,t0.wm_ra_err
                ,t0.wm_decl_err
                ,t0.avg_wra
                ,t0.avg_wdecl
                ,t0.avg_weight_ra
                ,t0.avg_weight_decl
                ,COS(RADIANS(t0.wm_decl)) * COS(RADIANS(t0.wm_ra)) AS x
                ,COS(RADIANS(t0.wm_decl)) * SIN(RADIANS(t0.wm_ra)) AS y
                ,SIN(RADIANS(t0.wm_decl)) AS z
                ,i_peak
                ,i_int
            FROM (SELECT m0.catsrc_id as catsrc_id
                        ,s0.catsrc_id as assoc_catsrc_id
                        ,%s as assoc_cat_id
                        ,datapoints + 1 AS datapoints
                        ,(datapoints * m0.avg_wra * s0.ra_err * s0.ra_err + s0.ra)
                         /
                         (datapoints * m0.avg_weight_ra * s0.ra_err * s0.ra_err + 1.0)
                         AS wm_ra
                        ,(datapoints * m0.avg_wdecl * s0.decl_err * s0.decl_err + s0.decl)
                         /
                         (datapoints * m0.avg_weight_decl * s0.decl_err * s0.decl_err + 1.0)
                         AS wm_decl
                        ,SQRT(1.0 
                             / (datapoints * m0.avg_weight_ra + 1 / (s0.ra_err * s0.ra_err))
                             ) AS wm_ra_err
                        ,SQRT(1.0 
                             / (datapoints * m0.avg_weight_decl + 1 / (s0.decl_err * s0.decl_err)) 
                             ) AS wm_decl_err
                        ,(datapoints * m0.avg_wra + s0.ra / (s0.ra_err * s0.ra_err))
                         / (datapoints + 1) AS avg_wra
                        ,(datapoints * m0.avg_wdecl + s0.decl / (s0.decl_err * s0.decl_err))
                         / (datapoints + 1) AS avg_wdecl
                        ,(datapoints * m0.avg_weight_ra + 1 / (s0.ra_err * s0.ra_err))
                         / (datapoints + 1) AS avg_weight_ra
                        ,(datapoints * m0.avg_weight_decl + 1 / (s0.decl_err * s0.decl_err))
                         / (datapoints + 1) AS avg_weight_decl
                        ,s0.i_peak
                        ,s0.i_int
                    FROM mergedcatalogs m0
                        ,selectedcatsources s0
                   WHERE m0.zone BETWEEN %s - 1
                                     AND %s + 1
                     AND m0.wm_decl BETWEEN %s - 0.025
                                        AND %s + 1.025
                     AND m0.wm_ra BETWEEN %s - alpha(0.025, %s)
                                      AND %s + alpha(0.025, %s)
                     AND SQRT(  (s0.ra * COS(RADIANS(s0.decl)) - m0.wm_ra * COS(RADIANS(m0.wm_decl)))
                              * (s0.ra * COS(RADIANS(s0.decl)) - m0.wm_ra * COS(RADIANS(m0.wm_decl)))
                              / (s0.ra_err * s0.ra_err + m0.wm_ra_err * m0.wm_ra_err)
                             + (s0.decl - m0.wm_decl) * (s0.decl - m0.wm_decl)
                              / (s0.decl_err * s0.decl_err + m0.wm_decl_err * m0.wm_decl_err)
                             ) < %s
                 ) t0
         ) t1
"""
        # NOTE for above query: Since we use zone as input param
        # to set the decl boundaries we look 90" below the zone (zone - 0.025)
        # and 90" above the zone (zone + 1.025)!

        # Taken out, might slow query down:
        # AND m0.x * s0.x + m0.y * s0.y + m0.z * s0.z > 0.9999999048070578
        print "\t\t\t\tExecuting _insert_tempmergedcatalogs() ..."
        cursor.execute(query, (cat_id, zone, zone, zone, zone, ra_min, zone+0.5, ra_max, zone+0.5, deRuiter_r))
        conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        hv = [cat_id, deRuiter_r]
        logging.warn("host variables: %s" % hv)
        raise
    finally:
        cursor.close()


def _flag_multiple_counterparts_in_mergedcatalogs(conn):
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
                      ,MIN(SQRT((s0.ra - m0.wm_ra) * COS(RADIANS(s0.decl))
                                * (s0.ra - m0.wm_ra) * COS(RADIANS(s0.decl))
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
                                                 FROM tempmergedcatalogs
                                               GROUP BY assoc_catsrc_id
                                               HAVING COUNT(*) > 1
                                              )
                   AND tm0.catsrc_id = m0.catsrc_id
                   AND tm0.assoc_catsrc_id = s0.catsrc_id
                GROUP BY tm0.assoc_catsrc_id
               ) t0
              ,(SELECT tm1.catsrc_id
                      ,tm1.assoc_catsrc_id
                      ,SQRT( (s1.ra - m1.wm_ra) * COS(RADIANS(s1.decl))
                            *(s1.ra - m1.wm_ra) * COS(RADIANS(s1.decl))
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
                                                 FROM tempmergedcatalogs
                                               GROUP BY assoc_catsrc_id
                                               HAVING COUNT(*) > 1
                                              )
                   AND tm1.catsrc_id = m1.catsrc_id
                   AND tm1.assoc_catsrc_id = s1.catsrc_id
               ) t1
         WHERE t1.assoc_catsrc_id = t0.assoc_catsrc_id
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
              FROM tempmergedcatalogs
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

def _insert_multiple_crossassocs(conn):
    """Insert sources with multiple associations

    -2- Now, we take care of the sources in the running catalogue that
    have more than one counterpart among the extracted sources.

    We now make two entries in the running catalogue, in stead of the
    one we had before. Therefore, we 'swap' the ids.
    """
    #TODO: check where clause, assoccrosscatsources should have entries for 
    # assoc_lr_method 8 and 9.

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
                ,3600 * DEGREES(2 * ASIN(SQRT((m.x - s.x) * (m.x - s.x)
                                          + (m.y - s.y) * (m.y - s.y)
                                          + (m.z - s.z) * (m.z - s.z)
                                          ) / 2) ) AS assoc_distance_arcsec
                ,3600 * sqrt(
                    ( (m.wm_ra * cos(RADIANS(m.wm_decl)) - s.ra * cos(RADIANS(s.decl)))
                     *(m.wm_ra * cos(RADIANS(m.wm_decl)) - s.ra * cos(RADIANS(s.decl)))
                    ) 
                    / (m.wm_ra_err * m.wm_ra_err + s.ra_err * s.ra_err)
                    + ((m.wm_decl - s.decl) * (m.wm_decl - s.decl)) 
                    / (m.wm_decl_err * m.wm_decl_err + s.decl_err * s.decl_err)
                            ) as assoc_r
                ,9
            FROM tempmergedcatalogs t
                ,mergedcatalogs m
                ,selectedcatsources s
           WHERE t.catsrc_id = m.catsrc_id
             AND t.assoc_catsrc_id = s.catsrc_id
             AND t.catsrc_id IN (SELECT catsrc_id
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


def _insert_first_of_multiple_crossassocs(conn):
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
                ,8
            FROM tempmergedcatalogs
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


def _flag_swapped_multiple_crossassocs(conn):
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


def _insert_multiple_crossassocs_mergedcat(conn):
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
            FROM tempmergedcatalogs
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


def _flag_old_multiple_assocs_mergedcat(conn):
    """Here the old assocs in runcat will be deleted."""

    # TODO: Consider setting row to inactive instead of deleting
    try:
        cursor = conn.cursor()
        query = """\
        DELETE
          FROM mergedcatalogs
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


def _flag_multiple_assocs(conn):
    """Delete the multiple assocs from the temporary running catalogue table"""

    try:
        cursor = conn.cursor()
        query = """\
        DELETE
          FROM tempmergedcatalogs
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


def _insert_single_crossassocs(conn):
    """Insert remaining 1-1 associations into assocxtrsources table"""

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
          SELECT t.catsrc_id
                ,t.assoc_catsrc_id
                ,3600 * DEGREES(2 * ASIN(SQRT((m.x - s.x) * (m.x - s.x)
                                          + (m.y - s.y) * (m.y - s.y)
                                          + (m.z - s.z) * (m.z - s.z)
                                          ) / 2) ) AS assoc_distance_arcsec
                ,3600 * sqrt(
                    ((m.wm_ra * cos(RADIANS(m.wm_decl)) 
                     - s.ra * cos(RADIANS(s.decl))) 
                    * (m.wm_ra * cos(RADIANS(m.wm_decl)) 
                     - s.ra * cos(RADIANS(s.decl)))) 
                    / (m.wm_ra_err * m.wm_ra_err + s.ra_err*s.ra_err)
                    +
                    ((m.wm_decl - s.decl) * (m.wm_decl - s.decl)) 
                    / (m.wm_decl_err * m.wm_decl_err + s.decl_err*s.decl_err)
                            ) as assoc_r
                ,10
            FROM tempmergedcatalogs t
                ,mergedcatalogs m
                ,selectedcatsources s
           WHERE t.catsrc_id = m.catsrc_id
             AND t.assoc_catsrc_id = s.catsrc_id
        """
        cursor.execute(query)
        conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()


def _update_mergedcatalogs(conn):
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
              ,catsrc_id
          FROM tempmergedcatalogs
        """
        cursor.execute(query)
        y = cursor.fetchall()
        print "\t\t\t\tHave to iterate over UPDATE " + str(len(y)) + " times..."
        query = """\
UPDATE mergedcatalogs
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
WHERE catsrc_id = %s
"""
        for k in range(len(y)):
            #print y[k][0], y[k][1], y[k][2]
            cursor.execute(query, (y[k][0]
                                  ,y[k][1]
                                  ,y[k][2]
                                  ,y[k][3]
                                  ,y[k][4]
                                  ,y[k][5]
                                  ,y[k][6]
                                  ,y[k][7]
                                  ,y[k][8]
                                  ,y[k][9]
                                  ,y[k][10]
                                  ,y[k][11] 
                                  ,y[k][12]
                                  ,y[k][13]
                                 ))
            if (k % 100 == 0):
                print "\t\t\t\t\tUpdate iter:", k
        conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()


def _count_known_sources(conn, zone, ra_min, ra_max, deRuiter_r):
    """Count number of sources that are already known 
    in the mergedcatalogs"""

    try:
        cursor = conn.cursor()
        query = """\
SELECT s0.catsrc_id
  FROM selectedcatsources s0
      ,mergedcatalogs m0
 WHERE m0.zone BETWEEN %s - 1
                   AND %s + 1
   AND m0.wm_decl BETWEEN %s - 0.025
                      AND %s + 1.025
   AND m0.wm_ra BETWEEN %s - alpha(0.025, %s)
                    AND %s + alpha(0.025, %s)
   AND SQRT(  (s0.ra * COS(RADIANS(s0.decl)) - m0.wm_ra * COS(RADIANS(m0.wm_decl)))
            * (s0.ra * COS(RADIANS(s0.decl)) - m0.wm_ra * COS(RADIANS(m0.wm_decl)))
            / (s0.ra_err * s0.ra_err + m0.wm_ra_err * m0.wm_ra_err)
           + (s0.decl - m0.wm_decl) * (s0.decl - m0.wm_decl)
            / (s0.decl_err * s0.decl_err + m0.wm_decl_err * m0.wm_decl_err)
           ) < %s
"""
        cursor.execute(query, (zone, zone, zone, zone, ra_min, zone+0.5, ra_max, zone+0.5, deRuiter_r))
        y = cursor.fetchall()
        print "\t\t\t\tNumber of selectedcatsources known in meregdcatalogs (or sources in NOT IN): ", len(y)
        conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()


def _insert_new_assocs(conn, zone, ra_min, ra_max, deRuiter_r):
    """Insert new associations for unknown sources

    This inserts new associations for the sources that were not known
    in the running catalogue (i.e. they did not have an entry in the
    runningcatalog table).
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
          SELECT s1.catsrc_id as catsrc_id
                ,s1.catsrc_id as assoc_catsrc_id
                ,0
                ,0
                ,7
            FROM selectedcatsources s1
           WHERE s1.catsrc_id NOT IN (SELECT s0.catsrc_id
                                        FROM selectedcatsources s0
                                            ,mergedcatalogs m0
                                       WHERE m0.zone BETWEEN %s - 1
                                                         AND %s + 1
                                         AND m0.wm_decl BETWEEN %s - 0.025
                                                            AND %s + 1.025
                                         AND m0.wm_ra BETWEEN %s - alpha(0.025, %s)
                                                          AND %s + alpha(0.025, %s)
                                         AND SQRT(  (s0.ra * COS(RADIANS(s0.decl)) - m0.wm_ra * COS(RADIANS(m0.wm_decl)))
                                                  * (s0.ra * COS(RADIANS(s0.decl)) - m0.wm_ra * COS(RADIANS(m0.wm_decl)))
                                                  / (s0.ra_err * s0.ra_err + m0.wm_ra_err * m0.wm_ra_err)
                                                 + (s0.decl - m0.wm_decl) * (s0.decl - m0.wm_decl)
                                                  / (s0.decl_err * s0.decl_err + m0.wm_decl_err * m0.wm_decl_err)
                                                 ) < %s
                                     )
        """
        print "\t\t\t\tExecuting _insert_new_assocs() ..."
        cursor.execute(query, (zone, zone, zone, zone, ra_min, zone+0.5, ra_max, zone+0.5, deRuiter_r))
        conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()

def _count_selectedcatsources(conn):
    """Simply count the number of sources 
    that are currently in the mergedcatalogs table.

    """

    nr_of_sources = 0
    try:
        cursor = conn.cursor()
        query = """\
        SELECT COUNT(*)
          FROM selectedcatsources
        """
        cursor.execute(query)
        nr_of_sources = cursor.fetchall()[0]
        conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s; for reason %s" % (query, e))
        raise
    finally:
        cursor.close()
    return nr_of_sources

def _count_mergedcatalogs(conn, zone=None, ra_min=None, ra_max=None):
    """Simply count the number of sources 
    that are currently in the mergedcatalogs table.

    """
    
    nr_of_sources = 0
    try:
        cursor = conn.cursor()
        if not zone and not ra_min and not ra_max:
            query = """\
            SELECT COUNT(*)
              FROM mergedcatalogs
            """
            cursor.execute(query)
        elif not ra_min and not ra_max:
            query = """\
            SELECT COUNT(*)
              FROM mergedcatalogs
             WHERE zone = %s
            """
            cursor.execute(query, (int(zone),))
        else:
            query = """\
            SELECT COUNT(*)
              FROM mergedcatalogs
             WHERE zone = %s
               AND wm_ra BETWEEN %s AND %s
            """
            cursor.execute(query, (int(zone),ra_min, ra_max))
        nr_of_sources = cursor.fetchall()[0][0]
        conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s; for reason %s." % (query, e))
        raise
    finally:
        cursor.close()
    return nr_of_sources


def _insert_new_source_mergedcatalogs(conn, cat_id, zone, ra_min, ra_max, deRuiter_r):
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
    FROM selectedcatsources s1
   WHERE s1.cat_id = %s
     AND s1.catsrc_id NOT IN (SELECT s0.catsrc_id
                                FROM selectedcatsources s0
                                    ,mergedcatalogs m0
                               WHERE s0.cat_id = %s
                                 AND m0.zone BETWEEN %s - 1
                                                 AND %s + 1
                                 AND m0.wm_decl BETWEEN %s - 0.025
                                                    AND %s + 1.025
                                 AND m0.wm_ra BETWEEN %s - alpha(0.025, %s)
                                                  AND %s + alpha(0.025, %s)
                                 AND SQRT(  (s0.ra * COS(RADIANS(s0.decl)) - m0.wm_ra * COS(RADIANS(m0.wm_decl)))
                                          * (s0.ra * COS(RADIANS(s0.decl)) - m0.wm_ra * COS(RADIANS(m0.wm_decl)))
                                          / (s0.ra_err * s0.ra_err + m0.wm_ra_err * m0.wm_ra_err)
                                         + (s0.decl - m0.wm_decl) * (s0.decl - m0.wm_decl)
                                          / (s0.decl_err * s0.decl_err + m0.wm_decl_err * m0.wm_decl_err)
                                         ) < %s
                            )
"""
        print "\t\t\t\tExecuting _insert_new_source_mergedcatalogs() ..."
        cursor.execute(query, (cat_id, cat_id, zone, zone, zone, zone, ra_min, zone+0.5, ra_max, zone+0.5, deRuiter_r))
        conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()


def _update_fluxes_mergedcatalogs(conn, c, zone, ra_min, ra_max):
    """ Reduce the number of sources to update by selecting the 
    region under inpsection for this zone and ra_lims
    """

    query = """\
    SELECT a.catsrc_id
          ,a.assoc_catsrc_id
          ,c.catsrcid
          ,c.cat_id
          ,c.i_peak_avg
          ,c.i_peak_avg_err
          ,c.i_int_avg 
          ,c.i_int_avg_err
      FROM assoccrosscatsources a
          ,catalogedsources c 
     WHERE a.assoc_catsrc_id = c.catsrcid 
       AND c.cat_id = %s
       AND c.zone BETWEEN %s - 1
                      AND %s + 1
       AND c.decl BETWEEN %s - 0.025
                      AND %s + 1.025
       AND c.ra BETWEEN %s - alpha(0.025, %s)
                    AND %s + alpha(0.025, %s)
    ORDER BY a.catsrc_id
    """
    print "\t\t\t\tExecuting _update_fluxes_mergedcatalogs() ..."
    for i in range(len(c)):
        print "\t\t\t\t\tc[", i, "] =", c[i]
        try:
            cursor = conn.cursor()
            cursor.execute(query, (c[i], zone, zone, zone, zone, ra_min, zone+0.5, ra_max, zone+0.5))
            results = zip(*cursor.fetchall())
        except db.Error, e:
            logging.warn("Failed on query %s; for reason %s " % (query,e))
            raise
        
        if len(results) != 0:
            catsrc_id = results[0]
            assoc_catsrc_id = results[1]
            catsrcid = results[2]
            cat_id = results[3]
            i_peak = results[4]
            i_peak_err = results[5]
            i_int = results[6]
            i_int_err = results[7]
            print "\t\t\t\t\t\tUpdating", len(catsrc_id), " records ..."
            for j in range(len(catsrc_id)):
                #print "catsrc_id[", j, "] =", catsrc_id[j], \
                #      "\ncat_id[", j, "] =", cat_id[j], \
                #      "\ni_peak[", j, "] =", i_peak[j], \
                #      "\ni_int[", j, "] =", i_int[j]
                if c[i] == 3:
                    uquery = """\
                    update mergedcatalogs
                       set i_peak_nvss = %s
                          ,i_peak_nvss_err = %s
                          ,i_int_nvss = %s
                          ,i_int_nvss_err = %s
                     where catsrc_id = %s
                    """
                elif c[i] == 4:
                    uquery = """\
                    update mergedcatalogs
                       set i_peak_vlss = %s
                          ,i_peak_vlss_err = %s
                          ,i_int_vlss = %s
                          ,i_int_vlss_err = %s
                     where catsrc_id = %s
                    """
                elif c[i] == 5:
                    uquery = """\
                    update mergedcatalogs
                       set i_peak_wenssm = %s
                          ,i_peak_wenssm_err = %s
                          ,i_int_wenssm = %s
                          ,i_int_wenssm_err = %s
                     where catsrc_id = %s
                    """
                elif c[i] == 6:
                    uquery = """\
                    update mergedcatalogs
                       set i_peak_wenssp = %s
                          ,i_peak_wenssp_err = %s
                          ,i_int_wenssp = %s
                          ,i_int_wenssp_err = %s
                     where catsrc_id = %s
                    """
                else:
                    logging.warn("No such catalogue %s for results %s" % c[i], catsrc_id[i])
                    raise
                
                try:
                    cursor.execute(uquery, (i_peak[j], i_peak_err[j], i_int[j], i_int_err[j], catsrc_id[j]))
                    conn.commit()
                except db.Error, e:
                    pquery = uquery % (i_peak[j], i_peak_err[j], i_int[j], i_int_err[j], catsrc_id[j])
                    logging.warn("Failed on query %s; for reason %s " % (pquery, e))
                    raise
    try:
        cursor.close()
    except db.Error, e:
        logging.warn("Failed closing cursor for reason %s " % (e,))
        raise

def _update_spectralindices_mergedcatalogs(conn, c, zone, ra_min, ra_max):
    """ """

    print "\t\t\t\t\tExecuting _update_spectralindices_mergedcatalogs() ..."
    queries = []
    v_wm_query = """\
    SELECT catsrc_id
          ,i_int_vlss
          ,i_int_wenssm
      FROM mergedcatalogs 
     WHERE i_int_vlss IS NOT NULL 
       AND i_int_wenssm IS NOT NULL
       AND zone BETWEEN %s - 1
                    AND %s + 1
       AND wm_decl BETWEEN %s - 0.025
                       AND %s + 1.025
       AND wm_ra BETWEEN %s - alpha(0.025, %s)
                     AND %s + alpha(0.025, %s)
    """
    queries.append(v_wm_query)
    v_wp_query = """\
    SELECT catsrc_id
          ,i_int_vlss
          ,i_int_wenssp
      FROM mergedcatalogs 
     WHERE i_int_vlss IS NOT NULL 
       AND i_int_wenssp IS NOT NULL
       AND zone BETWEEN %s - 1
                    AND %s + 1
       AND wm_decl BETWEEN %s - 0.025
                       AND %s + 1.025
       AND wm_ra BETWEEN %s - alpha(0.025, %s)
                     AND %s + alpha(0.025, %s)
    """
    queries.append(v_wp_query)
    v_n_query = """\
    SELECT catsrc_id
          ,i_int_vlss
          ,i_int_nvss
      FROM mergedcatalogs 
     WHERE i_int_vlss IS NOT NULL 
       AND i_int_nvss IS NOT NULL
       AND zone BETWEEN %s - 1
                    AND %s + 1
       AND wm_decl BETWEEN %s - 0.025
                       AND %s + 1.025
       AND wm_ra BETWEEN %s - alpha(0.025, %s)
                     AND %s + alpha(0.025, %s)
    """
    queries.append(v_n_query)
    wm_wp_query = """\
    SELECT catsrc_id
          ,i_int_wenssm
          ,i_int_wenssp
      FROM mergedcatalogs 
     WHERE i_int_wenssm IS NOT NULL 
       AND i_int_wenssp IS NOT NULL
       AND zone BETWEEN %s - 1
                    AND %s + 1
       AND wm_decl BETWEEN %s - 0.025
                       AND %s + 1.025
       AND wm_ra BETWEEN %s - alpha(0.025, %s)
                     AND %s + alpha(0.025, %s)
    """
    queries.append(wm_wp_query)
    wm_n_query = """\
    SELECT catsrc_id
          ,i_int_wenssm
          ,i_int_nvss
      FROM mergedcatalogs 
     WHERE i_int_wenssm IS NOT NULL 
       AND i_int_nvss IS NOT NULL
       AND zone BETWEEN %s - 1
                    AND %s + 1
       AND wm_decl BETWEEN %s - 0.025
                       AND %s + 1.025
       AND wm_ra BETWEEN %s - alpha(0.025, %s)
                     AND %s + alpha(0.025, %s)
    """
    queries.append(wm_n_query)
    wp_n_query = """\
    SELECT catsrc_id
          ,i_int_wenssp
          ,i_int_nvss
      FROM mergedcatalogs 
     WHERE i_int_wenssp IS NOT NULL 
       AND i_int_nvss IS NOT NULL
       AND zone BETWEEN %s - 1
                    AND %s + 1
       AND wm_decl BETWEEN %s - 0.025
                       AND %s + 1.025
       AND wm_ra BETWEEN %s - alpha(0.025, %s)
                     AND %s + alpha(0.025, %s)
    """
    queries.append(wp_n_query)
    v_wm_n_query = """\
    SELECT catsrc_id
          ,i_int_vlss
          ,i_int_wenssm
          ,i_int_nvss
          ,i_int_vlss_err
          ,i_int_wenssm_err
          ,i_int_nvss_err
      FROM mergedcatalogs 
     WHERE i_int_vlss IS NOT NULL 
       AND i_int_wenssm IS NOT NULL
       AND i_int_nvss IS NOT NULL
       AND zone BETWEEN %s - 1
                    AND %s + 1
       AND wm_decl BETWEEN %s - 0.025
                       AND %s + 1.025
       AND wm_ra BETWEEN %s - alpha(0.025, %s)
                     AND %s + alpha(0.025, %s)
    """
    queries.append(v_wm_n_query)
    try:
        cursor = conn.cursor()
        for i in range(len(queries)):
            cursor.execute(queries[i], (zone, zone, zone, zone, ra_min, zone+0.5, ra_max, zone+0.5))
            results = zip(*cursor.fetchall())
            if len(results) != 0:
                if queries[i] == v_wm_n_query:
                    catsrc_id = results[0]
                    i_int1 = results[1]
                    i_int2 = results[2]
                    i_int3 = results[3]
                    i_int_err1 = results[4]
                    i_int_err2 = results[5]
                    i_int_err3 = results[6]
                else:
                    catsrc_id = results[0]
                    i_int1 = results[1]
                    i_int2 = results[2]
                if i == 0:
                    for j in range(len(catsrc_id)):
                        alpha = -pylab.log10(i_int1[j]/i_int2[j]) / pylab.log10(74./325.)
                        uquery = """\
                        update mergedcatalogs
                           set alpha_v_wm = %s
                         where catsrc_id = %s
                        """
                        cursor.execute(uquery, (float(alpha), catsrc_id[j]))
                        conn.commit() 
                elif i == 1:
                    for j in range(len(catsrc_id)):
                        alpha = -pylab.log10(i_int1[j]/i_int2[j]) / pylab.log10(74./352.)
                        uquery = """\
                        update mergedcatalogs
                           set alpha_v_wp = %s
                         where catsrc_id = %s
                        """
                        cursor.execute(uquery, (float(alpha), catsrc_id[j]))
                        conn.commit() 
                elif i == 2:
                    for j in range(len(catsrc_id)):
                        alpha = -pylab.log10(i_int1[j]/i_int2[j]) / pylab.log10(74./1400.)
                        uquery = """\
                        update mergedcatalogs
                           set alpha_v_n = %s
                         where catsrc_id = %s
                        """
                        cursor.execute(uquery, (float(alpha), catsrc_id[j]))
                        conn.commit() 
                elif i == 3:
                    for j in range(len(catsrc_id)):
                        alpha = -pylab.log10(i_int1[j]/i_int2[j]) / pylab.log10(325./352.)
                        uquery = """\
                        update mergedcatalogs
                           set alpha_wm_wp = %s
                         where catsrc_id = %s
                        """
                        cursor.execute(uquery, (float(alpha), catsrc_id[j]))
                        conn.commit() 
                elif i == 4:
                    for j in range(len(catsrc_id)):
                        alpha = -pylab.log10(i_int1[j]/i_int2[j]) / pylab.log10(325./1400.)
                        uquery = """\
                        update mergedcatalogs
                           set alpha_wm_n = %s
                         where catsrc_id = %s
                        """
                        cursor.execute(uquery, (float(alpha), catsrc_id[j]))
                        conn.commit() 
                elif i == 5:
                    for j in range(len(catsrc_id)):
                        alpha = -pylab.log10(i_int1[j]/i_int2[j]) / pylab.log10(352./1400.)
                        uquery = """\
                        update mergedcatalogs
                           set alpha_wp_n = %s
                         where catsrc_id = %s
                        """
                        cursor.execute(uquery, (float(alpha), catsrc_id[j]))
                        conn.commit() 
                elif i == 6:
                    for j in range(len(catsrc_id)):
                        # y = mx + c
                        # logS = m lognu + c
                        # Here we fit straight line through three points
                        nu = np.array([74E6, 325E6, 1400E6])
                        f = np.array([i_int1[j], i_int2[j], i_int3[j]])
                        f_e = np.array([i_int_err1[j], i_int_err2[j], i_int_err3[j]])
                        alpha, chisq = fitspectralindex(nu, f, f_e)
                        #print "catsrc_id [", j, "] = ", catsrc_id[j], \
                        #      "\tspectral_index = ", -alpha, \
                        #      "\tchi_square = ", chisq
                        #alpha = -pylab.log10(i_int1[j]/i_int2[j]) / pylab.log10(352./1400.)
                        uquery = """\
                        update mergedcatalogs
                           set alpha_v_wm_n = %s
                              ,chisq_v_wm_n = %s
                         where catsrc_id = %s
                        """
                        cursor.execute(uquery, (float(-alpha), float(chisq), catsrc_id[j]))
                        conn.commit() 
    except db.Error, e:
        logging.warn("Failed on subuery %s" % uquery)
        logging.warn("Failed on query %s" % queries[i])
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


def get_merged_catalogs(conn, ra_centr_deg, decl_centr_deg, radius_arcsec=None):
    """
    """
    if not radius_arcsec:
        radius_arcsec = 90 # default search radius is 90 arcsec
    ra_rad = pylab.pi * ra_centr_deg / 180.
    decl_rad = pylab.pi * decl_centr_deg / 180.
    radius_deg = radius_arcsec / 3600.
    radius_rad = pylab.pi * (radius_arcsec / 648000.)
    try:
        cursor = conn.cursor()
        query = """\
SELECT catsrc_id
      ,datapoints
      ,m0.x * COS(%s)*COS(%s) + m0.y * COS(%s) * SIN(%s) + m0.z * SIN(%s)
       AS distance_arcsec
      ,wm_ra
      ,wm_decl
      ,wm_ra_err
      ,wm_decl_err
      ,i_int_vlss
      ,i_int_wenssm
      ,i_int_wenssp
      ,i_int_nvss
      ,alpha_v_wm
      ,alpha_v_wp
      ,alpha_v_n
      ,alpha_wm_wp
      ,alpha_wm_n
      ,alpha_wp_n
      ,alpha_v_wm_n
      ,chisq_v_wm_n
  FROM mergedcatalogs m0
 WHERE m0.zone BETWEEN CAST(FLOOR(CAST(%s AS DOUBLE) - %s) as INTEGER)
                   AND CAST(FLOOR(CAST(%s AS DOUBLE) + %s) as INTEGER)
   AND m0.wm_decl BETWEEN CAST(%s AS DOUBLE) - %s
                      AND CAST(%s AS DOUBLE) + %s
   AND m0.wm_ra BETWEEN CAST(%s AS DOUBLE) - alpha(%s, %s)
                    AND CAST(%s AS DOUBLE) + alpha(%s, %s)
   AND m0.x * COS(%s)*COS(%s) + m0.y * COS(%s) * SIN(%s) + m0.z * SIN(%s) > COS(%s)
ORDER BY datapoints DESC
        ,i_int_vlss DESC
"""
        cursor.execute(query, (decl_rad
                              ,ra_rad
                              ,decl_rad
                              ,ra_rad
                              ,decl_rad
                              ,decl_centr_deg
                              ,radius_deg
                              ,decl_centr_deg
                              ,radius_deg
                              ,decl_centr_deg
                              ,radius_deg
                              ,decl_centr_deg
                              ,radius_deg
                              ,ra_centr_deg
                              ,radius_deg
                              ,decl_centr_deg
                              ,ra_centr_deg
                              ,radius_deg
                              ,decl_centr_deg
                              ,decl_rad
                              ,ra_rad
                              ,decl_rad
                              ,ra_rad
                              ,decl_rad
                              ,radius_rad
                              ))
        y = cursor.fetchall()
        if len(y) > 0:
            for r in range(len(y)):
                print "r:", r, "y = ", y[r]
            return y
        else:
            print "EMPTY!"
            hv = [decl_rad
                 ,ra_rad
                 ,decl_rad
                 ,ra_rad
                 ,decl_rad
                 ,decl_rad
                 ,radius_rad
                 ,decl_rad
                 ,radius_rad
                 ,decl_rad
                 ,radius_rad
                 ,decl_rad
                 ,radius_rad
                 ,ra_rad
                 ,radius_rad
                 ,decl_rad
                 ,ra_rad
                 ,radius_rad
                 ,decl_rad
                 ,decl_rad
                 ,ra_rad
                 ,decl_rad
                 ,ra_rad
                 ,decl_rad
                 ,radius_rad
                 ]
            print "hv =", hv
            return None
    except db.Error, e:
        logging.warn("Failed on query %s" % query)
        raise
    finally:
        cursor.close()




def associate_catalogued_sources_in_area(conn, ra, dec, search_radius):
    """Detection of variability in the extracted sources as
    compared their previous detections.
    """
    pass
    # the sources in the current image need to be matched to the
    # list of sources from the merged cross-correlated catalogues

def fitspectralindex(freq,flux,flux_err):

    powerlaw = lambda x, amp, index: amp * (x**index)
    
    xdata=pylab.array(freq)
    ydata=pylab.array(flux)
    yerr=pylab.array(flux_err)
    
    logx = pylab.log10(xdata)
    logy = pylab.log10(ydata)
    logyerr = yerr / ydata
    
    fitfunc = lambda p, x: p[0] + p[1] * x
    errfunc = lambda p, x, y, err: (y - fitfunc(p, x)) / err
    
    pinit=[flux[0],-0.7]
    out = optimize.leastsq(errfunc, pinit, args=(logx, logy, logyerr), full_output=1)
    
    pfinal = out[0]
    covar = out[1]
    #print "pfinal =", pfinal
    #print "covar =", covar
    
    index = pfinal[1]
    amp = 10.0**pfinal[0]
    
    #print "index =",index
    #print "amp =",amp
    
    indexErr = sqrt( covar[0][0] )
    ampErr = sqrt( covar[1][1] ) * amp
    
    chisq=0
    for i in range(len(freq)):
        chisq += ((flux[i] - amp*(freq[i]**index))/flux_err[i])**2
    
    """
    fig = pylab.figure()
    ax1 = fig.add_subplot(211)
    ax1.plot(xdata, amp*(xdata**index), 'b--', label='Fit')     # Fit
    ax1.errorbar(xdata, ydata, yerr=yerr, fmt='o', color='red', label='Data')  # Data
    for i in range(len(ax1.get_xticklabels())):
        ax1.get_xticklabels()[i].set_size('x-large')
    for i in range(len(ax1.get_yticklabels())):
        ax1.get_yticklabels()[i].set_size('x-large')
    ax1.set_xlabel(r'Frequency', size='x-large')
    ax1.set_ylabel(r'Flux', size='x-large')
    ax1.grid(True)

    ax2 = fig.add_subplot(212)
    ax2.loglog(xdata, xdata*amp*(xdata**index), 'b-', label='Fit')
    ax2.errorbar(xdata, xdata*ydata, yerr=yerr, fmt='o', color='red', label='Data')  # Data
    for i in range(len(ax2.get_xticklabels())):
        ax2.get_xticklabels()[i].set_size('x-large')
    for i in range(len(ax2.get_yticklabels())):
        ax2.get_yticklabels()[i].set_size('x-large')
    ax2.set_xlabel(r'Frequency (log)', size='x-large')
    ax2.set_ylabel(r'Flux (log)', size='x-large')
    ax2.grid(True)

    pylab.savefig('power_law_fit.png')
    """

    return index,chisq

def get_bss_skymodel(conn):
    """Get spectral indices
    """

    try:
        cursor = conn.cursor()
        query = """\
        SELECT ra2hms(wm_ra)
              ,decl2dms(wm_decl)
              ,i_int_vlss
              ,0 
              ,0
              ,0
              ,i_int_nvss
              ,-alpha_v_n 
         FROM mergedcatalogs 
        WHERE i_int_vlss IS NOT NULL;"""
        cursor.execute(query)
        conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()

