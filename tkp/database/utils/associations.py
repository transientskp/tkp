# LOFAR Transients Key Project
#
# Bart Scheers, Evert Rol, Tim Staley 
#
# discovery@transientskp.org
#

"""
A collection of back end subroutines (mostly SQL queries), 

In this module we deal with source association.

"""

import sys, os
import logging
import monetdb.sql as db
from tkp.config import config

logger = logging.getLogger(__name__)

AUTOCOMMIT = config['database']['autocommit']
DERUITER_R = config['source_association']['deruiter_radius']
BG_DENSITY = config['source_association']['bg-density']

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
    #| Association pairs are of the sequence runcat-xtrsrc, |
    #| which may be matching one of the following cases:    |
    #| many-to-many, many-to-one, one-to-many, one-to-many  |
    #+------------------------------------------------------+
    _insert_temprunningcatalog(conn, image_id, deRuiter_r)
    #+------------------------------------------------------+
    #| Here we process (flag) the many-to-many associations.|
    #+------------------------------------------------------+
    # _process_many_to_many() 
    _flag_many_to_many_tempruncat(conn)
    #+------------------------------------------------------+
    #| After this, the assocs have been reduced to many-to-1|
    #| which are treated identical as 1-to-1, and 1-to-many.|
    #+------------------------------------------------------+
    # _process_many_to_1() => process_1_to_1()
    #+------------------------------------------------------+
    #| Here we process the one-to-many associations.        |
    #+------------------------------------------------------+
    _insert_1_to_many_runcat(conn)
    _insert_1_to_many_runcat_flux(conn)
    _insert_1_to_many_basepoint_assoc(conn)
    _insert_1_to_many_assoc(conn)
    _insert_1_to_many_monitoringlist(conn)
    #_insert_1_to_many_transient(conn)
    _delete_1_to_many_inactive_assoc(conn)
    _delete_1_to_many_inactive_runcat_flux(conn)
    _flag_1_to_many_inactive_runcat(conn)
    _flag_1_to_many_inactive_tempruncat(conn)
    _delete_1_to_many_inactive_monitoringlist(conn)
    _delete_1_to_many_inactive_transient(conn)
    #+-----------------------------------------------------+
    #| Here we process the one-to-one associations         |
    #+-----------------------------------------------------+
    # _process_1_to_1()
    _insert_1_to_1_assoc(conn)
    _update_1_to_1_runcat(conn)
    _select_for_update_1_to_1_runcat_flux(conn)
    #+-------------------------------------------------------+
    #| Here we take care of the extracted sources that could |
    #| not be associated with any runningcatalog source      |
    #+-------------------------------------------------------+
    _insert_new_runcat(conn, image_id)
    _insert_new_runcat_flux(conn, image_id)
    _insert_new_assoc(conn, image_id)
    _insert_new_monitoringlist(conn, image_id)
    if image_id == 2:
        sys.exit()
    _go_back_to_other_images_and_do_a_forcedfit_in_non_rejected_images(conn, image_id)
    #_then_we_need_to_merge_results_from_ff_into_extr/assoc/runcat/runcat_flux/monlist()
    #+-------------------------------------------------------+
    #| New sources are added to transient table as well, but |
    #| that is done in the transient_search recipe.          |
    #+-------------------------------------------------------+
    _empty_temprunningcatalog(conn)
    _delete_inactive_runcat(conn)

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

#def associate_catalogued_sources_in_area(conn, ra, dec, radius, deRuiter_r=DERUITER_R/3600.):
#    pass


###############################################################################################
# Subroutines...
# Here be SQL dragons.
###############################################################################################

def _empty_temprunningcatalog(conn):
    """Initialize the temporary storage table

    Initialize the temporary table temprunningcatalog which contains
    the current observed sources.
    """

    try:
        cursor = conn.cursor()
        query = """\
        DELETE FROM temprunningcatalog;
        """
        cursor.execute(query)
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error, e:
        logger.warn("Failed on query\n%s" % query)
        raise
    finally:
        cursor.close()


def _insert_temprunningcatalog(conn, image_id, deRuiter_r, radius=0.03):
    """Select matched sources

    Here we select the extractedsource that have a positional match
    with the sources in the running catalogue table (runningcatalog).
    Those sources which *do* have a potential match, will be inserted into the
    temporary running catalogue table (temprunningcatalog).

    See also:
    http://docs.transientskp.org/tkp/database/schema.html#temprunningcatalog

    Explanation of some column name prefixes/suffixes used in the SQL query:

    - avg_X := average of X
    - avg_X_sq := average of X^2
    - avg_weight_X := average of weight of X, i.e. mean( 1/error^2 )
    - avg_weighted_X := average of weighted X,
         i.e. mean(X/error^2)
    - avg_weighted_X_sq := average of weighted X^2,
         i.e. mean(X^2/error^2)

    This result set might contain multiple associations (1-n,n-1)
    for a single known source in runningcatalog.

    The n-1 assocs will be treated similar as the 1-1 assocs.
    
    NOTE: Beware of the extra condition on x0.image in the WHERE clause, 
    preventing the query to grow exponentially in response time
    """

    deRuiter_red = float(deRuiter_r) / 3600.
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
             AND x0.image = %s
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
        cursor.execute(query, (image_id, image_id,
                                radius, radius, radius, radius, 
                                radius, radius, deRuiter_red))
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error, e:
        q = query % (image_id, image_id,
                        radius, radius, radius, radius, 
                        radius, radius, deRuiter_red)
        logger.warn("Failed on query\n%s." % q)
        raise
    finally:
        cursor.close()

def _flag_many_to_many_tempruncat(conn):
    """Select the many-to-many association pairs in temprunningcatalog.

    By flagging the many-to-many associations, we reduce the
    processing to one-to-many and many-to-one (identical to one-to-one)
    relationships
    """

    try:
        cursor = conn.cursor()
        # This one selects the farthest out of the many-to-many assocs
        query = """\
UPDATE temprunningcatalog
   SET inactive = TRUE
 WHERE EXISTS (SELECT runcat
                     ,xtrsrc
                 FROM (SELECT t1.runcat
                             ,t1.xtrsrc
                         FROM (SELECT xtrsrc
                                     ,MIN(r) as min_r
                                 FROM temprunningcatalog
                                WHERE runcat IN (SELECT runcat
                                                   FROM temprunningcatalog
                                                  WHERE runcat IN (SELECT runcat
                                                                     FROM temprunningcatalog
                                                                    WHERE xtrsrc IN (SELECT xtrsrc
                                                                                       FROM temprunningcatalog
                                                                                     GROUP BY xtrsrc
                                                                                     HAVING COUNT(*) > 1
                                                                                    )
                                                                  )
                                                 GROUP BY runcat
                                                 HAVING COUNT(*) > 1
                                                )
                                  AND xtrsrc IN (SELECT xtrsrc
                                                   FROM temprunningcatalog
                                                 GROUP BY xtrsrc
                                                 HAVING COUNT(*) > 1
                                                )
                               GROUP BY xtrsrc
                              ) t0
                             ,(SELECT runcat
                                     ,xtrsrc
                                     ,r
                                 FROM temprunningcatalog
                                WHERE runcat IN (SELECT runcat
                                                   FROM temprunningcatalog
                                                  WHERE runcat IN (SELECT runcat
                                                                     FROM temprunningcatalog
                                                                    WHERE xtrsrc IN (SELECT xtrsrc
                                                                                       FROM temprunningcatalog
                                                                                     GROUP BY xtrsrc
                                                                                     HAVING COUNT(*) > 1
                                                                                    )
                                                                  )
                                                 GROUP BY runcat
                                                 HAVING COUNT(*) > 1
                                                )
                                  AND xtrsrc IN (SELECT xtrsrc
                                                   FROM temprunningcatalog
                                                 GROUP BY xtrsrc
                                                 HAVING COUNT(*) > 1
                                                )
                              ) t1
                        WHERE t0.xtrsrc = t1.xtrsrc
                          AND t0.min_r < t1.r
                      ) t2
                WHERE t2.runcat = temprunningcatalog.runcat
                  AND t2.xtrsrc = temprunningcatalog.xtrsrc
              )
;
"""
        cursor.execute(query)
        if not AUTOCOMMIT:
            conn.commit()
        #results = zip(*cursor.fetchall())
        #if len(results) != 0:
        #    runcat = results[0]
        #    xtrsrc = results[1]
        #    query = """\
        #    UPDATE temprunningcatalog
        #       SET inactive = TRUE
        #     WHERE runcat = %s
        #       AND xtrsrc = %s
        #    """
        #    for j in range(len(runcat)):
        #        logger.info("Many-to-many in tempruncat set to inactive: "
        #                    "%s %s " % (runcat[j], xtrsrc[j]))
        #        cursor.execute(query, (runcat[j], xtrsrc[j]))
        #        if not AUTOCOMMIT:
        #            conn.commit()
        #    #sys.exit()
        cursor.close()
    except db.Error, e:
        logger.warn("Failed on query nr %s." % query)
        raise

#def _flag_many_to_many_tempruncat2(conn):
#    """Select the many-to-many association pairs in temprunningcatalog.
#
#    By flagging the many-to-many associations, we reduce the
#    processing to one-to-many and many-to-one (identical to one-to-one)
#    relationships
#    """
#
#    try:
#        cursor = conn.cursor()
#        # This one selects the farthest out of the many-to-many assocs
#        query = """\
#SELECT t1.runcat
#      ,t1.xtrsrc
#  FROM (SELECT xtrsrc
#              ,MIN(r) as min_r
#          FROM temprunningcatalog
#         WHERE runcat IN (SELECT runcat
#                            FROM temprunningcatalog
#                           WHERE runcat IN (SELECT runcat
#                                              FROM temprunningcatalog
#                                             WHERE xtrsrc IN (SELECT xtrsrc
#                                                                FROM temprunningcatalog
#                                                              GROUP BY xtrsrc
#                                                              HAVING COUNT(*) > 1
#                                                             )
#                                           )
#                          GROUP BY runcat
#                          HAVING COUNT(*) > 1
#                         )
#           AND xtrsrc IN (SELECT xtrsrc
#                            FROM temprunningcatalog
#                          GROUP BY xtrsrc
#                          HAVING COUNT(*) > 1
#                         )
#        GROUP BY xtrsrc
#       ) t0
#      ,(SELECT runcat
#              ,xtrsrc
#              ,r
#          FROM temprunningcatalog
#         WHERE runcat IN (SELECT runcat
#                            FROM temprunningcatalog
#                           WHERE runcat IN (SELECT runcat
#                                              FROM temprunningcatalog
#                                             WHERE xtrsrc IN (SELECT xtrsrc
#                                                                FROM temprunningcatalog
#                                                              GROUP BY xtrsrc
#                                                              HAVING COUNT(*) > 1
#                                                             )
#                                           )
#                          GROUP BY runcat
#                          HAVING COUNT(*) > 1
#                         )
#           AND xtrsrc IN (SELECT xtrsrc
#                            FROM temprunningcatalog
#                          GROUP BY xtrsrc
#                          HAVING COUNT(*) > 1
#                         )
#       ) t1
# WHERE t0.xtrsrc = t1.xtrsrc
#   AND t0.min_r < t1.r
#        """
#        cursor.execute(query)
#        results = zip(*cursor.fetchall())
#        if len(results) != 0:
#            runcat = results[0]
#            xtrsrc = results[1]
#            query = """\
#            UPDATE temprunningcatalog
#               SET inactive = TRUE
#             WHERE runcat = %s
#               AND xtrsrc = %s
#            """
#            for j in range(len(runcat)):
#                logger.info("Many-to-many in tempruncat set to inactive: "
#                            "%s %s " % (runcat[j], xtrsrc[j]))
#                cursor.execute(query, (runcat[j], xtrsrc[j]))
#                if not AUTOCOMMIT:
#                    conn.commit()
#            #sys.exit()
#        cursor.close()
#    except db.Error, e:
#        logger.warn("Failed on query nr %s." % query)
#        raise

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
           WHERE inactive = FALSE
             AND runcat IN (SELECT runcat
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
        logger.warn("Failed on query:\n%s" % query)
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
             AND trc0.inactive = FALSE
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
        logger.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()

def _insert_1_to_many_basepoint_assoc(conn):
    """Insert base points for one-to-many associations

    Before continuing, we have to insert the 'base points' of the associations, 
    i.e. the links between the new runningcatalog entries
    and their associated (new) extractedsources.
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
           WHERE t.inactive = FALSE
             AND t.xtrsrc = r.xtrsrc
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
        logger.warn("Failed on query:\n%s" % query)
        raise
    finally:
        cursor.close()

def _insert_1_to_many_assoc(conn):
    """Insert links into the association table between the new runcat 
    entries and the old extractedsources.
    (New to New ('basepoint') links have been added earlier).

    In this case, new entries in the runningcatalog and runningcatalog_flux
    were already added (for every extractedsource one), which will replace
    the existing ones in the runningcatalog.
    Therefore, we have to update the references to these new ids as well.
    So, we will append to assocxtrsource and delete the entries from
    runningcatalog_flux.

    NOTE:
    1. We do not update the distance_arcsec and r values of the pairs.

    TODO:
    1. Why not?

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
           WHERE t.inactive = FALSE
             AND t.xtrsrc = r.xtrsrc
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
        logger.warn("Failed on query:\n%s" % query)
        raise
    finally:
        cursor.close()

def _insert_1_to_many_monitoringlist(conn):
    """Insert one-to-many in monitoringlist

    In case where we have a non-user-entry source in the monitoringlist 
    that goes one-to-many in the associations, we have to "split" it up 
    into the new runcat ids and delete the old runcat.

    TODO: See discussion in issues #3564 & #3919 how to proceed

    """

    try:
        cursor = conn.cursor()
        query = """\
        INSERT INTO monitoringlist
          (runcat
          ,ra
          ,decl
          ,dataset
          )
          SELECT r.id AS runcat
                ,r.wm_ra AS ra
                ,r.wm_decl AS decl
                ,r.dataset
            FROM temprunningcatalog t
                ,runningcatalog r
           WHERE t.inactive = FALSE
             AND t.xtrsrc = r.xtrsrc
             AND t.runcat IN (SELECT runcat
                                FROM temprunningcatalog
                               WHERE inactive = FALSE
                              GROUP BY runcat
                              HAVING COUNT(*) > 1
                             )

        """
        #  /* the old runcat's in monlist that need to be replaced (with the above r.id's : */
        #  select m.runcat
        #    from monitoringlist m
        #        ,runningcatalog r
        #   where m.runcat = r.id
        #     and m.userentry = true
        #     and m.runcat in (select runcat
        #                        from temprunningcatalog
        #                       where inactive = false
        #                      group by runcat
        #                      having count(*) > 1
        #                     )
        cursor.execute(query)
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error, e:
        logger.warn("Failed on query:\n%s" % query)
        raise
    finally:
        cursor.close()

def _insert_1_to_many_transient(conn):
    """Update the runcat id for the one-to-many associations,
    and delete the transient entries of the old runcat id
    (the new ones have been added earlier).

    In this case, new entries in the runningcatalog and runningcatalog_flux
    were already added (for every extractedsource one), which will replace
    the existing ones in the runningcatalog.
    Therefore, we have to update the references to these new ids as well.
    So, we will append these to monitoringlist and delete the entries referring
    to the old runncat.
    """

    try:
        cursor = conn.cursor()
        query = """\
        INSERT INTO transient
          (runcat
          ,siglevel
          ,v
          ,eta
          ,detection_level
          ,trigger_xtrsrc
          ,status
          ,t_start
          )
          SELECT r.id
                ,tr.siglevel
                ,tr.v
                ,tr.eta
                ,tr.detection_level
                ,tr.trigger_xtrsrc
                ,tr.status
                ,tr.t_start
            FROM temprunningcatalog t
                ,runningcatalog r
                ,transient tr
           WHERE t.xtrsrc = r.xtrsrc
             AND t.inactive = FALSE
             AND t.runcat = tr.runcat
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
        logger.warn("Failed on query:\n%s" % query)
        raise
    finally:
        cursor.close()

def _delete_1_to_many_inactive_monitoringlist(conn):
    """Delete the monitoringlist sources of the old runcat

    Since we replaced this runcat.id with multiple new ones, we now
    delete the old one.

    """

    try:
        cursor = conn.cursor()
        query = """\
        DELETE
          FROM monitoringlist
         WHERE userentry = FALSE
           AND id IN (SELECT m.id
                        FROM monitoringlist m
                            ,runningcatalog r
                       WHERE m.runcat = r.id
                         AND r.inactive = TRUE
                     )
        """
        cursor.execute(query)
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error, e:
        logger.warn("Failed on query:\n%s" % query)
        raise
    finally:
        cursor.close()

def _delete_1_to_many_inactive_transient(conn):
    """Delete the transient sources of the old runcat

    Since we replaced this runcat.id with multiple new ones, we now
    delete the old one.

    """

    try:
        cursor = conn.cursor()
        query = """\
        DELETE
          FROM transient
         WHERE id IN (SELECT tr.id
                        FROM transient tr
                            ,runningcatalog r
                       WHERE tr.runcat = r.id
                         AND r.inactive = TRUE
                     )
        """
        cursor.execute(query)
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error, e:
        logger.warn("Failed on query:\n%s" % query)
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
        logger.warn("Failed on query nr %s." % query)
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
        logger.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()

def _flag_1_to_many_inactive_runcat(conn):
    """Flag the old runcat ids in the runningcatalog to inactive

    We do not delete them yet, because we need them later on.
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
        logger.warn("Failed on query:\n%s." % query)
        raise
    finally:
        cursor.close()

def _flag_1_to_many_inactive_tempruncat(conn):
    """Delete the one-to-many associations from temprunningcatalog,
    and delete the inactive rows from runningcatalog.

    We do not delete them yet, because we need them later on.
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
        logger.warn("Failed on query:\n%s" % query)
        raise
    finally:
        cursor.close()

def _insert_1_to_1_assoc(conn):
    """
    Insert remaining associations from temprunningcatalog into assocxtrsource.
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
             AND t.inactive = FALSE
             AND t.xtrsrc = x.id
        """
        cursor.execute(query)
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error, e:
        logger.warn("Failed on query:\n%s." % query)
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
        logger.warn("Failed on query:\n%s" % query)
        raise
    finally:
        cursor.close()

def _select_for_update_1_to_1_runcat_flux(conn):
    """Update the runningcatalog_flux

    Based on the runcat ids in tempruncat, the fluxes of the corresponding
    entries in runcat_flux should be updated.
    If they do not exist yet, they will be inserted

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
        cursor.close()
        if len(results) > 0:
            for result in results:
                _insert_or_update_1_to_1_runcat_flux(conn, tuple(result))
    except db.Error, e:
        logger.warn("Failed on query:\n%s" % query)
        raise

def _insert_or_update_1_to_1_runcat_flux(conn, result):
    """Insert or update the runningcatalog_flux, depending on existing entries

    If the runcat,band,stokes entry does not exist in runcat_flux,
    we need to do an insert, otherwise an update

    NOTE: Together with previous query this should be optimised,
          in order to reduce data I/O
    """

    try:
        cursor = conn.cursor()
        query = """\
        SELECT COUNT(*)
          FROM runningcatalog_flux
         WHERE runcat = %s
           AND band = %s
           AND stokes = %s
        """
        # Be aware that the last items must correspond to the query
        # in _select_for_update_1_to_1_runcat_flux()
        cursor.execute(query, (result[-3], result[-2], result[-1]))
        cnt = cursor.fetchone()[0]
        if cnt == 0:
            query = """\
            INSERT INTO runningcatalog_flux
              (f_datapoints
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
              )
            """
        else:
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
        cursor.execute(query, tuple(result))
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error, e:
        logger.warn("Failed on query:\n%s" % query)
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
        ins = cursor.execute(query, (image_id,))
        #cursor.execute(query, (image_id, image_id,
        #                        radius, radius, radius, radius, radius, radius,
        #                        deRuiter_r/3600.))
        if not AUTOCOMMIT:
            conn.commit()
        if ins > 0:
            logger.info("Added %s new sources to the runningcatalog" % (ins,))
    except db.Error, e:
        q = query % (image_id,)
        logger.warn("Failed on query:\n%s." % q)
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
        logger.warn("Failed on query:\n%s" % q)
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
        logger.warn("Failed on query:\n%s" % q)
        raise
    finally:
        cursor.close()

def _insert_new_monitoringlist(conn, image_id):
    """A new source needs to be added to the monitoringlist.
    
    Except for sources that were detected in the initial image.
    """

    try:
        cursor = conn.cursor()
        query = """\
        INSERT INTO monitoringlist
          (runcat
          ,ra
          ,decl
          ,dataset
          )
          SELECT r0.id AS runcat
                ,r0.wm_ra AS ra
                ,r0.wm_decl AS decl
                ,r0.dataset AS dataset
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
             AND EXISTS (SELECT COUNT(*) 
                           FROM image 
                          WHERE dataset = (SELECT dataset 
                                             FROM image 
                                            WHERE id = %s
                                          )
                         HAVING COUNT(*) <> 1
                        )
        """
        #q = query % (image_id,image_id)
        #print "QUERY:\n",q
        ins = cursor.execute(query, (image_id,image_id))
        if not AUTOCOMMIT:
            conn.commit()
        if ins > 0:
            logger.info("Added %s new sources to the monitoringlist" % (ins,))
    except db.Error, e:
        q = query % (image_id,)
        logger.warn("Failed on query:\n%s" % q)
        raise
    finally:
        cursor.close()

def _go_back_to_other_images_and_do_a_forcedfit_in_non_rejected_images(conn, image_id):
    """Return a list of previous image ids and urls in which
    the new sources were not detected
    
    """

    try:
        cursor = conn.cursor()
        query = """\
        SELECT id
              ,url
          FROM image
         WHERE id <> %s 
           AND rejected = FALSE
           AND dataset = (SELECT dataset 
                            FROM image i 
                           WHERE i.id = %s
                         )
           AND EXISTS (SELECT t0.xtrsrc
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
        cursor.execute(query, (image_id, image_id, image_id))
        results = zip(*cursor.fetchall())
        if not AUTOCOMMIT:
            conn.commit()
        cursor.close()
        
        if len(results) != 0:
            imageids = results[0]
            urls = results[1]
            # Check if the urls are still available
            validurls = []
            for url in urls:
                if os.path.exists(url):
                    validurls.append(url)
                    logger.info("Image %s still available for forced fit" % (os.path.basename(url),))
    except db.Error, e:
        q = query % (image_id,image_id,image_id)
        logger.warn("Failed on query:\n%s" % q)
        raise

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
        logger.warn("Failed on query:\n%s" % query)
        raise
    finally:
        cursor.close()

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
        logger.warn("Query failed:\n%s" % query)
        raise
    finally:
        cursor.close()



