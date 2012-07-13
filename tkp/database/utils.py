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
    tau_mode = 0 ###Placeholder, this variable is not well defined currently.

    newimgid = None
    try:
        cursor = conn.cursor()
        query = """\
        SELECT insertImage(%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (dataset
                              #,tau_mode
                              #,tau_time
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


def _insert_temprunningcatalog(conn, image_id, deRuiter_r):
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
  /*,avg_f_peak
  ,avg_f_peak_sq
  ,avg_f_peak_weight
  ,avg_weighted_f_peak
  ,avg_weighted_f_peak_sq
  ,avg_f_int
  ,avg_f_int_sq
  ,avg_f_int_weight
  ,avg_weighted_f_int
  ,avg_weighted_f_int_sq*/
  )
  SELECT t0.runcat
        ,t0.xtrsrc
        ,t0.dataset
        ,t0.band
        ,t0.stokes
        ,t0.datapoints
        ,CAST(FLOOR(t0.wm_decl) AS INTEGER)
        ,t0.wm_ra
        ,t0.wm_decl
        ,t0.wm_ra_err
        ,t0.wm_decl_err
        ,t0.avg_wra
        ,t0.avg_wdecl
        ,t0.avg_weight_ra
        ,t0.avg_weight_decl
        ,COS(RADIANS(t0.wm_decl)) * COS(RADIANS(t0.wm_ra))
        ,COS(RADIANS(t0.wm_decl)) * SIN(RADIANS(t0.wm_ra))
        ,SIN(RADIANS(t0.wm_decl))
        ,CASE WHEN t0.f_datapoints IS NULL
              THEN 0 
              ELSE f_datapoints
         END AS f_datapoints
        /*,t0.avg_I_peak
        ,t0.avg_I_peak_sq
        ,t0.avg_weight_peak
        ,t0.avg_weighted_I_peak
        ,t0.avg_weighted_I_peak_sq*/
    FROM (SELECT rc0.id as runcat
                ,x0.id as xtrsrc
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
                ,f_datapoints
                /*,x0.f_peak
                ,x0.f_peak_err
                ,x0.f_int
                ,x0.f_int_err*/
            FROM runningcatalog rc0
                 LEFT OUTER JOIN runningcatalog_flux rf0
                 ON rc0.id = rf0.runcat
                ,extractedsource x0
                ,image
           WHERE image.id = %s
             AND x0.image = image.id
             AND image.dataset = rc0.dataset
             AND rf0.runcat = rc0.id
             AND rf0.band = image.band
             AND rf0.stokes = image.stokes
             AND rc0.zone BETWEEN CAST(FLOOR(x0.decl - 0.025) as INTEGER)
                                 AND CAST(FLOOR(x0.decl + 0.025) as INTEGER)
             AND rc0.wm_decl BETWEEN x0.decl - 0.025
                                    AND x0.decl + 0.025
             AND rc0.wm_ra BETWEEN x0.ra - alpha(0.025, x0.decl)
                                  AND x0.ra + alpha(0.025, x0.decl)
             AND SQRT(  (x0.ra * COS(RADIANS(x0.decl)) - rc0.wm_ra * COS(RADIANS(rc0.wm_decl)))
                      * (x0.ra * COS(RADIANS(x0.decl)) - rc0.wm_ra * COS(RADIANS(rc0.wm_decl)))
                      / (x0.ra_err * x0.ra_err + rc0.wm_ra_err * rc0.wm_ra_err)
                     + (x0.decl - rc0.wm_decl) * (x0.decl - rc0.wm_decl)
                      / (x0.decl_err * x0.decl_err + rc0.wm_decl_err * rc0.wm_decl_err)
                     ) < %s
         ) t0
"""
        cursor.execute(query, (image_id, deRuiter_r/3600.))
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()


def _flag_multiple_counterparts_in_runningcatalog(conn):
    """Flag source with multiple associations

    Before we continue, we first take care of the many-to-many associations:
    sources that have multiple associations in both directions.

    -1- running-catalogue sources  <- extracted source

    NOTE: We do not yet handle the case where two or more extractedsource have
    the same counterparts (i.e. two or more) in the runningcatalog,
    the so-called many-to-many association.
    
    What we do is filtering on single extracted sources that have 
    multiple counterparts in the running catalogue, 
    i.e. the many-to-one associations.

    For now, we only keep the extractedsource that has 
    the lowest De Ruiter radius, the other pairs will be thrown away.

    NOTES & TODO:
    1. The calculation of min_r1 and r1 is an approximation.
    2. It is worth considering whether this might be changed to selecting
    the brightest neighbour source, instead of just the closest
    neighbour.
    (There are case [when flux_lim > 10Jy] that the nearest source has
    a lower flux level, causing unexpected spectral indices)
    3. TODO: We should not throw away those outlier pairs, but flag
    them as such in temprunningcatag.
    """

    try:
        cursor = conn.cursor()
        query = """\
SELECT t1.runcat
      ,t1.xtrsrc
  FROM (SELECT trc0.xtrsrc
              ,MIN(SQRT(  (x0.ra - rc0.wm_ra) * COS(RADIANS(x0.decl))
                        * (x0.ra - rc0.wm_ra) * COS(RADIANS(x0.decl))
                          / (x0.ra_err * x0.ra_err + rc0.wm_ra_err * rc0.wm_ra_err)
                       +  (x0.decl - rc0.wm_decl) * (x0.decl - rc0.wm_decl)
                          / (x0.decl_err * x0.decl_err + rc0.wm_decl_err * rc0.wm_decl_err)
                       )
                  ) AS min_r1
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
              ,SQRT(  (x1.ra - rc1.wm_ra) * COS(RADIANS(x1.decl))
                    * (x1.ra - rc1.wm_ra) * COS(RADIANS(x1.decl))
                      / (x1.ra_err * x1.ra_err + rc1.wm_ra_err * rc1.wm_ra_err)
                   +  (x1.decl - rc1.wm_decl) * (x1.decl - rc1.wm_decl)
                      / (x1.decl_err * x1.decl_err + rc1.wm_decl_err * rc1.wm_decl_err)
                   ) AS r1
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
            query = """\
            DELETE
              FROM temprunningcatalog
             WHERE runcat = %s
               AND xtrsrc = %s
            """
            for j in range(len(runcat)):
                print "\nThrowing away from temruncat:", runcat[j], xtrsrc[j]
                cursor.execute(query, (runcat[j], xtrsrc[j]))
                if not AUTOCOMMIT:
                    conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()


def _insert_multiple_assocs(conn):
    """Insert sources with multiple associations

    -2- Here, we take care of the extractedsources that have the 
    same single running catalogue source as counterpart, 
    i.e. the one-to-many associations.

    In this case, new entries in the runningcatalogue will be made
    (for every extractedsource one), which will replace the existing one 
    of the runningcatalog. Therefore, we swap the (multiple) extractedsource 
    ids with the runningcatalog id.

    NOTE:
    1. TODO, see also comment in _flag_multiple_counterparts_in_runningcatalog()
    We should catch the case where we have many-to-many relations.
    2. TODO: Check where clause of query
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
          SELECT t.xtrsrc
                ,t.runcat
                ,3600 * DEGREES(2 * ASIN(SQRT( (r.x - x.x) * (r.x - x.x)
                                             + (r.y - x.y) * (r.y - x.y)
                                             + (r.z - x.z) * (r.z - x.z)
                                             ) / 2) 
                               ) AS distance_arcsec
                ,3600 * sqrt(
                    ( (r.wm_ra * cos(RADIANS(r.wm_decl)) - x.ra * cos(RADIANS(x.decl)))
                     *(r.wm_ra * cos(RADIANS(r.wm_decl)) - x.ra * cos(RADIANS(x.decl)))
                    ) 
                    / (r.wm_ra_err * r.wm_ra_err + x.ra_err * x.ra_err)
                    + ((r.wm_decl - x.decl) * (r.wm_decl - x.decl)) 
                    / (r.wm_decl_err * r.wm_decl_err + x.decl_err * x.decl_err)
                            ) as r
                ,1
            FROM temprunningcatalog t
                ,runningcatalog r
                ,extractedsource x
           WHERE t.runcat = r.id
             AND t.xtrsrc = x.id
             AND t.runcat IN (SELECT runcat
                               FROM temprunningcatalog
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


def _insert_first_of_assocs(conn):
    """Insert identical ids

    -3- And, we have to insert identical ids to identify a light-curve
    starting point.
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
          SELECT xtrsrc
                ,xtrsrc
                ,0
                ,0
                ,2
            FROM temprunningcatalog
           WHERE xtrsrc IN (SELECT xtrsrc
                                 FROM temprunningcatalog
                               GROUP BY xtrsrc
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
          FROM assocxtrsource
         WHERE xtrsrc IN (SELECT xtrsrc
                               FROM temprunningcatalog
                             GROUP BY xtrsrc
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


def _insert_multiple_assocs_runcat(conn):
    """Insert new ids of the sources in the running catalogue
    
    """
    #TODO: Add runningcatalog_flux as well

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
          /*,avg_I_peak
          ,avg_I_peak_sq
          ,avg_weight_peak
          ,avg_weighted_I_peak
          ,avg_weighted_I_peak_sq*/
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
                /*,avg_I_peak
                ,avg_I_peak_sq
                ,avg_weight_peak
                ,avg_weighted_I_peak
                ,avg_weighted_I_peak_sq*/
            FROM temprunningcatalog
           WHERE xtrsrc IN (SELECT xtrsrc
                              FROM temprunningcatalog
                            GROUP BY xtrsrc
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


def _flag_old_assocs_runcat(conn):
    """Here the old assocs in runcat will be deleted."""

    # TODO: Consider setting row to inactive instead of deleting
    try:
        cursor = conn.cursor()
        query = """\
        DELETE
          FROM runningcatalog
         WHERE xtrsrc IN (SELECT xtrsrc
                               FROM temprunningcatalog
                             GROUP BY xtrsrc
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


def _flag_multiple_assocs(conn):
    """Delete the multiple assocs from the temporary running catalogue table"""

    try:
        cursor = conn.cursor()
        query = """\
        DELETE
          FROM temprunningcatalog
         WHERE xtrsrc IN (SELECT xtrsrc
                               FROM temprunningcatalog
                             GROUP BY xtrsrc
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


def _insert_single_assocs(conn):
    """Insert remaining 1-1 associations into assocxtrsource table
    
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
        ,3600 * DEGREES(2 * ASIN(SQRT( (r.x - x.x) * (r.x - x.x)
                                     + (r.y - x.y) * (r.y - x.y)
                                     + (r.z - x.z) * (r.z - x.z)
                                     ) / 2) 
                       ) AS distance_arcsec
        ,3600 * SQRT( (r.wm_ra * cos(RADIANS(r.wm_decl)) - x.ra * cos(RADIANS(x.decl)))
                     * (r.wm_ra * cos(RADIANS(r.wm_decl)) - x.ra * cos(RADIANS(x.decl))) 
                       / (r.wm_ra_err * r.wm_ra_err + x.ra_err * x.ra_err)
                    + (r.wm_decl - x.decl) * (r.wm_decl - x.decl)
                      / (r.wm_decl_err * r.wm_decl_err + x.decl_err * x.decl_err)
                    ) AS r
        ,3
    FROM temprunningcatalog t
        ,runningcatalog r
        ,extractedsource x
   WHERE t.runcat = r.id
     AND t.xtrsrc = x.id
"""
        cursor.execute(query)
        if not AUTOCOMMIT:
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
      ,runcat
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
WHERE id = %s
"""
        for result in results:
            cursor.execute(query, tuple(result))
            if not AUTOCOMMIT:
                conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()

def _update_runningcatalog_flux(conn):
    """Update the runningcatalog_flux
    
    Based on the runcat ids in tempruncat, the corresponding
    entries in runcat_flux should be updated.
    
    
    """

    #TODO: It is possible that for the current runcat source,
    # no flux entries exist
    try:
        cursor = conn.cursor()
        query = """\
SELECT f_datapoints
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
      ,runcat
      ,band
      ,stokes
  FROM temprunningcatalog
        """
        cursor.execute(query)
        results = cursor.fetchall()
        query = """\
UPDATE runningcatalog_flux
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
WHERE xtrsrc = %s
"""
        for result in results:
            cursor.execute(query, tuple(result))
            if not AUTOCOMMIT:
                conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()


def _count_known_sources(conn, image_id, deRuiter_r):
    """Count number of extracted sources that are known in the running
    catalog"""

    cursor = conn.cursor()
    try:
        query = """\
        SELECT COUNT(*)
          FROM extractedsource x0
              ,image
              ,runningcatalog b0
         WHERE x0.image = %s
           AND x0.image = image.id
           AND image.dataset = b0.dataset
           AND b0.zone BETWEEN x0.zone - cast(0.025 as integer)
                           AND x0.zone + cast(0.025 as integer)
           AND b0.wm_decl BETWEEN x0.decl - 0.025
                              AND x0.decl + 0.025
           AND b0.wm_ra BETWEEN x0.ra - alpha(0.025,x0.decl)
                            AND x0.ra + alpha(0.025,x0.decl)
           AND SQRT(  (x0.ra * COS(RADIANS(x0.decl)) - b0.wm_ra * COS(RADIANS(b0.wm_decl)))
                    * (x0.ra * COS(RADIANS(x0.decl)) - b0.wm_ra * COS(RADIANS(b0.wm_decl)))
                    / (x0.ra_err * x0.ra_err + b0.wm_ra_err * b0.wm_ra_err)
                   + (x0.decl - b0.wm_decl) * (x0.decl - b0.wm_decl)
                    / (x0.decl_err * x0.decl_err + b0.wm_decl_err * b0.wm_decl_err)
                   ) < %s
        """
        cursor.execute(query, (image_id, deRuiter_r/3600.))
        y = cursor.fetchall()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()



def _insert_new_source_runcat(conn, image_id):
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
        ,image.dataset
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
         LEFT OUTER JOIN temprunningcatalog trc0
         ON x0.id = trc0.xtrsrc
        ,image 
   WHERE trc0.xtrsrc IS NULL
     AND x0.image = image.id
     AND x0.image = %s
"""
        cursor.execute(query, (image_id,))
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()

def _insert_new_assocs(conn, image_id):
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

    cursor = conn.cursor()
    try:
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
     AND r0.xtrsrc IN (SELECT x1.id
                      FROM extractedsource x1
                           LEFT OUTER JOIN temprunningcatalog trc1
                           ON x1.id = trc1.xtrsrc
                          ,image
                     WHERE trc1.xtrsrc IS NULL
                       AND x1.image = image.id
                       AND image.id = %s
                      )
"""
        cursor.execute(query, (image_id,))
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()

def _insert_new_source_runcat_flux(conn, image_id):
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
        ,image.band
        ,image.stokes
        ,1
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
        ,image
        ,extractedsource x0
   WHERE x0.image = image.id
     AND x0.id = r0.xtrsrc
     AND r0.xtrsrc IN (SELECT x1.id
                         FROM extractedsource x1
                              LEFT OUTER JOIN temprunningcatalog trc1
                              ON x1.id = trc1.xtrsrc
                             ,image
                        WHERE trc1.xtrsrc IS NULL
                          AND x1.image = image.id
                          AND image.id = %s
                      )
"""
        cursor.execute(query, (image_id,))
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()


def _associate_across_frequencies(conn, dataset, image_id, deRuiter_r=DERUITER_R):
    """Associate sources in running catalog across frequency bands

    The dimensionless distance between two sources is given by the
    "De Ruiter radius", see Ch2&3 of thesis Scheers.

    Here we use a default value of deRuiter_r = 3.717/3600. for a
    reliable association.
    """
    return
    try:
        cursor = conn.cursor()
        query = """\
        SELECT COUNT(*)
              /*r1.xtrsrc AS runcat_id
              ,r1.band AS band
              ,r2.xtrsrc AS assoc_runcat_id
              ,r2.band AS assoc_band*/
          FROM runningcatalog r1
              ,runningcatalog r2
              ,image im1
         WHERE r1.dataset = %s
           AND im1.id = %s
           AND r1.band = im1.band
           AND r2.dataset = r1.dataset
           AND r2.band <> r1.band
           AND r2.zone BETWEEN CAST(FLOOR(r1.decl - 0.025) AS INTEGER)
                           AND CAST(FLOOR(r1.decl + 0.025) AS INTEGER)
           AND r2.decl BETWEEN r1.decl - 0.025
                           AND r1.decl + 0.025
           AND r2.ra BETWEEN r1.ra - alpha(0.025, r1.decl)
                         AND r1.ra + alpha(0.025, r1.decl)
           AND SQRT( ((r1.ra * COS(RADIANS(r1.decl)) - r2.ra * COS(RADIANS(r2.decl))) 
                      * (r1.ra * COS(RADIANS(r1.decl)) - r2.ra * COS(RADIANS(r2.decl))))
                     / (r1.ra_err * r1.ra_err + r2.ra_err * r2.ra_err)
                   + ((r1.decl - r2.decl) * (r1.decl - r2.decl))
                    / (r1.decl_err * r1.decl_err + r2.decl_err * r2.decl_err)
                   ) < %s
        """
        cursor.execute(query, (dataset, image_id, deRuiter_r/3600.))
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s; for reason %s" % (query, e))
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

    _empty_temprunningcatalog(conn)
    #+------------------------------------------------------+
    #| Here we select all extracted sources that have one or|
    #| more counterparts in the runningcatalog              |
    #+------------------------------------------------------+
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
    #_update_runningcatalog_flux(conn)
    #_count_known_sources(conn, image_id, deRuiter_r)
    #+-------------------------------------------------------+
    #| Here we take care of the extracted sources that could |
    #| not be associated with any runningcatalog source      |
    #+-------------------------------------------------------+
    _insert_new_source_runcat(conn, image_id)
    _insert_new_assocs(conn, image_id)
    _insert_new_source_runcat_flux(conn, image_id)
    _empty_temprunningcatalog(conn)
    #_associate_across_frequencies(conn, dataset, image_id, deRuiter_r)


def select_single_epoch_detection(conn, dsid):
    """Select sources from running catalog which have only one detection"""

    results = []
    cursor = conn.cursor()
    try:
        query = """\
SELECT xtrsrc
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

    cursor = conn.cursor()
    try:
        query = """\
SELECT im.taustart_ts, im.tau_time, ex.i_peak, ex.i_peak_err, ex.id
FROM extractedsource ex, assocxtrsource ax, image im
WHERE ax.xtrsrc in
    (SELECT xtrsrc FROM assocxtrsource WHERE xtrsrc = %s)
  AND ex.id = ax.xtrsrc
  AND ex.image = im.id
ORDER BY im.taustart_ts"""
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
SELECT
     xtrsrc
    ,dataset
    ,datapoints
    ,wm_ra
    ,wm_decl
    ,wm_ra_err
    ,wm_decl_err
    ,t1.V_inter / t1.avg_i_peak as V
    ,t1.eta_inter / t1.avg_weight_peak as eta
FROM
    (SELECT
          xtrsrc
         ,dataset
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
      WHERE dataset = %s
      ) t1
  WHERE t1.V_inter / t1.avg_i_peak > %s
    AND t1.eta_inter / t1.avg_weight_peak > %s
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
            FROM (select id
                        ,ra
                        ,decl
                        ,ra_err
                        ,decl_err
                        ,cast(floor(decl - %s) as integer) as zone_min
                        ,cast(floor(decl + %s) as integer) as zone_max
                        ,ra + alpha(%s, decl) as ra_max
                        ,ra - alpha(%s, decl) as ra_min
                        ,decl - %s as decl_min
                        ,decl + %s as decl_max
                        ,x
                        ,y
                        ,z
                    from extractedsource
                   where image = %s
                 ) x0
                ,catalogedsource c0
           WHERE c0.zone BETWEEN zone_min AND zone_max
             AND c0.decl BETWEEN decl_min AND decl_max
             AND c0.ra BETWEEN ra_min AND ra_max
             and x0.x*c0.x + x0.y*c0.y + x0.z*c0.z > %s
             AND SQRT(  (x0.ra * COS(RADIANS(x0.decl)) - c0.ra * COS(RADIANS(c0.decl)))
                      * (x0.ra * COS(RADIANS(x0.decl)) - c0.ra * COS(RADIANS(c0.decl)))
                      / (x0.ra_err * x0.ra_err + c0.ra_err * c0.ra_err)
                     + (x0.decl - c0.decl) * (x0.decl - c0.decl)
                      / (x0.decl_err * x0.decl_err + c0.decl_err * c0.decl_err)
                     ) < %s
        """
        cursor.execute(query, (BG_DENSITY, radius, radius, radius, radius, radius, radius, 
                               image_id,math.cos(math.pi*radius/180.), deRuiter_r/3600.))
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error, e:
        logging.warn("Query failed: %s." % query)
        raise
    finally:
        cursor.close()


def associate_with_catalogedsources(conn, image_id, radius=0.025, deRuiter_r=DERUITER_R):
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
    zoneheight = 1.0
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
   ,3600 * DEGREES(2 * ASIN(SQRT(
       (rc.x - cs.x) * (rc.x - cs.x)
       + (rc.y - cs.y) * (rc.y - cs.y)
       + (rc.z - cs.z) * (rc.z - cs.z)
       ) / 2)
   ) AS assoc_distance_arcsec
   ,SQRT( (rc.wm_ra - cs.ra) * COS(RADIANS(rc.wm_decl)) * (rc.wm_ra - cs.ra) * COS(RADIANS(rc.wm_decl))
   / (cast(rc.wm_ra_err as double precision) * rc.wm_ra_err + cs.ra_err * cs.ra_err)
   + (rc.wm_decl - cs.decl) * (rc.wm_decl - cs.decl)
   / (cast(rc.wm_decl_err as double precision) * rc.wm_decl_err + cs.decl_err * cs.decl_err)
   ) AS assoc_r
FROM (
     SELECT
     wm_ra - alpha(%%s, wm_decl) as ra_min
    ,wm_ra + alpha(%%s, wm_decl) as ra_max
    ,CAST(FLOOR((wm_decl - %%s) / %%s) AS INTEGER) as zone_min
    ,CAST(FLOOR((wm_decl + %%s) / %%s) AS INTEGER) as zone_max
    ,wm_decl - %%s as decl_min
    ,wm_decl + %%s as decl_max
    ,x
    ,y
    ,z
    ,wm_ra
    ,wm_decl
    ,wm_ra_err
    ,wm_decl_err
    FROM runningcatalog
    WHERE xtrsrc = %%s
    ) rc
    ,catalogedsources cs
    ,catalogs c
WHERE
      %(catalog_filter)s
  cs.cat_id = c.catid
  AND cs.zone BETWEEN rc.zone_min AND rc.zone_max
  AND cs.ra BETWEEN rc.ra_min and rc.ra_max
  AND cs.decl BETWEEN rc.decl_min and rc.decl_max
  AND cs.x * rc.x + cs.y * rc.y + cs.z * rc.z > COS(RADIANS(%%s))
""" % {'catalog_filter': catalog_filter}
#  AND cs.ra BETWEEN rc.wm_ra - alpha(%%s, rc.wm_decl)
#                AND rc.wm_ra + alpha(%%s, rc.wm_decl)
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
        cursor.execute(query,  (radius, radius, radius, zoneheight,
                                radius, zoneheight, radius, radius,
                                srcid, radius, assoc_r))
        results = cursor.fetchall()
        results = [
            {'catsrcid': result[0], 'catsrcname': result[1],
             'catid': result[2], 'catname': result[3],
             'ra': result[4], 'decl': result[5],
             'ra_err': result[6], 'decl_err': result[7],
             'dist_arcsec': result[8], 'assoc_r': result[9]}
            for result in results]
    except db.Error, e:
        query = query % (radius, radius, radius, zoneheight,
                         radius, zoneheight,
                         radius, radius, srcid, radius, assoc_r)
        logging.warn("Query failed: %s", query)
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

    cursor = conn.cursor()
    query = """\
SELECT rc.wm_ra
      ,rc.wm_decl
      ,t2.xtrsrc2
      ,t2.monitorid
FROM
   (SELECT ml.monitorid AS monitorid
          ,ml.xtrsrc AS xtrsrc_id2
          ,t1.xtrsrc AS xtrsrc_id
          ,t1.xtrsrc AS xtrsrc
          ,t1.image AS image_id
          ,ml.dataset AS dataset
      FROM monitoringlist ml
      LEFT OUTER JOIN 
          (SELECT ax.xtrsrc as xtrsrc_id
                ,ex.id as xtrsrcid
                ,ex.image as image_id
                ,ax.xtrsrc as xtrsrc
            FROM extractedsource ex, assocxtrsource ax
            WHERE ex.id = ax.xtrsrc
            AND ex.image = %s
          ) t1
      ON ml.xtrsrc = t1.xtrsrc
      WHERE t1.xtrsrc IS NULL
    ) t2, image im, runningcatalog rc
WHERE im.dataset = t2.dataset
AND im.id = %s
AND rc.xtrsrc = t2.xtrsrc2
"""
    try:
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
SELECT COUNT(*) FROM monitoringlist WHERE xtrsrc_id = %s"""
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
    for xtrsrc_id, monitorid, result in results:
        ra, dec, ra_err, dec_err, peak, peak_err, flux, flux_err, sigma, \
            semimajor, semiminor, pa = result
        x = math.cos(math.radians(dec)) * math.cos(math.radians(ra))
        y = math.cos(math.radians(dec)) * math.sin(math.radians(ra))
        z = math.sin(math.radians(dec))
        # Always insert them into extractedsource
        query = """\
        INSERT INTO extractedsource
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
          ,semimajor
          ,semiminor
          ,pa
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
          )
"""
        try:
            cursor.execute(
                query, (image_id, int(math.floor(dec)), ra, dec, ra_err, dec_err,
                        x, y, z, sigma, peak, peak_err, flux, flux_err,
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
        if xtrsrc_id < 0:
            # Insert as new source into the running catalog
            # and update the monitoringlist.xtrsrc
            query = """\
INSERT INTO runningcatalog
    (xtrsrc_id
    ,dataset
    ,band
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
    SELECT
        t0.id
        ,im.dataset
        ,im.band
        ,1
        ,t0.zone
        ,t0.ra
        ,t0.decl
        ,t0.ra_err
        ,t0.decl_err
        ,t0.ra
        ,t0.decl
        ,t0.ra_err
        ,t0.decl_err
        ,t0.x
        ,t0.y
        ,t0.z
        ,t0.flux
        ,t0.flux_sq
        ,t0.flux
        ,t0.flux
        ,t0.flux_sq
    FROM (SELECT
        ex.image
        ,ex.id
        ,ex.zone
        ,ex.ra
        ,ex.decl
        ,ex.ra_err
        ,ex.decl_err
        ,ex.x
        ,ex.y
        ,ex.z 
        ,ex.i_peak as flux
        ,ex.i_peak * ex.i_peak as flux_sq
        FROM extractedsource ex
        WHERE ex.id = %s
        ) as t0, image im
    WHERE im.id = %s
"""
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
  (
  xtrsrc_id,
  xtrsrc,
  assoc_weight,
  assoc_distance_arcsec,
  type,
  assoc_r, loglr
  )
VALUES
  (%s, %s, 0, 0, 0, 0, 0)"""
            try:
                cursor.execute(query, (xtrsrcid, xtrsrcid))
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
            query = """\
UPDATE monitoringlist SET xtrsrc_id=%s, image_id=%s WHERE monitorid=%s"""
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
INSERT INTO assocxtrsource (xtrsrc_id, xtrsrc, distance_arcsec, type, r, loglr)
VALUES (%s, %s, 0, 0, 0, 0)"""
            try:
                cursor.execute(query, (xtrsrc_id, xtrsrcid))
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

    A check is performed where the base id (asocxtrsources.xtrsrc)
    for the light curve of the transient is queried, by assuming the
    current srcid falls within a light curve
    (assocxtrsource.xtrsrc = srcid). If this id already in the
    table, we replace that transient by this one.

    The reason we check the assocxtrsource, is that when there is a
    double source match, the main source id (as stored in the
    runningcatalog) may change; this results in transients already
    stored having a different id than the current transient, while
    they are in the fact the same transient. The xtrsrc_id of the
    stored id, however, should still be in the light curve of the new
    xtrsrc_id, as an xtrsrc. We thus update the transient,
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
SELECT transientid FROM transients WHERE xtrsrc_id IN (
SELECT xtrsrc FROM assocxtrsource WHERE xtrsrc_id = %s
)
"""
        cursor.execute(query, (srcid,))
        transientid = cursor.fetchone()
        if transientid:  # update/replace existing source
            query = """\
UPDATE transients SET
    xtrsrc_id = %s
    ,eta = %s
    ,V = %s
WHERE transientid = %s
"""
            cursor.execute(query, (srcid, transientid[0],
                                   transient.eta, transient.V))
        else:  # insert new source
            # First, let'find the current xtrsrc_id that belongs to the
            # current image: this is the trigger source id
            if images is None:
                image_set = ""
            else:
                image_set = ", ".join([str(image) for image in images])
            query = """\
SELECT ex.id FROM extractedsource ex, assocxtrsource ax
WHERE ex.image IN (%s) AND ex.id = ax.xtrsrc AND
ax.xtrsrc = %%s""" % image_set
            cursor.execute(query, (srcid,))
            trigger_srcid = cursor.fetchone()[0]
            query = """\
INSERT INTO transients (xtrsrc_id, eta, V, trigger_xtrsrc_id)
VALUES (%s, %s, %s, %s)
"""
            cursor.execute(query, (srcid, transient.eta, transient.V,
                                   trigger_srcid))
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error:
        logging.warn("Query %s failed", query)
        logging.debug("Query %s failed", query)
        cursor.close()
        raise
    try:
        query = """\
INSERT INTO monitoringlist
(xtrsrc_id, ra, decl, dataset)
SELECT ex.id, 0, 0, %s
FROM extractedsource ex
WHERE ex.id = %s
  AND
    ex.id NOT IN
    (SELECT xtrsrc_id FROM monitoringlist)
"""
        cursor.execute(query, (dataset, srcid))
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error:
        query = query % srcid
        logging.warn("Query %s failed", query)
        cursor.close()
        raise
    cursor.close()
