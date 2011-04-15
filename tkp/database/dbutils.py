#
# LOFAR Transients Key Project
#

# Local tkp_lib functionality
import os, errno, time, sys
from datetime import datetime
import monetdb.sql as db
from monetdb.sql import Error as Error
#import MySQLdb as db
#from MySQLdb import Error as Error
import logging
from tkp.settings import DERUITER_R


def loadLSM(ira_min, ira_max, idecl_min, idecl_max, cn1,cn2,cn3, conn):
    raise NotImplementedError
    """
    try:
        cursor = conn.cursor()
        procLoadLSM = "CALL LoadLSM(%s,%s,%s,%s,%s,%s,%s)" % (ira_min,ira_max,idecl_min,idecl_max,cn1,cn2,cn3)
        cursor.execute(procLoadLSM)
    except db.Error, e:
        logging.warn("Failed to insert lsm by procedure LoadLSM")
        raise
    finally:
        cursor.close()
    conn.commit()
    """


def insertExtractedSources(conn, image_id, results):
    """
    This method inserts the sources that were detected by the
    Source Extraction procedures into the "extractedsources" table.
    Therefore, we use a temporary table containing the "raw" detections,
    from which the sources will then be inserted into extractedsourtces.
    """

    try: 
        cursor = conn.cursor()
        
        query = "sql_pre_empty_detections"
        sql_pre_empty_detections = """\
          DELETE FROM detections
        """
        #query_start = time.time()
        cursor.execute(sql_pre_empty_detections)
        #query_time = time.time() - query_start
        #print "\tQuery", query, ":", str(round(query_time*1000,2)), "ms"
        conn.commit()
        
        # TODO: COPY INTO is faster. 
        query = "sql_insert_detections"
        sql_insert_detections = "INSERT INTO detections VALUES "
        i = 0
        if len(results) > 0:
            for det in results:
                if i < len(results) - 1:
                    sql_insert_detections += str(det.serialize()) + ","
                else:
                    sql_insert_detections += str(det.serialize())
                i += 1
            #print "sql_insert_detections =", sql_insert_detections
            #query_start = time.time()
            cursor.execute(sql_insert_detections)
            #query_time = time.time() - query_start
            #print "\tQuery", query, ":", str(round(query_time*1000,2)), "ms"
            conn.commit()
        
        query = "insertExtractedSources"
        sql_insert_extractedsources = """\
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
                  ,COS(RADIANS(ldecl)) * COS(RADIANS(lra)) 
                  ,COS(RADIANS(ldecl)) * SIN(RADIANS(lra)) 
                  ,SIN(RADIANS(ldecl)) 
                  ,ldet_sigma 
                  ,lI_peak 
                  ,lI_peak_err 
                  ,lI_int 
                  ,lI_int_err 
              FROM detections
        """
        #query_start = time.time()
        cursor.execute(sql_insert_extractedsources, (image_id,))
        #query_time = time.time() - query_start
        #print "\tQuery", query, ":", str(round(query_time*1000,2)), "ms"
        conn.commit()

        query = "sql_post_empty_detections"
        sql_post_empty_detections = """\
          DELETE FROM detections
        """
        #query_start = time.time()
        cursor.execute(sql_post_empty_detections)
        #query_time = time.time() - query_start
        #print "\tQuery", query, ":", str(round(query_time*1000,2)), "ms"
        conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()


def associateExtractedSources(conn, image_id, deRuiter_r=DERUITER_R):
    """Association of extracted sources with sources detected before
    (those in running catalog).
    
    The dimensionless distance between two sources is given by the 
    "De Ruiter radius", see Ch2&3 of thesis Scheers.
    
    Here we use a default value of deRuiter_r = 3.717/3600. for a
    reliable association.
    
    """
    try:
        cursor = conn.cursor()
        
        query = "sql_pre_empty_tempruncat"
        sql_pre_empty_tempruncat = """\
          DELETE FROM temprunningcatalog
        """
        #query_start = time.time()
        cursor.execute(sql_pre_empty_tempruncat)
        #query_time = time.time() - query_start
        #print "\tQuery", query, ":", str(round(query_time*1000,2)), "ms"
        conn.commit()
        
        """
        Here we select the extractedsources that have a positional match with the 
        sources in the running catalogue (runningcatalog) and those who have
        will be inserted into the temp_running catalogue table.
        """
        query = "sql_insert_tempruncat"
        sql_insert_tempruncat = """\
        INSERT INTO temprunningcatalog
          (xtrsrc_id 
          ,assoc_xtrsrc_id
          ,ds_id
          ,zone
          ,ra_avg 
          ,decl_avg 
          ,ra_err_avg 
          ,decl_err_avg 
          ,x
          ,y
          ,z
          ,datapoints 
          ,avg_weighted_ra
          ,avg_weighted_decl
          ,avg_ra_weight
          ,avg_decl_weight
          ,I_peak_sum 
          ,I_peak_sq_sum 
          ,weight_peak_sum 
          ,weight_I_peak_sum 
          ,weight_I_peak_sq_sum 

          ) 
          SELECT t0.xtrsrc_id
                ,t0.assoc_xtrsrc_id
                ,t0.ds_id
                ,CAST(FLOOR(t0.decl_avg/1) AS INTEGER) 
                ,t0.ra_avg
                ,t0.decl_avg
                ,t0.ra_err_avg
                ,t0.decl_err_avg
                ,COS(RADIANS(t0.decl_avg)) * COS(RADIANS(t0.ra_avg))
                ,COS(RADIANS(t0.decl_avg)) * SIN(RADIANS(t0.ra_avg))
                ,SIN(RADIANS(t0.decl_avg)) 
                ,t0.datapoints
                ,t0.avg_weighted_ra
                ,t0.avg_weighted_decl
                ,t0.avg_ra_weight
                ,t0.avg_decl_weight
                ,t0.I_peak_sum 
                ,t0.I_peak_sq_sum 
                ,t0.weight_peak_sum 
                ,t0.weight_I_peak_sum 
                ,t0.weight_I_peak_sq_sum 
            FROM (SELECT b0.xtrsrc_id
                        ,x0.xtrsrcid as assoc_xtrsrc_id
                        ,im0.ds_id
                        ,(datapoints * b0.avg_weighted_ra + x0.ra / (x0.ra_err * x0.ra_err)) 
                         / (datapoints * b0.avg_ra_weight + 1 / (x0.ra_err * x0.ra_err) ) as ra_avg 
                        ,(datapoints * b0.avg_weighted_decl + x0.decl / (x0.decl_err * x0.decl_err)) 
                         / (datapoints * b0.avg_decl_weight + 1 / (x0.decl_err * x0.decl_err) ) as decl_avg 
                        ,sqrt(1 / ((datapoints * b0.avg_ra_weight + 1 / (x0.ra_err * x0.ra_err)))) as ra_err_avg
                        ,sqrt(1 / ((datapoints * b0.avg_decl_weight + 1 / (x0.decl_err * x0.decl_err)))) as decl_err_avg
                        ,b0.datapoints + 1 as datapoints 
                        ,(datapoints * b0.avg_weighted_ra + x0.ra / (x0.ra_err * x0.ra_err))
                         / (datapoints + 1) as avg_weighted_ra
                        ,(datapoints * b0.avg_weighted_decl + x0.decl / (x0.decl_err * x0.decl_err))
                         / (datapoints + 1) as avg_weighted_decl
                        ,(datapoints * b0.avg_ra_weight + 1 / (x0.ra_err * x0.ra_err))
                         / (datapoints + 1) as avg_ra_weight
                        ,(datapoints * b0.avg_decl_weight + 1 / (x0.decl_err * x0.decl_err))
                         / (datapoints + 1) as avg_decl_weight
                        ,(datapoints * b0.I_peak_sum + x0.I_peak) as i_peak_sum
                        ,b0.I_peak_sq_sum + x0.I_peak * x0.I_peak as i_peak_sq_sum 
                        ,b0.weight_peak_sum + 1 / (x0.I_peak_err * x0.I_peak_err) as weight_peak_sum 
                        ,b0.weight_I_peak_sum  + x0.I_peak / (x0.I_peak_err * x0.I_peak_err) as weight_i_peak_sum 
                        ,b0.weight_I_peak_sq_sum + x0.I_peak * x0.I_peak / (x0.I_peak_err * x0.I_peak_err) as weight_i_peak_sq_sum 
                    FROM runningcatalog b0 
                        ,extractedsources x0 
                        ,images im0 
                   WHERE x0.image_id = %s
                     AND x0.image_id = im0.imageid
                     AND im0.ds_id = b0.ds_id
                     AND b0.zone BETWEEN CAST(FLOOR(x0.decl - 0.025) as INTEGER) 
                                     AND CAST(FLOOR(x0.decl + 0.025) as INTEGER) 
                     AND b0.decl_avg BETWEEN x0.decl - 0.025 
                                         AND x0.decl + 0.025 
                     AND b0.ra_avg BETWEEN x0.ra - alpha(0.025,x0.decl) 
                                       AND x0.ra + alpha(0.025,x0.decl) 
                     AND SQRT((x0.ra - b0.ra_avg) * COS(RADIANS(x0.decl)) 
                              * (x0.ra - b0.ra_avg) * COS(RADIANS(x0.decl))
                              /(x0.ra_err * x0.ra_err + b0.ra_err_avg * b0.ra_err_avg)
                             +(x0.decl - b0.decl_avg) * (x0.decl - b0.decl_avg)
                              /(x0.decl_err * x0.decl_err + b0.decl_err_avg * b0.decl_err_avg)
                             ) < %s 
                 ) t0
        """
        # This result set might contain multiple associations (1-n,n-1)
        # for a single known source in runningcatalog.
        # The n-1 assocs will be treated similar as the 1-1 assocs.
        #query_start = time.time()
        cursor.execute(sql_insert_tempruncat, (image_id, deRuiter_r))
        #query_time = time.time() - query_start
        #print "\tQuery", query, ":", str(round(query_time*1000,2)), "ms"
        conn.commit()
           
        #: Before we continue, we first take care of the sources 
        #: that have multiple associations in both directions.
        #: 
        #: -1- running-catalogue sources  <- extracted source
        #: An extracted source has multiple counterparts in the
        #: running catalogue.
        #: We only keep the ones with the lowest deRuiter_r value,
        #: the rest we throw away.
        #:
        #: NOTE :
        #: It is worth considering whether this might be changed to
        #: selecting the brightest neighbour source, instead of
        #: just the closest neighbour.
        #: (There are case [when flux_lim > 10Jy] that the nearest source
        #:  has a lower flux level, causing unexpected spectral indices)
        query = "sql_select_closest_runcat_assoc"
        sql_select_closest_runcat_assoc = """\
        SELECT t1.xtrsrc_id
              ,t1.assoc_xtrsrc_id
          FROM (SELECT tb0.assoc_xtrsrc_id
                      ,MIN(SQRT((x0.ra - b0.ra_avg) * COS(RADIANS(x0.decl))  
                      * (x0.ra - b0.ra_avg) * COS(RADIANS(x0.decl))
                      /(x0.ra_err * x0.ra_err + b0.ra_err_avg * b0.ra_err_avg)
                      +(x0.decl - b0.decl_avg) * (x0.decl - b0.decl_avg)
                      /(x0.decl_err * x0.decl_err + b0.decl_err_avg * b0.decl_err_avg)
                      )) as min_r1     
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
                      ,SQRT((x1.ra - b1.ra_avg) * COS(RADIANS(x1.decl)) 
                        * (x1.ra - b1.ra_avg) * COS(RADIANS(x1.decl))
                        /(x1.ra_err * x1.ra_err + b1.ra_err_avg * b1.ra_err_avg)
                        +(x1.decl - b1.decl_avg) * (x1.decl - b1.decl_avg) 
                        /(x1.decl_err * x1.decl_err + b1.decl_err_avg * b1.decl_err_avg)
                        ) as r1 
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
        #query_start = time.time()
        cursor.execute(sql_select_closest_runcat_assoc)
        #query_time = time.time() - query_start
        #print "\tQuery", query, ":", str(round(query_time*1000,2)), "ms"
        results = zip(*cursor.fetchall())
        if len(results) != 0:
            xtrsrc_id = results[0]
            assoc_xtrsrc_id = results[1]
            query = "sql_delete_nonclosest_runcat_assocs"
            # TODO: Consider setting row to inactive instead of deleting
            sql_delete_nonclosest_runcat_assocs = """\
            DELETE
              FROM temprunningcatalog
             WHERE xtrsrc_id = %s
               AND assoc_xtrsrc_id = %s
            """
            #query_start = time.time()
            for j in range(len(xtrsrc_id)):
                cursor.execute(sql_delete_nonclosest_runcat_assocs, (xtrsrc_id[j],assoc_xtrsrc_id[j]))
            #query_time = time.time() - query_start
            #print "\tQuery", query, ":", str(round(query_time*1000,2)), "ms"
            conn.commit()
        
        """
        -2- Now, we take care of the sources in the running catalogue 
        that have more than one counterpart among the extracted sources.
        We now make two entries in the running catalogue, in stead of the one we
        had before. Therefore, we 'swap' the ids.
        """
        query = "sql_select_mult_assocs"
        sql_select_mult_assocs = """\
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
        #query_start = time.time()
        cursor.execute(sql_select_mult_assocs)
        #query_time = time.time() - query_start
        #print "\tQuery", query, ":", str(round(query_time*1000,2)), "ms"
        conn.commit()
        
        """
        -3- And, we have to insert identical ids to identify a
        light-curve starting point.
        """
        query = "sql_insert_mult_assocs"
        sql_insert_mult_assocs = """\
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
        #query_start = time.time()
        cursor.execute(sql_insert_mult_assocs)
        #query_time = time.time() - query_start
        #print "\tQuery", query, ":", str(round(query_time*1000,2)), "ms"
        conn.commit()
        
        """
        -4- And, we throw away the swapped id
        Maybe TODO, It might be better to flag this record...
        """
        # TODO: Consider setting rows to inactive instead of deleting
        query = "sql_delete_mult_assocs"
        sql_delete_mult_assocs = """\
        DELETE 
          FROM assocxtrsources
         WHERE xtrsrc_id IN (SELECT xtrsrc_id 
                               FROM temprunningcatalog
                             GROUP BY xtrsrc_id 
                             HAVING COUNT(*) > 1
                            )
        """
        #query_start = time.time()
        cursor.execute(sql_delete_mult_assocs)
        #query_time = time.time() - query_start
        #print "\tQuery", query, ": ", str(round(query_time*1000,2)), "ms"
        conn.commit()
        
        """
        Here we insert new ids of the sources in the running catalogue
        """
        query = "sql_insert_mult_assocs_runcat"
        sql_insert_mult_assocs_runcat = """\
        INSERT INTO runningcatalog
          (xtrsrc_id 
          ,ds_id
          ,zone 
          ,ra_avg 
          ,decl_avg 
          ,ra_err_avg 
          ,decl_err_avg 
          ,x 
          ,y 
          ,z 
          ,datapoints 
          ,avg_weighted_ra
          ,avg_weighted_decl
          ,avg_ra_weight
          ,avg_decl_weight
          ,I_peak_sum 
          ,I_peak_sq_sum 
          ,weight_peak_sum 
          ,weight_I_peak_sum 
          ,weight_I_peak_sq_sum 
          ) 
          SELECT assoc_xtrsrc_id 
                ,ds_id
                ,zone
                ,ra_avg 
                ,decl_avg 
                ,ra_err_avg 
                ,decl_err_avg 
                ,x
                ,y
                ,z
                ,datapoints 
                ,avg_weighted_ra
                ,avg_weighted_decl
                ,avg_ra_weight
                ,avg_decl_weight
                ,I_peak_sum 
                ,I_peak_sq_sum 
                ,weight_peak_sum 
                ,weight_I_peak_sum 
                ,weight_I_peak_sq_sum 
            FROM temprunningcatalog
           WHERE xtrsrc_id IN (SELECT xtrsrc_id 
                                 FROM temprunningcatalog
                               GROUP BY xtrsrc_id 
                               HAVING COUNT(*) > 1
                              )
        """
        #query_start = time.time()
        cursor.execute(sql_insert_mult_assocs_runcat)
        #query_time = time.time() - query_start
        #print "\tQuery", query, ":", str(round(query_time*1000,2)), "ms"
        conn.commit()
        
        query = "sql_delete_mult_assocs_runcat"
        # TODO: Consider setting row to inactive instead of deleting
        sql_delete_mult_assocs_runcat = """\
        DELETE 
          FROM runningcatalog
         WHERE xtrsrc_id IN (SELECT xtrsrc_id 
                               FROM temprunningcatalog
                             GROUP BY xtrsrc_id 
                             HAVING COUNT(*) > 1
                            )
        """
        #query_start = time.time()
        cursor.execute(sql_delete_mult_assocs_runcat)
        #query_time = time.time() - query_start
        #print "\tQuery", query, ":", str(round(query_time*1000,2)), "ms"
        conn.commit()
        
        query = "sql_delete_mult_assocs_tempruncat"
        # TODO: Consider setting row to inactive instead of deleting
        sql_delete_mult_assocs_tempruncat = """\
        DELETE 
          FROM tempmultcatbasesources 
         WHERE xtrsrc_id IN (SELECT xtrsrc_id 
                               FROM tempmultcatbasesources 
                             GROUP BY xtrsrc_id 
                             HAVING COUNT(*) > 1
                            )
        """
        # The resulting content of tempmultcatbasesources
        # will be the 1-1 and n-1 assocs.
        #query_start = time.time()
        cursor.execute(sql_delete_mult_assocs_tempruncat)
        #query_time = time.time() - query_start
        #print "\tQuery", query, ":", str(round(query_time*1000,2)), "ms"
        conn.commit()
        
        #+-----------------------------------------------------+
        #| After all this, we are now left with the 1-1 assocs |
        #+-----------------------------------------------------+

        query = "sql_insert_assocs"
        sql_insert_assocs = """\
        INSERT INTO assocxtrsources
          (xtrsrc_id
          ,assoc_xtrsrc_id
          )
          SELECT xtrsrc_id
                ,assoc_xtrsrc_id 
            FROM temprunningcatalog
        """
        #query_start = time.time()
        cursor.execute(sql_insert_assocs)
        #query_time = time.time() - query_start
        #print "\tQuery", query, ":", str(round(query_time*1000,2)), "ms"
        conn.commit()
        
        """
        Since Jun2010 version we cannot use the massive update statement anymore.
        Therefore, unfortunately, we cursor through the tempsources table
        """
        query = "sql_select_assocs"
        sql_select_assocs = """\
        SELECT zone
              ,ra_avg
              ,decl_avg
              ,ra_err_avg
              ,decl_err_avg
              ,x
              ,y
              ,z
              ,datapoints
              ,avg_weighted_ra
              ,avg_weighted_decl
              ,avg_ra_weight
              ,avg_decl_weight
              ,I_peak_sum 
              ,I_peak_sq_sum 
              ,weight_peak_sum 
              ,weight_I_peak_sum 
              ,weight_I_peak_sq_sum 
              ,xtrsrc_id
          FROM temprunningcatalog
        """
        #query_start = time.time()
        cursor.execute(sql_select_assocs)
        #query_time = time.time() - query_start
        #print "\tQuery", query, ":", str(round(query_time*1000,2)), "ms"
        y = cursor.fetchall()
        #print "\t\tlen(y) = ", len(y)
        
        query = "sql_update_assocs"
        sql_update_assocs = """\
        UPDATE runningcatalog
          SET zone = %s
             ,ra_avg = %s
             ,decl_avg = %s
             ,ra_err_avg = %s
             ,decl_err_avg = %s
             ,x = %s
             ,y = %s
             ,z = %s
             ,datapoints = %s
             ,avg_weighted_ra = %s
             ,avg_weighted_decl = %s
             ,avg_ra_weight = %s
             ,avg_decl_weight = %s
             ,I_peak_sum = %s
             ,I_peak_sq_sum = %s
             ,weight_peak_sum = %s
             ,weight_I_peak_sum = %s
             ,weight_I_peak_sq_sum = %s
        WHERE xtrsrc_id = %s
        """
        #query_start = time.time()
        for k in range(len(y)):
            #print y[k][0], y[k][1], y[k][2]
            cursor.execute(sql_update_assocs, (y[k][0] \
                                            ,y[k][1] \
                                            ,y[k][2] \
                                            ,y[k][3] \
                                            ,y[k][4] \
                                            ,y[k][5] \
                                            ,y[k][6] \
                                            ,y[k][7] \
                                            ,y[k][8] \
                                            ,y[k][9] \
                                            ,y[k][10] \
                                            ,y[k][11] \
                                            ,y[k][12] \
                                            ,y[k][13] \
                                            ,y[k][14] \
                                            ,y[k][15] \
                                            ,y[k][16] \
                                            ,y[k][17] \
                                            ,y[k][18] \
                                            ))
            if (k % 100 == 0):
                print "\t\tQuery", query, "; iter", k
        #query_time = time.time() - query_start
        #print "\tQuery", query, ":", str(round(query_time*1000,2)), "ms"
        conn.commit()
        
        """
        #if catids[i] != 4:
        query = 10
        sql_update_known_sources = ""\
          UPDATE multcatbasesources 
            SET zone = (SELECT zone
                          FROM tempmultcatbasesources 
                         WHERE tempmultcatbasesources.xtrsrc_id = multcatbasesources.xtrsrc_id
                       ) 
               ,ra_avg = (SELECT ra_avg 
                            FROM tempmultcatbasesources 
                           WHERE tempmultcatbasesources.xtrsrc_id = multcatbasesources.xtrsrc_id 
                         ) 
               ,decl_avg = (SELECT decl_avg 
                              FROM tempmultcatbasesources 
                             WHERE tempmultcatbasesources.xtrsrc_id = multcatbasesources.xtrsrc_id 
                           ) 
               ,ra_err_avg = (SELECT ra_err_avg 
                                FROM tempmultcatbasesources 
                               WHERE tempmultcatbasesources.xtrsrc_id = multcatbasesources.xtrsrc_id 
                             ) 
               ,decl_err_avg = (SELECT decl_err_avg 
                                  FROM tempmultcatbasesources 
                                 WHERE tempmultcatbasesources.xtrsrc_id = multcatbasesources.xtrsrc_id 
                               ) 
               ,x = (SELECT x 
                       FROM tempmultcatbasesources 
                      WHERE tempmultcatbasesources.xtrsrc_id = multcatbasesources.xtrsrc_id 
                    ) 
               ,y = (SELECT y
                       FROM tempmultcatbasesources 
                      WHERE tempmultcatbasesources.xtrsrc_id = multcatbasesources.xtrsrc_id 
                    ) 
               ,z = (SELECT z 
                       FROM tempmultcatbasesources 
                      WHERE tempmultcatbasesources.xtrsrc_id = multcatbasesources.xtrsrc_id 
                    ) 
               ,datapoints = (SELECT datapoints 
                                FROM tempmultcatbasesources 
                               WHERE tempmultcatbasesources.xtrsrc_id = multcatbasesources.xtrsrc_id 
                             ) 
               ,avg_weighted_ra = (SELECT avg_weighted_ra
                                     FROM tempmultcatbasesources 
                                    WHERE tempmultcatbasesources.xtrsrc_id = multcatbasesources.xtrsrc_id 
                                  ) 
               ,avg_weighted_decl = (SELECT avg_weighted_decl
                                       FROM tempmultcatbasesources 
                                      WHERE tempmultcatbasesources.xtrsrc_id = multcatbasesources.xtrsrc_id 
                                    ) 
               ,avg_ra_weight = (SELECT avg_ra_weight
                                   FROM tempmultcatbasesources 
                                  WHERE tempmultcatbasesources.xtrsrc_id = multcatbasesources.xtrsrc_id 
                                ) 
               ,avg_decl_weight = (SELECT avg_decl_weight
                                     FROM tempmultcatbasesources 
                                    WHERE tempmultcatbasesources.xtrsrc_id = multcatbasesources.xtrsrc_id 
                                  ) 
          WHERE EXISTS (SELECT xtrsrc_id 
                          FROM tempmultcatbasesources 
                         WHERE tempmultcatbasesources.xtrsrc_id = multcatbasesources.xtrsrc_id 
                       )
        """
        
        query = "sql_delete_tempassocs"
        sql_delete_tempassocs = """\
          DELETE FROM temprunningcatalog
        """
        #query_start = time.time()
        cursor.execute(sql_delete_tempassocs)
        #query_time = time.time() - query_start
        #print "\tQuery", query, ": ", str(round(query_time*1000,2)), "ms"
        conn.commit()

        query = "sql_count_assocs"
        sql_count_assocs = """\
        SELECT COUNT(*)
          FROM extractedsources x0 
              ,images im0
              ,runningcatalog b0 
         WHERE x0.image_id = %s
           AND x0.image_id = im0.imageid
           AND im0.ds_id = b0.ds_id
           AND b0.zone BETWEEN x0.zone - cast(0.025 as integer) 
                           AND x0.zone + cast(0.025 as integer) 
           AND b0.decl_avg BETWEEN x0.decl - 0.025 
                               AND x0.decl + 0.025 
           AND b0.ra_avg BETWEEN x0.ra - alpha(0.025,x0.decl) 
                             AND x0.ra + alpha(0.025,x0.decl) 
           AND SQRT((x0.ra - b0.ra_avg) * COS(RADIANS(x0.decl)) 
                    * (x0.ra - b0.ra_avg) * COS(RADIANS(x0.decl))
                    /(x0.ra_err * x0.ra_err + b0.ra_err_avg * b0.ra_err_avg)
                   +(x0.decl - b0.decl_avg) * (x0.decl - b0.decl_avg)
                    /(x0.decl_err * x0.decl_err + b0.decl_err_avg * b0.decl_err_avg)
                   ) < %s 
        """
        #query_start = time.time()
        cursor.execute(sql_count_assocs, (image_id,deRuiter_r))
        #query_time = time.time() - query_start
        #print "\tQuery", query, ": ", str(round(query_time*1000,2)), "ms"
        y=cursor.fetchall()
        #print "\t\tNumber of known sources (or sources in NOT IN): ", y[0][0]
        conn.commit()
        
        query = "sql_insert_new_assocs"
        sql_insert_new_assocs = """\
        INSERT INTO assocxtrsources 
          (xtrsrc_id 
          ,assoc_xtrsrc_id
          ) 
          SELECT x1.xtrsrcid as xtrsrc_id
                ,x1.xtrsrcid as assoc_xtrsrc_id
            FROM extractedsources x1 
           WHERE x1.image_id = %s
             AND x1.xtrsrcid NOT IN (SELECT x0.xtrsrcid 
                                       FROM extractedsources x0 
                                           ,runningcatalog b0 
                                           ,images im0
                                      WHERE x0.image_id = %s
                                        AND x0.image_id = im0.imageid
                                        AND im0.ds_id = b0.ds_id
                                        AND b0.zone BETWEEN x0.zone - cast(0.025 as integer) 
                                                        AND x0.zone + cast(0.025 as integer) 
                                        AND b0.decl_avg BETWEEN x0.decl - 0.025 
                                                            AND x0.decl + 0.025 
                                        AND b0.ra_avg BETWEEN x0.ra - alpha(0.025,x0.decl) 
                                                          AND x0.ra + alpha(0.025,x0.decl) 
                                        AND SQRT((x0.ra - b0.ra_avg) * COS(RADIANS(x0.decl)) 
                                                 * (x0.ra - b0.ra_avg) * COS(RADIANS(x0.decl))
                                                 /(x0.ra_err * x0.ra_err 
                                                  + b0.ra_err_avg * b0.ra_err_avg
                                                  )
                                                +(x0.decl - b0.decl_avg) * (x0.decl - b0.decl_avg)
                                                 /(x0.decl_err * x0.decl_err 
                                                  + b0.decl_err_avg * b0.decl_err_avg
                                                  )
                                                ) < %s 
                                    )
        """
        #query_start = time.time()
        cursor.execute(sql_insert_new_assocs, (image_id,image_id,deRuiter_r))
        #query_time = time.time() - query_start
        #print "\tQuery", query, ": ", str(round(query_time*1000,2)), "ms"
        conn.commit()
        
        query = "sql_insert_new_assocs_runcat"
        sql_insert_new_assocs_runcat = """\
        INSERT INTO runningcatalog
          (xtrsrc_id 
          ,ds_id
          ,zone 
          ,ra_avg 
          ,decl_avg 
          ,ra_err_avg 
          ,decl_err_avg 
          ,x 
          ,y 
          ,z 
          ,datapoints 
          ,avg_weighted_ra
          ,avg_weighted_decl
          ,avg_ra_weight
          ,avg_decl_weight
          ,I_peak_sum 
          ,I_peak_sq_sum 
          ,weight_peak_sum 
          ,weight_I_peak_sum 
          ,weight_I_peak_sq_sum 
          ) 
          SELECT x1.xtrsrcid 
                ,im1.ds_id
                ,x1.zone 
                ,x1.ra 
                ,x1.decl 
                ,x1.ra_err 
                ,x1.decl_err 
                ,x1.x 
                ,x1.y 
                ,x1.z 
                ,1 
                ,x1.ra / (x1.ra_err * x1.ra_err)
                ,x1.decl / (x1.decl_err * x1.decl_err)
                ,1 / (x1.ra_err * x1.ra_err)
                ,1 / (x1.decl_err * x1.decl_err)
                ,I_peak
                ,I_peak * I_peak 
                ,1 / (I_peak_err * I_peak_err)
                ,I_peak / (I_peak_err * I_peak_err)
                ,I_peak * I_peak / (I_peak_err * I_peak_err)
            FROM extractedsources x1 
                ,images im1
           WHERE x1.image_id = %s
             AND x1.image_id = im1.imageid
             AND x1.xtrsrcid NOT IN (SELECT x0.xtrsrcid 
                                       FROM extractedsources x0 
                                           ,runningcatalog b0 
                                           ,images im0
                                      WHERE x0.image_id = %s
                                        AND x0.image_id = im0.imageid
                                        AND im0.ds_id = b0.ds_id
                                        AND b0.zone BETWEEN x0.zone - cast(0.025 as integer) 
                                                        AND x0.zone + cast(0.025 as integer) 
                                        AND b0.decl_avg BETWEEN x0.decl - 0.025 
                                                            AND x0.decl + 0.025 
                                        AND b0.ra_avg BETWEEN x0.ra - alpha(0.025,x0.decl) 
                                                          AND x0.ra + alpha(0.025,x0.decl) 
                                        AND b0.x * x0.x + b0.y * x0.y + b0.z * x0.z > COS(RADIANS(0.025))
                                        AND SQRT((x0.ra - b0.ra_avg) * COS(RADIANS(x0.decl)) 
                                                 * (x0.ra - b0.ra_avg) * COS(RADIANS(x0.decl))
                                                 /(x0.ra_err * x0.ra_err 
                                                  + b0.ra_err_avg * b0.ra_err_avg
                                                  )
                                                +(x0.decl - b0.decl_avg) * (x0.decl - b0.decl_avg)
                                                 /(x0.decl_err * x0.decl_err 
                                                  + b0.decl_err_avg * b0.decl_err_avg
                                                  )
                                                ) < %s 
                                    )
        """
        #query_start = time.time()
        cursor.execute(sql_insert_new_assocs_runcat, (image_id,image_id,deRuiter_r))
        #query_time = time.time() - query_start
        #print "\tQuery", query, ": ", str(round(query_time*1000,2)), "ms"
        conn.commit()
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()
