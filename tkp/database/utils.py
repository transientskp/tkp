# -*- coding: utf-8 -*-

#
# LOFAR Transients Key Project
#
# Bart Scheers, Evert Rol
#
# discovery@transientskp.org
#
import os
import sys
import math
import logging
import monetdb.sql as db
from tkp.config import config
# To do: any way we can get rid of this dependency?
#from tkp.sourcefinder.extract import Detection
#from .database import ENGINE

AUTOCOMMIT = config['database']['autocommit']
DERUITER_R = config['source_association']['deruiter_radius']
BG_DENSITY = config['source_association']['bg-density']

def insert_dataset(conn, description):
    """Insert dataset with discription as given by argument.

    DB function insertDataset() sets the necessary default values.
    """

    newdsid = None
    try:
        cursor = conn.cursor()
        query = """\
        SELECT insertDataset(%s)
        """
        cursor.execute(query, (description,))
        if not AUTOCOMMIT:
            conn.commit()
        newdsid = cursor.fetchone()[0]
    except db.Error, e:
        logging.warn("Query failed: %s." % query)
        raise
    finally:
        cursor.close()
    return newdsid


def insert_image(conn, dataset,
                 freq_eff, freq_bw, 
                 taustart_ts, tau_time,
                 beam_maj, beam_min,
                 beam_pa,  
                 url):
    """Insert an image for a given dataset with the column values
    given in the argument list.
    """
    #tau_mode = 0 ###Placeholder, this variable is not well defined currently.

    newimgid = None
    try:
        cursor = conn.cursor()
        query = """\
        SELECT insertImage(%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (dataset
                              #,tau_mode
                              ,tau_time
                              ,freq_eff
                              ,freq_bw
                              ,taustart_ts
                              #,beam_maj
                              #,beam_min
                              #,beam_pa
                              ,url
                              ))
        newimgid = cursor.fetchone()[0]
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error, e:
        logging.warn("Query failed: %s." % query)
        raise
    finally:
        cursor.close()
    return newimgid

def _insert_extractedsources(conn, image_id, results):
    """Insert all extracted sources with their properties

    The content of results is in the following sequence:
    (ra, dec, ra_err, dec_err, peak_flux, peak_flux_err, 
    int_flux, int_flux_err, significance level,
    beam major width (as), beam minor width(as), beam parallactic angle).
    
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
    xtrsrc = []
    for src in results:
        r = list(src)
        r[2] = r[2] * 3600. # ra_err converted to arcsec
        r[3] = r[3] * 3600. # decl_err is converted to arcsec
        r.append(image_id) # id of the image
        r.append(int(math.floor(r[1]))) # zone
        r.append(math.cos(math.radians(r[1])) * math.cos(math.radians(r[0]))) # Cartesian x
        r.append(math.cos(math.radians(r[1])) * math.sin(math.radians(r[0]))) # Cartesian y
        r.append(math.sin(math.radians(r[1]))) # Cartesian z
        r.append(r[0] * math.cos(math.radians(r[1]))) # ra * cos(radias(decl))
        xtrsrc.append(r)
    values = [str(tuple(xsrc)) for xsrc in xtrsrc]

    cursor = conn.cursor()
    try:
        query = """\
        INSERT INTO extractedsource
          (ra
          ,decl
          ,ra_err
          ,decl_err
          ,f_peak
          ,f_peak_err
          ,f_int
          ,f_int_err
          ,det_sigma
          ,semimajor
          ,semiminor
          ,pa
          ,image
          ,zone
          ,x
          ,y
          ,z
          ,racosdecl
          )
        VALUES
        """\
        + ",".join(values)
        cursor.execute(query)
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()


def insert_extracted_sources(conn, image_id, results):
    """Insert all extracted sources

    Insert the sources that were detected by the Source Extraction
    procedures into the extractedsource table.
    """
    
    _insert_extractedsources(conn, image_id, results)

# The following set of functions are private to the module;
# these are called by associate_extracted_sources, and should
# only be used in that way
def _empty_temprunningcatalog(conn):
    """Initialize the temporary storage table

    Initialize the temporary table temprunningcatalog which contains
    the current observed sources.
    """

    try:
        cursor = conn.cursor()
        query = """DELETE FROM temprunningcatalog"""
        cursor.execute(query)
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()


def _insert_temprunningcatalog(conn, image_id, deRuiter_r, radius=0.03):
    """Select matched sources

    Here we select the extractedsource that have a positional match
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
  ,wm_ra_err
  ,wm_decl_err
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
        ,t0.wm_ra_err
        ,t0.wm_decl_err
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
                ,3600 * SQRT(  (rc0.wm_ra * COS(RADIANS(rc0.wm_decl)) - x0.ra * COS(RADIANS(x0.decl)))
                             * (rc0.wm_ra * COS(RADIANS(rc0.wm_decl)) - x0.ra * COS(RADIANS(x0.decl))) 
                               / (rc0.wm_ra_err * rc0.wm_ra_err + x0.ra_err * x0.ra_err)
                            + (rc0.wm_decl - x0.decl) * (rc0.wm_decl - x0.decl)
                              / (rc0.wm_decl_err * rc0.wm_decl_err + x0.decl_err * x0.decl_err)
                            ) AS r
                ,x0.f_peak
                ,x0.f_peak_err
                ,x0.f_int
                ,x0.f_int_err
                ,image.dataset
                ,image.band
                ,image.stokes
                ,rc0.datapoints + 1 AS datapoints
                ,((datapoints * rc0.avg_wra + x0.ra /
                  (x0.ra_err * x0.ra_err)) / (datapoints + 1))
                 /
                 ((datapoints * rc0.avg_weight_ra + 1 /
                   (x0.ra_err * x0.ra_err)) / (datapoints + 1))
                 AS wm_ra
                ,((datapoints * rc0.avg_wdecl + x0.decl /
                  (x0.decl_err * x0.decl_err)) / (datapoints + 1))
                 /
                 ((datapoints * rc0.avg_weight_decl + 1 /
                   (x0.decl_err * x0.decl_err)) / (datapoints + 1))
                 AS wm_decl
                ,SQRT(1 / ((datapoints + 1) *
                  ((datapoints * rc0.avg_weight_ra +
                    1 / (x0.ra_err * x0.ra_err)) / (datapoints + 1))
                          )
                     ) AS wm_ra_err
                ,SQRT(1 / ((datapoints + 1) *
                  ((datapoints * rc0.avg_weight_decl +
                    1 / (x0.decl_err * x0.decl_err)) / (datapoints + 1))
                          )
                     ) AS wm_decl_err
                ,(datapoints * rc0.avg_wra + x0.ra / (x0.ra_err * x0.ra_err))
                 / (datapoints + 1) AS avg_wra
                ,(datapoints * rc0.avg_wdecl + x0.decl /
                  (x0.decl_err * x0.decl_err))
                 / (datapoints + 1) AS avg_wdecl
                ,(datapoints * rc0.avg_weight_ra + 1 /
                  (x0.ra_err * x0.ra_err))
                 / (datapoints + 1) AS avg_weight_ra
                ,(datapoints * rc0.avg_weight_decl + 1 /
                  (x0.decl_err * x0.decl_err))
                 / (datapoints + 1) AS avg_weight_decl
            FROM extractedsource x0
                ,runningcatalog rc0
                ,image
           WHERE image.id = %s
             AND x0.image = image.id
             AND image.dataset = rc0.dataset
             AND rc0.zone BETWEEN CAST(FLOOR(x0.decl - %s) as INTEGER)
                                 AND CAST(FLOOR(x0.decl + %s) as INTEGER)
             AND rc0.wm_decl BETWEEN x0.decl - %s
                                    AND x0.decl + %s
             AND rc0.wm_ra BETWEEN x0.ra - alpha(%s, x0.decl)
                                  AND x0.ra + alpha(%s, x0.decl)
             AND SQRT(  (x0.ra * COS(RADIANS(x0.decl)) - rc0.wm_ra * COS(RADIANS(rc0.wm_decl)))
                      * (x0.ra * COS(RADIANS(x0.decl)) - rc0.wm_ra * COS(RADIANS(rc0.wm_decl)))
                      / (x0.ra_err * x0.ra_err + rc0.wm_ra_err * rc0.wm_ra_err)
                     + (x0.decl - rc0.wm_decl) * (x0.decl - rc0.wm_decl)
                      / (x0.decl_err * x0.decl_err + rc0.wm_decl_err * rc0.wm_decl_err)
                     ) < %s
         ) t0
         LEFT OUTER JOIN runningcatalog_flux rf0
         ON t0.runcat = rf0.runcat
         AND t0.band = rf0.band
         AND t0.stokes = rf0.stokes
"""
        #print "Q:\n",query % (image_id, 
        #                        radius, radius, radius, radius, 
        #                        radius, radius, deRuiter_r/3600.)
        cursor.execute(query, (image_id, 
                                radius, radius, radius, radius, 
                                radius, radius, deRuiter_r/3600.))
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error, e:
        q = query % (image_id, 
                        radius, radius, radius, radius, 
                        radius, radius, deRuiter_r/3600.)
        logging.warn("Failed on query\n%s." % q)
        raise
    finally:
        cursor.close()

def _flag_multiple_counterparts_in_runningcatalog(conn):
    """Flag the many-to-many and many-to-one association pairs. 

    -1- many running-catalogue sources  <-> many extracted sources
        many running-catalogue sources  <-> one extracted source

    We take care of the many-to-many associations and the 
    many-to-one associations in the same way.

    NOTE: We do not yet handle the case where two or more extractedsource have
    two or more counterparts in the runningcatalog, and all can be cross-
    associated, the so-called many-to-many associations. However,
    those pairs will be split up in a set of many-to-one associations
    and handled as such.
    
    What we do is filtering on single extracted sources that have 
    multiple counterparts in the running catalogue, 
    i.e. the many-to-one associations.
    We only keep the association pair that has the lowest De Ruiter radius, 
    namely the highest association probability, 
    whereas the other pairs will be omitted.

    NOTES & TODO:
    1. The calculation of min_r1 and r1 is an approximation.
    2. It is worth considering whether this might be changed to selecting
    the brightest neighbour source, instead of just the closest neighbour. 
    (There are case [when flux_lim > 10Jy] that the nearest source has a 
    lower flux level, causing unexpected spectral indices.)
    3. TODO: We should not throw away those outlier pairs, but flag
    them as such in temprunningcatag.
    """

    try:
        cursor = conn.cursor()
        query = """\
        SELECT t1.runcat
              ,t1.xtrsrc
          FROM (SELECT trc0.xtrsrc
                      ,MIN(trc0.r) AS min_r1
                  FROM temprunningcatalog trc0
                      ,runningcatalog rc0
                      ,extractedsource x0
                 WHERE trc0.xtrsrc IN (SELECT xtrsrc
                                         FROM temprunningcatalog
                                       GROUP BY xtrsrc
                                       HAVING COUNT(*) > 1
                                      )
                   AND trc0.runcat = rc0.id
                   AND trc0.xtrsrc = x0.id
                GROUP BY trc0.xtrsrc
               ) t0
              ,(SELECT trc1.runcat
                      ,trc1.xtrsrc
                      ,trc1.r AS r1
                  FROM temprunningcatalog trc1
                      ,runningcatalog rc1
                      ,extractedsource x1
                 WHERE trc1.xtrsrc IN (SELECT xtrsrc
                                         FROM temprunningcatalog
                                       GROUP BY xtrsrc
                                       HAVING COUNT(*) > 1
                                      )
                   AND trc1.runcat = rc1.id
                   AND trc1.xtrsrc = x1.id
               ) t1
         WHERE t1.xtrsrc = t0.xtrsrc
           AND t1.r1 > t0.min_r1
        """
        cursor.execute(query)
        results = zip(*cursor.fetchall())
        if len(results) != 0:
            runcat = results[0]
            xtrsrc = results[1]
            # TODO: See NOTE 3 above: Consider setting row to inactive instead of deleting
            # Here, for the many-to-many and many-to-one associations, we throw away
            # the pairs of which the De Ruiter radius is larger that the smallest one
            # of the set.
            # This will effectively reduce the tempruncat table with associations of the 
            # one-to-one and one-to-many types.
            query = """\
            UPDATE temprunningcatalog
               SET inactive = TRUE
             WHERE runcat = %s
               AND xtrsrc = %s
            """
            for j in range(len(runcat)):
                #print "\nThrowing away many-to-many from tempruncat:", runcat[j], xtrsrc[j]
                cursor.execute(query, (runcat[j], xtrsrc[j]))
                if not AUTOCOMMIT:
                    conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()

def _insert_1_to_many_runcat(conn):
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

    try:
        cursor = conn.cursor()
        query = """\
        INSERT INTO runningcatalog
          (xtrsrc
          ,dataset
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
          SELECT xtrsrc
                ,dataset
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
            FROM temprunningcatalog
           WHERE runcat IN (SELECT runcat
                              FROM temprunningcatalog
                             WHERE inactive = FALSE
                            GROUP BY runcat
                            HAVING COUNT(*) > 1
                           )
        """
        cursor.execute(query)
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()

def _insert_1_to_many_runcat_flux(conn):
    """Insert the fluxes of the extracted sources that belong 
    to a one-to-many association in the runningcatalog.
    
    Analogous to the runningcatalog, extracted source properties
    are added to the runningcatalog_flux table.
    """

    try:
        cursor = conn.cursor()
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
          SELECT rc0.id
                ,trc0.band
                ,trc0.stokes
                ,trc0.f_datapoints 
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
            FROM temprunningcatalog trc0
                ,runningcatalog rc0
           WHERE trc0.xtrsrc = rc0.xtrsrc
             AND trc0.runcat IN (SELECT runcat
                                   FROM temprunningcatalog
                                  WHERE inactive = FALSE
                                 GROUP BY runcat
                                 HAVING COUNT(*) > 1
                                )
        """
        cursor.execute(query)
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()

def _insert_1_to_many_basepoint_assoc(conn):
    """Insert base points for one-to-many associations

    And, we have to insert the base point of the associations.
    """

    try:
        cursor = conn.cursor()
        query = """\
        INSERT INTO assocxtrsource
          (runcat
          ,xtrsrc
          ,distance_arcsec
          ,r
          ,type
          )
          SELECT r.id
                ,t.xtrsrc
                ,t.distance_arcsec
                ,t.r
                ,2
            FROM temprunningcatalog t
                ,runningcatalog r
           WHERE t.xtrsrc = r.xtrsrc
             AND t.runcat IN (SELECT runcat
                                FROM temprunningcatalog
                               WHERE inactive = FALSE
                              GROUP BY runcat
                              HAVING COUNT(*) > 1
                             )
        """
        cursor.execute(query)
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error, e:
        logging.warn("Failed on query:\n%s" % query)
        raise
    finally:
        cursor.close()

def _insert_1_to_many_assoc(conn):
    """Update the runcat id for the one-to-many associations,
    and delete the runningcatalog_flux entries of the old runcat id
    (the new ones have been added earlier).

    In this case, new entries in the runningcatalog and runningcatalog_flux
    were already added (for every extractedsource one), which will replace 
    the existing ones in the runningcatalog. 
    Therefore, we have to update the references to these new ids as well.
    So, we will append to assocxtrsource and delete the entries from
    runningcatalog_flux.

    NOTE:
    1. We do not update the distance_arcsec and r values of the pairs. 
    """
    
    try:
        cursor = conn.cursor()
        query = """\
        INSERT INTO assocxtrsource
          (runcat
          ,xtrsrc
          ,distance_arcsec
          ,r
          ,type
          )
          SELECT r.id
                ,a.xtrsrc
                ,a.distance_arcsec
                ,a.r
                ,6
            FROM assocxtrsource a
                ,runningcatalog r
                ,temprunningcatalog t
           WHERE t.xtrsrc = r.xtrsrc
             AND t.runcat = a.runcat
             AND t.runcat IN (SELECT runcat
                                FROM temprunningcatalog
                               WHERE inactive = FALSE
                              GROUP BY runcat
                              HAVING COUNT(*) > 1
                             )
        """
        cursor.execute(query)
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error, e:
        logging.warn("Failed on query:\n%s." % query)
        raise
    finally:
        cursor.close()

def _delete_1_to_many_inactive_assoc(conn):
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

    try:
        cursor = conn.cursor()
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
        cursor.execute(query)
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()

def _delete_1_to_many_inactive_runcat_flux(conn):
    """Flag the old runcat ids in the runningcatalog to inactive
    
    Since we replaced this runcat.id with multiple new one, we first
    flag it as inactive, after which we delete it from the runningcatalog
    
    """

    try:
        cursor = conn.cursor()
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
        cursor.execute(query)
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()

def _flag_1_to_many_inactive_runcat(conn):
    """Flag the old runcat ids in the runningcatalog to inactive
    
    We do noy delete them yet, because we need them later on.
    Since we replaced this runcat.id with multiple new one, we first
    flag it as inactive, after which we delete it from the runningcatalog
    """

    try:
        cursor = conn.cursor()
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
        cursor.execute(query)
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error, e:
        logging.warn("Failed on query:\n%s." % query)
        raise
    finally:
        cursor.close()

def _flag_1_to_many_inactive_tempruncat(conn):
    """Delete the one-to-many associations from temprunningcatalog,
    and delete the inactive rows from runningcatalog.
    
    We do noy delete them yet, because we need them later on.
    After the one-to-many associations have been processed,
    they can be deleted from the temporary table and
    the runningcatalog.
    
    """

    try:
        cursor = conn.cursor()
        # TODO: When we delete the many from the 1-to-many assocs here,
        #       it will later on pop up again in the list of extracted
        #       sources that did not have a match in temprunningcatalog
        #
        # See also comments at _insert_new_runcat()
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
        cursor.execute(query)
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error, e:
        logging.warn("Failed on query:\n%s" % query)
        raise
    finally:
        cursor.close()

def _insert_1_to_1_assoc(conn):
    """Insert remaining one-to-one associations into assocxtrsource table
    
    This handles the case where a single extractedsource is associated
    with a single runningcatalog source.
    The extractedsource.id is appended to the assocxtrsource table
    (i.e. its light-curve datapoints).

    Since tempruncat contains the new (updated)  position average 
    (including the latest extractedsource), 
    the calculations of the distance and r should be done 
    with the runningcatalog values
    """
    
    try:
        cursor = conn.cursor()
        query = """\
        INSERT INTO assocxtrsource
          (runcat
          ,xtrsrc
          ,distance_arcsec
          ,r
          ,type
          )
          SELECT t.runcat
                ,t.xtrsrc
                ,t.distance_arcsec
                ,t.r
                ,3
            FROM temprunningcatalog t
                ,runningcatalog r
                ,extractedsource x
           WHERE t.runcat = r.id
             AND r.inactive = FALSE
             AND t.xtrsrc = x.id
        """
        cursor.execute(query)
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error, e:
        logging.warn("Failed on query:\n%s." % query)
        raise
    finally:
        cursor.close()


def _update_1_to_1_runcat(conn):
    """Update the running catalog with the values in temprunningcatalog"""
    
    # TODO : Check for clause inactive
    try:
        cursor = conn.cursor()
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
              ,wm_ra_err = (SELECT wm_ra_err
                              FROM temprunningcatalog
                             WHERE temprunningcatalog.runcat = runningcatalog.id
                          AND temprunningcatalog.inactive = FALSE
                           )
              ,wm_decl_err = (SELECT wm_decl_err
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
         WHERE EXISTS (SELECT runcat
                         FROM temprunningcatalog
                        WHERE temprunningcatalog.runcat = runningcatalog.id
                          AND temprunningcatalog.inactive = FALSE
                      )
        """
        cursor.execute(query)
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error, e:
        logging.warn("Failed on query:\n%s" % query)
        raise
    finally:
        cursor.close()

def _update_1_to_1_runcat_flux(conn):
    """Update the runningcatalog_flux
    
    Based on the runcat ids in tempruncat, the fluxes of the corresponding
    entries in runcat_flux should be updated.
    
    """

    # TODO: Change this to a single bulk update query
    try:
        cursor = conn.cursor()
        query = """\
        SELECT f_datapoints
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
              ,runcat
              ,band
              ,stokes
          FROM temprunningcatalog
         WHERE inactive = FALSE
        """
        cursor.execute(query)
        results = cursor.fetchall()
        query = """\
        UPDATE runningcatalog_flux
           SET f_datapoints = %s
              ,avg_f_peak = %s
              ,avg_f_peak_sq = %s
              ,avg_f_peak_weight = %s
              ,avg_weighted_f_peak = %s
              ,avg_weighted_f_peak_sq = %s
              ,avg_f_int = %s
              ,avg_f_int_sq = %s
              ,avg_f_int_weight = %s
              ,avg_weighted_f_int = %s
              ,avg_weighted_f_int_sq = %s
         WHERE runcat = %s
           AND band = %s
           AND stokes = %s
        """
        for result in results:
            cursor.execute(query, tuple(result))
            if not AUTOCOMMIT:
                conn.commit()
    except db.Error, e:
        logging.warn("Failed on query:\n%s." % query)
        raise
    finally:
        cursor.close()

#def _insert_new_runcat(conn, image_id, deRuiter_r, radius=0.03):
def _insert_new_runcat(conn, image_id):
    """Insert new sources into the running catalog
    
    Extractedsources for which no counterpart was found in the 
    runningcatalog (i.e. no pair exists in tempruncat),
    will be added as a new source to the assocxtrsource,
    runningcatalog and runningcatalog_flux tables.
    This function inserts the new source in the runningcatalog table,
    where xtrsrc is the id of the new extractedsource.
    This is the first of the series, since the other insertions have
    references to the runningcatalog table.
    """
    try:
        cursor = conn.cursor()
        # Unfortunately, this does not work,
        # since we previous deleted the extractedsources from the 
        # tempruncat table that had the same runcat counterpart 
        # (1-to-many assocs).
        # To get it working we need to not to delete the tempruncat entries,
        # but set them to inactive and empty the table (and the inactive 
        # runningcatalog sources) at the end of image processing
        #
        # NOTE: Here we include all (inactive TRUE&FALSE) tempruncat
        # source to have the original assocs available
        query = """\
        INSERT INTO runningcatalog
          (xtrsrc
          ,dataset
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
          SELECT t0.xtrsrc
                ,t0.dataset
                ,t0.datapoints
                ,t0.zone
                ,t0.wm_ra
                ,t0.wm_decl
                ,t0.wm_ra_err
                ,t0.wm_decl_err
                ,t0.avg_wra
                ,t0.avg_wdecl
                ,t0.avg_weight_ra
                ,t0.avg_weight_decl
                ,t0.x
                ,t0.y
                ,t0.z
            FROM (SELECT x0.id AS xtrsrc
                        ,i0.dataset
                        ,1 AS datapoints
                        ,x0.zone
                        ,x0.ra AS wm_ra
                        ,x0.decl AS wm_decl
                        ,x0.ra_err AS wm_ra_err
                        ,x0.decl_err AS wm_decl_err
                        ,x0.ra / (x0.ra_err * x0.ra_err) AS avg_wra
                        ,x0.decl / (x0.decl_err * x0.decl_err) AS avg_wdecl
                        ,1 / (x0.ra_err * x0.ra_err) AS avg_weight_ra
                        ,1 / (x0.decl_err * x0.decl_err) AS avg_weight_decl
                        ,x0.x
                        ,x0.y
                        ,x0.z
                    FROM extractedsource x0
                        ,image i0
                   WHERE x0.image = i0.id
                     AND x0.image = %s
                 ) t0
                 LEFT OUTER JOIN temprunningcatalog trc0
                 ON t0.xtrsrc = trc0.xtrsrc
           WHERE trc0.xtrsrc IS NULL
        """
        cursor.execute(query, (image_id,))
        #cursor.execute(query, (image_id, image_id,
        #                        radius, radius, radius, radius, radius, radius,
        #                        deRuiter_r/3600.))
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error, e:
        q = query % (image_id,)
        logging.warn("Failed on query:\n%s." % q)
        raise
    finally:
        cursor.close()

#def _insert_new_runcat_flux(conn, image_id, deRuiter_r, radius=0.03):
def _insert_new_runcat_flux(conn, image_id):
    """Insert new sources into the runningicatalog_flux
    
    Extractedsources for which not a counterpart was found in the
    runningcatalog, will be added as a new source to the assocxtrsource,
    runningcatalog and runningcatalog_flux tables.
    This function inserts the new source in the runningcatalog table,
    where xtrsrc is the id of the new extractedsource.

    """
    try:
        cursor = conn.cursor()
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
            FROM runningcatalog r0
                ,image i0
                ,extractedsource x0
           WHERE x0.image = i0.id
             AND x0.id = r0.xtrsrc
             AND r0.xtrsrc IN (SELECT t0.xtrsrc
                                 FROM (SELECT x1.id AS xtrsrc
                                         FROM extractedsource x1
                                             ,image i1
                                        WHERE x1.image = i1.id
                                          AND i1.id = %s
                                      ) t0
                                      LEFT OUTER JOIN temprunningcatalog trc1
                                      ON t0.xtrsrc = trc1.xtrsrc
                                 WHERE trc1.xtrsrc IS NULL
                              )
        """
        #q = query % (image_id,))
        #print "Q:\n%s" % q
        #sys.exit()
        cursor.execute(query, (image_id, ))
        #image_id,
        #                        radius, radius, radius, radius, radius, radius,
        #                        deRuiter_r/3600.))
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error, e:
        q = query % (image_id,)
        logging.warn("Failed on query:\n%s" % q)
        raise
    finally:
        cursor.close()

#def _insert_new_assoc(conn, image_id, deRuiter_r, radius=0.03):
def _insert_new_assoc(conn, image_id):
    """Insert new associations for unknown sources

    Extractedsources for which not a counterpart was found in the
    runningcatalog, will be added as a new source to the assocxtrsource,
    runningcatalog and runningcatalog_flux tables.
    This function inserts the new source in the assocxtrsource table,
    where the runcat and xtrsrc ids are identical to each other 
    in order to have this data point included in the light curve.
    
    The left outer join in combination with the trc0.xtrsrc is null,
    selects the extracted sources that were not present in 
    temprunningcatalog, i.e. did not have a counterpart in the runningcatalog.
    These were just inserted as new sources in the runningcatalog 
    of which we want to use the ids to have them
    in the assocxtrsource as well.
    """

    try:
        cursor = conn.cursor()
        query = """\
        INSERT INTO assocxtrsource
          (runcat
          ,xtrsrc
          ,distance_arcsec
          ,r
          ,type
          )
          SELECT r0.id AS runcat
                ,x0.id AS xtrsrc
                ,0
                ,0
                ,4
            FROM runningcatalog r0
                ,extractedsource x0
           WHERE r0.xtrsrc = x0.id
             AND r0.xtrsrc IN (SELECT t0.xtrsrc
                                 FROM (SELECT x1.id AS xtrsrc
                                         FROM extractedsource x1
                                             ,image i1
                                        WHERE x1.image = i1.id
                                          AND i1.id = %s
                                      ) t0
                                      LEFT OUTER JOIN temprunningcatalog trc1
                                      ON t0.xtrsrc = trc1.xtrsrc
                                 WHERE trc1.xtrsrc IS NULL
                              )
        """
        cursor.execute(query, (image_id,))
        #cursor.execute(query, (image_id, image_id,
        #                        radius, radius, radius, radius, radius, radius,
        #                        deRuiter_r/3600.))
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error, e:
        q = query % (image_id,)
        logging.warn("Failed on query:\n%s" % q)
        raise
    finally:
        cursor.close()

def _delete_inactive_runcat(conn):
    """Delete the one-to-many associations from temprunningcatalog,
    and delete the inactive rows from runningcatalog.
    
    After the one-to-many associations have been processed,
    they can be deleted from the temporary table and
    the runningcatalog.
    
    """

    try:
        cursor = conn.cursor()
        query = """\
        DELETE
          FROM runningcatalog
         WHERE inactive = TRUE
        """
        cursor.execute(query)
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error, e:
        logging.warn("Failed on query:\n%s" % query)
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
    print "De Ruiter Radius: r = ", deRuiter_r

    _empty_temprunningcatalog(conn)
    #+------------------------------------------------------+
    #| Here we select all extracted sources that have one or|
    #| more counterparts in the runningcatalog              |
    #| Association pairs are of the sequence runcat-xtrsrc, |
    #| which may be matching one of the following cases:    |
    #| many-to-many, many-to-one, one-to-many, one-to-many  |
    #+------------------------------------------------------+
    _insert_temprunningcatalog(conn, image_id, deRuiter_r)
    #+------------------------------------------------------+
    #| Here we process the many-to-many AND many-to-one     |
    #| associations.                                        |
    #+------------------------------------------------------+
    # _process_many_to_many() & _process_many_to_1()
    _flag_multiple_counterparts_in_runningcatalog(conn)
    #+------------------------------------------------------+
    #| Here we process the one-to-many associations.        |
    #+------------------------------------------------------+
    _insert_1_to_many_runcat(conn)
    _insert_1_to_many_runcat_flux(conn)
    _insert_1_to_many_basepoint_assoc(conn)
    _insert_1_to_many_assoc(conn)
    #TODO: It is probably best to update the transient and
    # monitoringlist tables here at the same time
    _delete_1_to_many_inactive_assoc(conn)
    _delete_1_to_many_inactive_runcat_flux(conn)
    _flag_1_to_many_inactive_runcat(conn)
    _flag_1_to_many_inactive_tempruncat(conn)
    #+-----------------------------------------------------+
    #| After all this, we are now left with the 1-1 assocs |
    #+-----------------------------------------------------+
    # _process_1_to_1()
    _insert_1_to_1_assoc(conn)
    _update_1_to_1_runcat(conn)
    _update_1_to_1_runcat_flux(conn)
    #+-------------------------------------------------------+
    #| Here we take care of the extracted sources that could |
    #| not be associated with any runningcatalog source      |
    #+-------------------------------------------------------+
    _insert_new_runcat(conn, image_id)
    _insert_new_runcat_flux(conn, image_id)
    _insert_new_assoc(conn, image_id)
    _empty_temprunningcatalog(conn)
    _delete_inactive_runcat(conn)

def select_single_epoch_detection(conn, dsid):
    """Select sources from running catalog which have only one detection"""

    results = []
    cursor = conn.cursor()
    try:
        query = """\
SELECT runcat
      ,dataset
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
 WHERE dataset = %s
   AND datapoints = 1
"""
        cursor.execute(query, (dsid, ))
        results = cursor.fetchall()
        results = [dict(srcid=x[0], npoints=x[2], v_nu=x[7], eta_nu=x[8])
                   for x in results]
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error:
        logging.warn("Failed on query %s", query)
        raise
    finally:
        cursor.close()
    return results


def lightcurve(conn, xtrsrcid):
    """Obtain a light curve for a specific extractedsource

    Args:

        xtrsrcid (int): the source identifier that corresponds to a
        point on the light curve. Note that the point does not have to
        be the start (first) point of the light curve.

    Returns:

        A list of 5-tuples, each tuple containing (in order):

            - observation start time as a datetime.datetime object
            
            - integration time (float)
            
            - peak flux (float)
            
            - peak flux error (float)
            
            - database ID of this particular source
    """
    #TODO: This lightcurve returns fluxes for every band and stokes if available.

    cursor = conn.cursor()
    try:
        query = """\
        SELECT im.taustart_ts
              ,im.tau_time
              ,ex.f_peak
              ,ex.f_peak_err
              ,ex.id
          FROM extractedsource ex
              ,assocxtrsource ax
              ,image im
         WHERE ax.runcat IN (SELECT runcat 
                               FROM assocxtrsource 
                              WHERE xtrsrc = %s
                            )
           AND ax.xtrsrc = ex.id
           AND ex.image = im.id
        ORDER BY im.taustart_ts
        """
        cursor.execute(query, (xtrsrcid,))
        results = cursor.fetchall()
    except db.Error:
        query = query % xtrsrcid
        logging.warn("Failed to obtain light curve")
        logging.warn("Query failed:\n%s", query)
        raise
    finally:
        cursor.close()
    return results


# This function is private to the module, and is only called by
# 
def _select_variability_indices(conn, dsid, V_lim, eta_lim):
    """Select sources and variability indices in the running catalog

    This comes relatively easily, since we have kept track of the
    average fluxes and the variance measures, and thus can quickly
    obtain any sources that exceed a constant flux by a certain amount.

    Args:

        dsid (int): dataset of interest

        V_lim ():

        eta_lim ():
    """

    # To do: explain V_lim and eta_lim
    
    results = []
    cursor = conn.cursor()
    try:
        query = """\
SELECT runcat
      ,dataset
      ,f_datapoints
      ,wm_ra
      ,wm_decl
      ,wm_ra_err
      ,wm_decl_err
      ,t1.V_inter / t1.avg_f_peak AS V
      ,t1.eta_inter / t1.avg_f_peak_weight AS eta
  FROM (SELECT runcat
              ,dataset
              ,f_datapoints
              ,wm_ra
              ,wm_decl
              ,wm_ra_err
              ,wm_decl_err
              ,avg_f_peak
              ,avg_f_peak_weight
              ,CASE WHEN rf0.f_datapoints = 1
                    THEN 0
                    ELSE SQRT(CAST(rf0.f_datapoints AS DOUBLE) * (avg_f_peak_sq - avg_f_peak * avg_f_peak) 
                             / (CAST(rf0.f_datapoints AS DOUBLE) - 1.0)
                             )
               END AS V_inter
              ,CASE WHEN rf0.f_datapoints = 1
                    THEN 0
                    ELSE (CAST(rf0.f_datapoints AS DOUBLE) / (CAST(rf0.f_datapoints AS DOUBLE) - 1.0)) 
                         * (avg_f_peak_weight * avg_weighted_f_peak_sq - avg_weighted_f_peak * avg_weighted_f_peak)
               END AS eta_inter
          FROM runningcatalog rc0
              ,runningcatalog_flux rf0
         WHERE rc0.dataset = %s
           AND rc0.id = rf0.runcat
       ) t1
 WHERE t1.V_inter / t1.avg_f_peak > %s
   AND t1.eta_inter / t1.avg_f_peak_weight > %s
"""
        cursor.execute(query, (dsid, V_lim, eta_lim))
        results = cursor.fetchall()
        results = [dict(
            srcid=x[0], npoints=x[2], v_nu=x[7], eta_nu=x[8], dataset=x[1],
            ra=x[3], dec=x[4], ra_err=x[5], dec_err=x[6])
                   for x in results]
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error:
        query = query % (dsid, V_lim, eta_lim)
        logging.warn("Query failed:\n%s", query)
        raise
    finally:
        cursor.close()
    return results

        
def detect_variable_sources(conn, dsid, V_lim, eta_lim):
    """Detect variability in extracted sources compared to the previous
    detections"""

    return _select_variability_indices(conn, dsid, V_lim, eta_lim)


def _insert_cat_assocs(conn, image_id, radius, deRuiter_r):
    """Insert found xtrsrc--catsrc associations into assoccatsource table.

    The search for cataloged counterpart sources is done in the catalogedsource
    table, which should have been preloaded with a selection of 
    the catalogedsources, depending on the expected field of view.
    
    """
    
    try:
        cursor = conn.cursor()
        query = """\
        INSERT INTO assoccatsource
          (xtrsrc
          ,catsrc
          ,distance_arcsec
          ,type
          ,r
          ,loglr
          )
          SELECT x0.id AS xtrsrc
                ,c0.id AS catsrc
                ,3600 * DEGREES(2 * ASIN(SQRT((x0.x - c0.x) * (x0.x - c0.x)
                                          + (x0.y - c0.y) * (x0.y - c0.y)
                                          + (x0.z - c0.z) * (x0.z - c0.z)
                                          ) / 2) ) AS distance_arcsec
                ,3
                ,3600 * sqrt( ((x0.ra * cos(RADIANS(x0.decl)) - c0.ra * cos(RADIANS(c0.decl))) 
                             * (x0.ra * cos(RADIANS(x0.decl)) - c0.ra * cos(RADIANS(c0.decl)))) 
                             / (x0.ra_err * x0.ra_err + c0.ra_err*c0.ra_err)
                            +
                              ((x0.decl - c0.decl) * (x0.decl - c0.decl)) 
                             / (x0.decl_err * x0.decl_err + c0.decl_err*c0.decl_err)
                            ) as r
                ,LOG10(EXP((   (x0.ra * COS(RADIANS(x0.decl)) - c0.ra * COS(RADIANS(c0.decl)))
                             * (x0.ra * COS(RADIANS(x0.decl)) - c0.ra * COS(RADIANS(x0.decl)))
                             / (x0.ra_err * x0.ra_err + c0.ra_err * c0.ra_err)
                            +  (x0.decl - c0.decl) * (x0.decl - c0.decl) 
                             / (x0.decl_err * x0.decl_err + c0.decl_err * c0.decl_err)
                           ) / 2
                          )
                      /
                      (2 * PI() * SQRT(x0.ra_err * x0.ra_err + c0.ra_err * c0.ra_err)
                                * SQRT(x0.decl_err * x0.decl_err + c0.decl_err * c0.decl_err) * %s)
                      ) AS loglr
            FROM extractedsource x0
                ,catalogedsource c0
           WHERE x0.image = %s
             AND c0.zone BETWEEN CAST(FLOOR(x0.decl - %s) AS INTEGER)
                             AND CAST(FLOOR(x0.decl + %s) AS INTEGER)
             AND c0.decl BETWEEN x0.decl - %s 
                             AND x0.decl + %s
             AND c0.ra BETWEEN x0.ra - alpha(%s, x0.decl)
                           AND x0.ra + alpha(%s, x0.decl)
             AND SQRT(  (x0.ra * COS(RADIANS(x0.decl)) - c0.ra * COS(RADIANS(c0.decl)))
                      * (x0.ra * COS(RADIANS(x0.decl)) - c0.ra * COS(RADIANS(c0.decl)))
                      / (x0.ra_err * x0.ra_err + c0.ra_err * c0.ra_err)
                     + (x0.decl - c0.decl) * (x0.decl - c0.decl)
                      / (x0.decl_err * x0.decl_err + c0.decl_err * c0.decl_err)
                     ) < %s
        """
        cursor.execute(query, (BG_DENSITY, 
                               image_id, 
                               radius, radius, radius, radius, radius, radius, 
                               deRuiter_r/3600.))
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error, e:
        logging.warn("Query failed:\n%s" % query)
        raise
    finally:
        cursor.close()


def associate_with_catalogedsources(conn, image_id, radius=0.03, deRuiter_r=DERUITER_R):
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


def associate_catalogued_sources_in_area(conn, ra, dec, radius, deRuiter_r=DERUITER_R/3600.):
    pass


# To do: move these two functions to unit tests
# Are these being used anyway? They appear to be defined, but not used
def concurrency_test_fixedalpha(conn):
    """Unit test function to test concurrency
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
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error, e:
        logging.warn("Query failed: %s." % query)
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
    except db.Error, e:
        logging.warn("Query failed: %s." % query)
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
    
        >>> columns_from_table(conn, 'image',
            keywords=['taustart_ts', 'tau_time', 'freq_eff', 'freq_bw'], where={'imageid': 1})
            [{'freq_eff': 133984375.0, 'taustart_ts': datetime.datetime(2010, 10, 9, 9, 4, 2), 'tau_time': 14400.0, 'freq_bw': 1953125.0}]

        This builds the SQL query:
        "SELECT taustart_ts, tau_time, freq_eff, freq_bw FROM image WHERE imageid=1"

    This function is implemented mainly to abstract and hide the SQL
    functionality from the Python interface.

    Args:

        conn: database connection object

        table (string): database table name

    Kwargs:

        keywords (list): column names to select from the table. None indicates all ('*')

        where (dict): where clause for the query, specified as a set
            of 'key = value' comparisons. Comparisons are and-ed
            together. Obviously, only 'is equal' comparisons are
            possible.

    Returns:

        (list): list of dicts. Each dict contains the given keywords,
            or all if keywords=None. Each element of the list
            corresponds to a table row.
        
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
        logging.warn("Query failed: %s" % query)
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
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error, e:
        query = query % (values + where_args)
        logging.warn("Query failed: %s", query)
        raise
    finally:
        cursor.close()


def get_imagefiles_for_ids(conn, image_ids):
    """Return a list of image filenames for the give image ids

    The actual returned list contains 2-tuples of (id, url)
    """
    
    where_string = ", ".join(["%s"] * len(image_ids))
    where_tuple = tuple(image_ids)
    query = ("""SELECT id, url FROM image WHERE id in (%s)""" %
             where_string)
    cursor = conn.cursor()
    try:
        querytxt = query % where_tuple
        cursor.execute(query, where_tuple)
        results = cursor.fetchall()
        ## extra
        #if not AUTOCOMMIT:
        #    conn.commit()
    except db.Error, e:
        query = query % where_tuple
        logging.warn("Query failed: %s", query)
        raise
    finally:
        cursor.close()
    return results


def match_nearests_in_catalogs(conn, srcid, radius=1.0,
                              catalogid=None, assoc_r=DERUITER_R/3600.):
    """Match a source with position ra, decl with catalogedsources
    within radius

    The function does not return the best match, but a list of sources
    that are contained within radius, ordered by distance.

    One can limit the list of matches using assoc_r for a
    goodness-of-match measure.
    
    Args:

        srcid: xtrsrc in runningcatalog

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
    
    #zoneheight = 1.0
    #catalog_filter = ""
    #if catalogid is None:
    #    catalog_filter = ""
    #else:
    #    try:
    #        iter(catalogid)
    #        # Note: cast to int, to ensure proper type
    #        catalog_filter = (
    #            "c.catid in (%s) AND " % ", ".join(
    #            [str(int(catid)) for catid in catalogid]))
    #    except TypeError:
    #        catalog_filter = "c.catid = %d AND " % catalogid
    #
    #subquery = """\
    #SELECT cs.catsrcid
    #      ,c.catid
    #      ,c.catname
    #      ,cs.catsrcname
    #      ,cs.ra
    #      ,cs.decl
    #      ,cs.ra_err
    #      ,cs.decl_err
    #      ,3600 * DEGREES(2 * ASIN(SQRT( (rc.x - cs.x) * (rc.x - cs.x)
    #                                   + (rc.y - cs.y) * (rc.y - cs.y)
    #                                   + (rc.z - cs.z) * (rc.z - cs.z)
    #                                   ) / 2)
    #                     ) AS assoc_distance_arcsec
    #      ,3600 * SQRT(  (rc.wm_ra - cs.ra) * COS(RADIANS(rc.wm_decl)) 
    #                   * (rc.wm_ra - cs.ra) * COS(RADIANS(rc.wm_decl))
    #                     / (rc.wm_ra_err * rc.wm_ra_err + cs.ra_err * cs.ra_err)
    #                  + (rc.wm_decl - cs.decl) * (rc.wm_decl - cs.decl)
    #                    / (rc.wm_decl_err * rc.wm_decl_err + cs.decl_err * cs.decl_err)
    #                  ) AS assoc_r
    #  FROM (SELECT wm_ra - alpha(%%s, wm_decl) as ra_min
    #              ,wm_ra + alpha(%%s, wm_decl) as ra_max
    #              ,CAST(FLOOR((wm_decl - %%s) / %%s) AS INTEGER) as zone_min
    #              ,CAST(FLOOR((wm_decl + %%s) / %%s) AS INTEGER) as zone_max
    #              ,wm_decl - %%s as decl_min
    #              ,wm_decl + %%s as decl_max
    #              ,x
    #              ,y
    #              ,z
    #              ,wm_ra
    #              ,wm_decl
    #              ,wm_ra_err
    #              ,wm_decl_err
    #          FROM runningcatalog
    #         WHERE xtrsrc = %%s
    #       ) rc
    #      ,catalogedsources cs
    #      ,catalogs c
    # WHERE %(catalog_filter)s
    #      cs.cat_id = c.catid
    #  AND cs.zone BETWEEN rc.zone_min 
    #                  AND rc.zone_max
    #  AND cs.ra BETWEEN rc.ra_min 
    #                and rc.ra_max
    #  AND cs.decl BETWEEN rc.decl_min 
    #                  and rc.decl_max
    #  AND cs.x * rc.x + cs.y * rc.y + cs.z * rc.z > COS(RADIANS(%%s))
    #""" % {'catalog_filter': catalog_filter}
    ##  AND cs.ra BETWEEN rc.wm_ra - alpha(%%s, rc.wm_decl)
    ##                AND rc.wm_ra + alpha(%%s, rc.wm_decl)
    #query = """\
    #SELECT 
    #    t.catsrcid
    #   ,t.catsrcname
    #   ,t.catid
    #   ,t.catname
    #   ,t.ra
    #   ,t.decl
    #   ,t.ra_err
    #   ,t.decl_err
    #   ,t.assoc_distance_arcsec
    #   ,t.assoc_r
    #FROM (%(subquery)s) as t
    #WHERE t.assoc_r < %%s
    #ORDER BY t.catid ASC, t.assoc_r ASC
    #""" % {'subquery': subquery}
    
    results = []
    # TODO: I would suggest this:
    q_alt = """\
    SELECT c.id
          ,c.catsrcname
          ,c.catalog
          ,k.name
          ,c.ra
          ,c.decl
          ,c.ra_err
          ,c.decl_err
          ,3600 * DEGREES(2 * ASIN(SQRT( (r.x - c.x) * (r.x - c.x)
                                       + (r.y - c.y) * (r.y - c.y)
                                       + (r.z - c.z) * (r.z - c.z)
                                       ) / 2)
                         ) AS distance_arcsec
          ,3600 * SQRT(  (r.wm_ra - c.ra) * COS(RADIANS(r.wm_decl)) 
                       * (r.wm_ra - c.ra) * COS(RADIANS(r.wm_decl))
                         / (r.wm_ra_err * r.wm_ra_err + c.ra_err * c.ra_err)
                      + (r.wm_decl - c.decl) * (r.wm_decl - c.decl)
                        / (r.wm_decl_err * r.wm_decl_err + c.decl_err * c.decl_err)
                      ) AS assoc_r
      FROM runningcatalog r
          ,catalogedsource c
          ,catalog k
     WHERE r.id = %s
       AND c.zone BETWEEN CAST(FLOOR(r.wm_decl - %s) AS INTEGER)
                      AND CAST(FLOOR(r.wm_decl + %s) AS INTEGER)
       AND c.decl BETWEEN r.wm_decl - %s
                      AND r.wm_decl + %s
       AND c.ra BETWEEN r.wm_ra - alpha(%s, r.wm_decl)
                    AND r.wm_ra + alpha(%s, r.wm_decl)
       AND c.x * r.x + c.y * r.y + c.z * r.z > COS(RADIANS(%s))
       AND c.catalog = k.id
       AND SQRT(  (r.wm_ra - c.ra) * COS(RADIANS(r.wm_decl)) 
                       * (r.wm_ra - c.ra) * COS(RADIANS(r.wm_decl))
                         / (r.wm_ra_err * r.wm_ra_err + c.ra_err * c.ra_err)
                      + (r.wm_decl - c.decl) * (r.wm_decl - c.decl)
                        / (r.wm_decl_err * r.wm_decl_err + c.decl_err * c.decl_err)
                      ) < %s
    ORDER BY c.catalog
            ,assoc_r
    """

    try:
        cursor = conn.cursor()
        #cursor.execute(query,  (radius, radius, radius, zoneheight,
        #                        radius, zoneheight, radius, radius,
        #                        srcid, radius, assoc_r))
        cursor.execute(q_alt,  (srcid,
                                radius, radius, radius, radius,
                                radius, radius, 
                                radius,
                                assoc_r))
        results = cursor.fetchall()
        results = [
            {'catsrcid': result[0], 'catsrcname': result[1],
             'catid': result[2], 'catname': result[3],
             'ra': result[4], 'decl': result[5],
             'ra_err': result[6], 'decl_err': result[7],
             'dist_arcsec': result[8], 'assoc_r': result[9]}
            for result in results]
    except db.Error, e:
        #query = query % (radius, radius, radius, zoneheight,
        #                 radius, zoneheight,
        #                 radius, radius, srcid, radius, assoc_r)
        #logging.warn("Query failed: %s", query)
        query = q_alt % (srcid,
                         radius, radius, radius, radius,
                         radius, radius,
                         radius,
                         assoc_r)
        logging.warn("Query failed:\n%s", query)
        raise
    finally:
        cursor.close()
    return results


def monitoringlist_not_observed(conn, image_id):
    """Return a list of sources from the monitoringlist that have no
    association with the extracted sources for this image

    We do this by matching the monitoring list xtrsrcs with the
    extractedsource xtrsrcids through the assocxtrsource. Using a
    left outer join, we get nulls in the place where a source should
    have been, but isn't: these are the sources that are not in
    extractedosurces and thus weren't automatically picked up by the
    sourcefinder. We limit our query using the image_id (and dataset
    through image.dataset).

    Lastly, we get the best (weighted averaged) position for the
    sources to be monitored from the runningcatalog, which shows up in
    the final inner join.

    Args:

        conn: A database connection object.

        image_id (int): the image under consideration.

    Returns (list):

        A list of sources yet to be observed; each list item is a
        tuple with the ra, dec, xtrsrcid and monitorid of the source.
    """

    try:
        cursor = conn.cursor()
        #original query refactored:
        query = """\
        SELECT rc.wm_ra
              ,rc.wm_decl
              ,t2.runcat2
              ,t2.monitorid
          FROM (SELECT ml.id AS monitorid
                      ,ml.runcat AS runcat2
                      ,t1.runcat AS runcat
                      ,t1.xtrsrc AS xtrsrc
                      ,t1.image AS image_id
                      ,ml.dataset 
                  FROM monitoringlist ml
                       LEFT OUTER JOIN (SELECT ax.runcat as runcat
                                              ,ex.id as xtrsrcid
                                              ,ex.image 
                                              ,ax.xtrsrc as xtrsrc
                                          FROM extractedsource ex
                                              ,assocxtrsource ax
                                         WHERE ex.id = ax.xtrsrc
                                           AND ex.image = %s
                                       ) t1
                       ON ml.runcat = t1.runcat
                 WHERE t1.xtrsrc IS NULL
               ) t2
              ,image im
              ,runningcatalog rc
         WHERE im.dataset = t2.dataset
           AND im.id = %s
           AND rc.id = t2.runcat2
        """
        cursor.execute(query, (image_id, image_id))
        results = cursor.fetchall()
    except db.Error, e:
        query = query % (image_id, image_id)
        logging.warn("Query failed: %s", query)
        raise
    finally:
        cursor.close()
    return results

    
def is_monitored(conn, srcid):
    """Return whether a source is in the monitoring list"""

    cursor = conn.cursor()
    try:
        query = """\
        SELECT COUNT(*) 
          FROM monitoringlist 
         WHERE runcat = %s
        """
        cursor.execute(query, (srcid,))
        result = bool(cursor.fetchone()[0])
    except db.Error, e:
        query = query % srcid
        logging.warn("Query failed: %s", query)
        raise
    finally:
        cursor.close()
    return result


def insert_monitoring_sources(conn, results, image_id):
    """Insert the list of measured monitoring sources for this image into
    extractedsource and runningcatalog.

    For user-inserted sources (i.e., sources that were not discovered
    automatically), the source will be inserted into the
    runningcatalog as well; for "normal" monitoring sources (i.e.,
    ones that preset a transient), this does not happen, to not
    pollute the runningcatalog averages for this entry.

    The insertion into runningcatalog can be done by xtrsrc_id from
    monitoringlist. In case it is negative, it is appended to
    runningcatalog, and xtrsrc_id is updated in the monitoringlist.
    """

    cursor = conn.cursor()
    # step through all the indiviudal results (/sources)
    for runcat, monitorid, result in results:
        ra, dec, ra_err, dec_err, peak, peak_err, flux, flux_err, sigma, \
            semimajor, semiminor, pa = result
        x = math.cos(math.radians(dec)) * math.cos(math.radians(ra))
        y = math.cos(math.radians(dec)) * math.sin(math.radians(ra))
        z = math.sin(math.radians(dec))
        racosdecl = ra * math.cos(math.radians(dec))
        # Always insert them into extractedsource
        query = """\
        INSERT INTO extractedsource
          (image
          ,zone
          ,ra
          ,decl
          ,ra_err
          ,decl_err
          ,x
          ,y
          ,z
          ,racosdecl
          ,det_sigma
          ,f_peak
          ,f_peak_err
          ,f_int
          ,f_int_err
          ,semimajor
          ,semiminor
          ,pa
          ,extract_type
          )
        VALUES
          (%s
          ,%s
          ,%s
          ,%s
          ,%s
          ,%s
          ,%s
          ,%s
          ,%s
          ,%s
          ,%s
          ,%s
          ,%s
          ,%s
          ,%s
          ,%s
          ,%s
          ,%s
          ,1
          )
        """
        try:
            cursor.execute(
                query, (image_id, int(math.floor(dec)), ra, dec, ra_err, dec_err,
                        x, y, z, racosdecl, sigma, peak, peak_err, flux, flux_err,
                        semimajor, semiminor, pa))
            if not AUTOCOMMIT:
                conn.commit()
            xtrsrcid = cursor.lastrowid
        except db.Error, e:
            query = query % (
                image_id, int(math.floor(dec)), ra, dec, ra_err, dec_err,
                x, y, z, sigma, peak, peak_err, flux, flux_err,
                semimajor, semiminor, pa)
            logging.warn("Query failed: %s", query)
            cursor.close()
            raise
        if runcat < 0:
            # TODO: When is this the case?
            # Insert as new source into the running catalog
            # and update the monitoringlist.xtrsrc
            query = """\
            INSERT INTO runningcatalog
                (xtrsrc
                ,dataset
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
                SELECT x0.id
                      ,i0.dataset
                      ,1
                      ,x0.zone
                      ,x0.ra
                      ,x0.decl
                      ,x0.ra_err
                      ,x0.decl_err
                      ,x0.ra / (x0.ra_err * x0.ra_err)
                      ,x0.decl / (x0.decl_err * x0.decl_err)
                      ,1 / (x0.ra_err * x0.ra_err)
                      ,1 / (x0.decl_err * x0.decl_err)
                      ,x0.x
                      ,x0.y
                      ,x0.z
                  FROM extractedsource x0
                      ,image i0
                 WHERE x0.id = %s
                   AND i0.id = %s
            """
            # TODO: Add runcat_flux as well!
            try:
                cursor.execute(query, (xtrsrcid, image_id))
                if not AUTOCOMMIT:
                    conn.commit()
            except db.Error, e:
                query = query % (image_id, xtrsrcid)
                logging.warn("query failed: %s", query)
                cursor.close()
                raise
            # Add it to the association table as well, so we can
            # obtain the lightcurve
            query = """\
            INSERT INTO assocxtrsource
              (runcat
              ,xtrsrc
              ,type
              ,distance_arcsec
              ,r
              ,loglr
              )
              SELECT runcat
                    ,xtrsrc
                    ,0
                    ,0
                    ,0
                    ,0
                FROM runningcatalog
               WHERE xtrsrc = %s
            """
            try:
                cursor.execute(query, (xtrsrcid, ))
                if not AUTOCOMMIT:
                    conn.commit()
            except db.Error, e:
                query = query % (xtrsrcid, xtrsrcid)
                logging.warn("query failed: %s", query)
                cursor.close()
                raise
            # Now update the monitoringlist.xtrsrc (note: the
            # original, possibly negative, xtrsrc_id is still held
            # safely in memory)
            # TODO: This must be defect for while...
            query = """\
            UPDATE monitoringlist 
               SET xtrsrc_id = %s
                  ,image_id = %s 
             WHERE monitorid = %s
            """
            try:
                cursor.execute(query, (xtrsrcid, image_id, monitorid))
                if not AUTOCOMMIT:
                    conn.commit()
            except db.Error, e:
                query = query % (xtrsrcid, xtrsrc_id)
                logging.warn("query failed: %s", query)
                cursor.close()
                raise                    
        else:
            # We don't update the runningcatalog, because:
            # - the fluxes are below the detection limit, and
            #   add little to nothing to the average flux
            # - the positions will have large errors, and
            #   contribute very litte to the average position
            # We thus only need to update the association table,
            # and the image_id in the monitoringlist
            # the xtrsrc_id from the monitoringlist already
            # points to the original/first point
            query = """\
            INSERT INTO assocxtrsource 
              (runcat
              ,xtrsrc
              ,type
              ,distance_arcsec
              ,r
              ,loglr
              )
            VALUES 
              (%s
              ,%s
              ,0
              ,0
              ,0
              ,0)
            """
            try:
                cursor.execute(query, (runcat, xtrsrcid))
                if not AUTOCOMMIT:
                    conn.commit()
            except db.Error, e:
                query = query % (xtrsrc_id, xtrsrcid)
                logging.warn("query failed: %s", query)
                cursor.close()
                raise
    cursor.close()
    

def insert_transient(conn, transient, dataset, images=None):
    """Insert a transient source in the database.
    Transients are stored in the transients table, as well as in
    the monitoring list.

    A check is performed where the base id (asocxtrsources.runcat)
    for the light curve of the transient is queried, by assuming the
    current srcid falls within a light curve
    (assocxtrsource.xtrsrc = srcid). If this id already in the
    table, we replace that transient by this one.

    The reason we check the assocxtrsource, is that when there is a
    1-to-many source match, the main source id (as stored in the
    runningcatalog) may change; this results in transients already
    stored having a different id than the current transient, while
    they are in the fact the same transient. The runcat of the
    stored id, however, should still be in the light curve of the new
    runcat, as an xtrsrc. We thus update the transient,
    and replace the current transients.xtrsrc by the new srcid
    (=assocxtrsource.xtrsrc)

    We store the transient in the monitoring list to ensure its flux
    will be measured even when the transient drops below the detection
    threshold.
    """

    srcid = transient.srcid
    cursor = conn.cursor()
    try:  # Find the possible transient associated with the current source
        query = """\
        SELECT id 
          FROM transient
         WHERE runcat = %s
        """
        cursor.execute(query, (srcid,))
        transientid = cursor.fetchone()
        if transientid:  # update/replace existing source
            query = """\
            UPDATE transient
               SET runcat = %s
                  ,eta = %s
                  ,V = %s
             WHERE id = %s
            """
            cursor.execute(query, (srcid, transient.eta, transient.V, transientid[0]))
        else:  # insert new source
            # First, let'find the current xtrsrc_id that belongs to the
            # current image: this is the trigger source id
            if images is None:
                image_set = ""
            else:
                image_set = ", ".join([str(image) for image in images])
            query = """\
            SELECT ex.id 
              FROM extractedsource ex
                  ,assocxtrsource ax
             WHERE ex.image IN (%s) 
               AND ex.id = ax.xtrsrc 
               AND ax.runcat = %%s
            """ % image_set
            cursor.execute(query, (srcid,))
            trigger_srcid = cursor.fetchone()[0]
            query = """\
            INSERT INTO transient
              (runcat
              ,eta
              ,V
              ,trigger_xtrsrc
              )
            VALUES 
              (%s
              ,%s
              ,%s
              ,%s
              )
            """
            cursor.execute(query, (srcid, transient.eta, transient.V, trigger_srcid))
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error:
        logging.warn("Query %s failed", query)
        logging.debug("Query %s failed", query)
        cursor.close()
        raise
    try:
        #TODO: File a MonetDB bug report, since
        # no two fk can be inserted
        query = """\
        INSERT INTO monitoringlist
          (runcat
          ,ra
          ,decl
          ,dataset
          )
          SELECT r.id
                ,0
                ,0
                ,%s
            FROM runningcatalog r
           WHERE r.id = %s
        """
        cursor.execute(query, (dataset, srcid))
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error:
        query = query % (dataset,srcid)
        logging.warn("Failed on query:\n%s" % query)
        cursor.close()
        raise
    cursor.close()
