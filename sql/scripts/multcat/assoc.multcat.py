import os, errno, time, sys
from datetime import datetime
import monetdb.sql as db
from monetdb.sql import Error as Error
#import MySQLdb as db
#from MySQLdb import Error as Error
import logging

host = sys.argv[1] # number of sources per image
#ns = int(sys.argv[2]) # number of sources per image
#iter = int(sys.argv[3]) # number of images to process
loadlsm = sys.argv[2] # Y/N to load lsm

db_type = "MonetDB"
db_host = host
db_port = 50000
db_dbase = "multcat"
db_user = "multcat" 
db_passwd = "ch4"

monetdbtkphome = os.getenv('MONETDBTKPHOME') 
#monetdbtkphome = '/scratch/bscheers'
path = monetdbtkphome + '/scripts/multcat'

#f = '/copy.into.extractedsources.' + str(ns) + '.csv'
#infile = path + f

logtime = time.strftime("%Y%m%d-%H%M")
lf = '/logs/multcat.assoc.' + host + '.log'
logfile = path + lf
logf = open(logfile, 'w')
row = 'csv log file of processing times of the multi-catalog association. \n'
logf.write(row)
row = '+========================================================================================+\n'
logf.write(row)
row = '| iter | imageid | query5_time | query8_time | query9_time | query10_time | query12_time |\n'
logf.write(row)
row = '+========================================================================================+\n'
logf.write(row)

conn = db.connect(hostname=db_host,database=db_dbase,username=db_user,password=db_passwd)
#conn = db.connect(host=db_host,db=db_dbase,user=db_user,passwd=db_passwd, unix_socket="/scratch/bscheers/databases/mysql/var/mysql.sock")

try:
    iter_start = time.time()
    cursor = conn.cursor()
    
    if loadlsm == 'Y':
        query = 0
        sql_load_lsm = """\
          CALL LoadLSM(0,360,30,90,'NVSS','VLSS','WENSS')
        """
        #sql_load_lsm = """\
        #  CALL LoadLSM(90,120,30,60,'NVSS','VLSS','WENSS')
        #  CALL LoadLSM(95,100,40,45,'NVSS','VLSS','WENSS')
        #"""
        query_start = time.time()
        cursor.execute(sql_load_lsm)
        query0_time = time.time() - query_start
        conn.commit()
        print "LSM Loaded"
    else:
        print "LSM NOT Loaded"
    
    query = 1
    sql_insert_dataset = """\
      SELECT insertDataset('Multi-Catalog Association')
    """
    query_start = time.time()
    cursor.execute(sql_insert_dataset)
    query1_time = time.time() - query_start
    dsid = cursor.fetchone()[0]
    conn.commit()
    print "dsid = ", dsid
    
    #catids = [3,4,5] #[NVSS,VLSS,WENSS]
    catids = [3,5,4] #[NVSS,WENSS,VLSS]
    for i in range(len(catids)):
        for z in range(30,91):
            print "Processing sources from catids[", i, "] = ", catids[i]
            obstime = datetime.now()
            params = [dsid \
                     ,42000000. \
                     ,4000000. \
                     ,obstime.strftime("%Y-%m-%d-%H:%M:%S") + '.' + str(obstime.microsecond) \
                     ,'sources from catid: ' + str(catids[i]) + ': zone = ' + str(z)
                     ]
            query = 2
            #cursor.execute("SELECT insertImage(%s,%s,%s,%s,%s)", params)
            sql_insert_image = """\
              INSERT INTO images 
                (ds_id 
                ,tau 
                ,band 
                ,tau_time 
                ,freq_eff 
                ,freq_bw
                ,taustart_ts 
                ,url 
                )  
              VALUES 
                (%s 
                ,1 
                ,4 
                ,3600 
                ,%s 
                ,%s 
                ,%s 
                ,%s 
                ) 
            """
            query_start = time.time()
            cursor.execute(sql_insert_image, (params[0],params[1],params[2],params[3],params[4]))
            query2_time = time.time() - query_start
            print "\tQuery ", query, ": ", str(round(query2_time*1000,2)), "ms"
            imgid = int(cursor.lastrowid)
            conn.commit()
            #print "imgid = ", imgid
            
            """
            query = 3
            query_start = time.time()
            cursor.execute("DELETE FROM loadxtrsources")
            query3_time = time.time() - query_start
            conn.commit()
            
            query = 4
            query_start = time.time()
            cursor.execute("COPY %s RECORDS " + \
                           "INTO loadxtrsources " + \
                           "FROM %s " + \
                           "USING DELIMITERS ',' " + \
                           "                ,'\n' " + \
                           "NULL AS '' ", (ns, infile))
            query4_time = time.time() - query_start
            #conn.commit()
            """

            query = 5
            sql_insert_extractedsources = """\
              INSERT INTO extractedsources 
                (xtrsrcid
                ,image_id  
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
                ,id
                ) 
                SELECT lsmid
                      ,%s
                      ,zone
                      ,ra 
                      ,decl 
                      ,ra_err 
                      ,decl_err 
                      ,COS(RADIANS(decl)) * COS(RADIANS(ra)) 
                      ,COS(RADIANS(decl)) * SIN(RADIANS(ra)) 
                      ,SIN(RADIANS(decl)) 
                      ,det_sigma 
                      ,I_peak_avg 
                      ,I_peak_avg_err 
                      ,I_int_avg 
                      ,I_int_avg_err 
                      ,orig_catsrcid
                  FROM lsm 
                 WHERE cat_id = %s 
                   AND zone = %s 
            """
            query_start = time.time()
            cursor.execute(sql_insert_extractedsources, (imgid,catids[i],z))
            query5_time = time.time() - query_start
            print "\tQuery ", query, ": ", str(round(query5_time*1000,2)), "ms"
            conn.commit()
            
            """
            query = 6
            query_start = time.time()
            cursor.execute("DELETE FROM loadxtrsources")
            query6_time = time.time() - query_start
            conn.commit()
            """
            
            query = 7
            query_start = time.time()
            cursor.execute("DELETE FROM tempmultcatbasesources")
            query7_time = time.time() - query_start
            print "\tQuery ", query, ": ", str(round(query7_time*1000,2)), "ms"
            conn.commit()
            
            query = 8
            sql_prep_update_known_sources = """\
              INSERT INTO tempmultcatbasesources 
                (xtrsrc_id 
                ,assoc_xtrsrc_id
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
                ) 
                SELECT t0.xtrsrc_id
                      ,t0.assoc_xtrsrc_id
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
                  FROM (SELECT b0.xtrsrc_id
                              ,x0.xtrsrcid as assoc_xtrsrc_id
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
                          FROM multcatbasesources b0 
                              ,extractedsources x0 
                         WHERE x0.image_id = %s
                           AND b0.zone BETWEEN x0.zone - cast(0.025 as integer) 
                                           AND x0.zone + cast(0.025 as integer) 
                           AND b0.decl_avg BETWEEN x0.decl - 0.025 
                                               AND x0.decl + 0.025 
                           AND b0.ra_avg BETWEEN x0.ra - alpha(0.025,x0.decl) 
                                             AND x0.ra + alpha(0.025,x0.decl) 
                           AND ASIN(SQRT((x0.x - b0.x)*(x0.x - b0.x) 
                                        +(x0.y - b0.y)*(x0.y - b0.y) 
                                        +(x0.z - b0.z)*(x0.z - b0.z) 
                                        ) / 2 
                                   ) 
                               / 
                               SQRT(x0.ra_err * x0.ra_err + b0.ra_err_avg * b0.ra_err_avg 
                                   +x0.decl_err * x0.decl_err + b0.decl_err_avg * b0.decl_err_avg) 
                               < 7.272E-6
                       ) t0
            """
            # This result set might contain multiple associations (1-n,n-1)
            # for a single known source in multcatbasesources.
            # The n-1 assocs will treated similar as the 1-1 assocs.
            query_start = time.time()
            cursor.execute(sql_prep_update_known_sources, (imgid,))
            query8_time = time.time() - query_start
            print "\tQuery ", query, ": ", str(round(query8_time*1000,2)), "ms"
            conn.commit()
           
            # Now we first take care of the multiple associations (1-n) 
            # before we continue
            #if catids[i] != 4:
            query = 81
            sql_filter_multiple_assocs = """\
              INSERT INTO assoccatsources
                (xtrsrc_id
                ,assoc_catsrc_id
                )
                SELECT assoc_xtrsrc_id
                      ,xtrsrc_id
                  FROM tempmultcatbasesources 
                 WHERE xtrsrc_id IN (SELECT xtrsrc_id 
                                       FROM tempmultcatbasesources 
                                     GROUP BY xtrsrc_id 
                                     HAVING COUNT(*) > 1
                                    )
            """
            # Inserting the multiple sources into assoc
            query_start = time.time()
            cursor.execute(sql_filter_multiple_assocs)
            query81_time = time.time() - query_start
            print "\tQuery ", query, ": ", str(round(query81_time*1000,2)), "ms"
            conn.commit()
            
            #if catids[i] != 4:
            query = 82
            sql_delete_multiple_assocs = """\
              DELETE 
                FROM assoccatsources
               WHERE xtrsrc_id IN (SELECT xtrsrc_id 
                                     FROM tempmultcatbasesources 
                                   GROUP BY xtrsrc_id 
                                   HAVING COUNT(*) > 1
                                  )
            """
            query_start = time.time()
            cursor.execute(sql_delete_multiple_assocs)
            query82_time = time.time() - query_start
            print "\tQuery ", query, ": ", str(round(query82_time*1000,2)), "ms"
            conn.commit()
            
            #if catids[i] != 4:
            query = 83
            sql_replace_single_known_source_by_multiple = """\
              INSERT INTO multcatbasesources 
                (xtrsrc_id 
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
                ) 
                SELECT assoc_xtrsrc_id 
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
                  FROM tempmultcatbasesources
                 WHERE xtrsrc_id IN (SELECT xtrsrc_id 
                                       FROM tempmultcatbasesources 
                                     GROUP BY xtrsrc_id 
                                     HAVING COUNT(*) > 1
                                    )
            """
            query_start = time.time()
            cursor.execute(sql_replace_single_known_source_by_multiple)
            query83_time = time.time() - query_start
            print "\tQuery ", query, ": ", str(round(query83_time*1000,2)), "ms"
            conn.commit()
            
            #if catids[i] != 4:
            query = 84
            sql_delete_single_known_source = """\
              DELETE 
                FROM multcatbasesources 
               WHERE xtrsrc_id IN (SELECT xtrsrc_id 
                                     FROM tempmultcatbasesources 
                                   GROUP BY xtrsrc_id 
                                   HAVING COUNT(*) > 1
                                  )
            """
            query_start = time.time()
            cursor.execute(sql_delete_single_known_source)
            query84_time = time.time() - query_start
            print "\tQuery ", query, ": ", str(round(query84_time*1000,2)), "ms"
            conn.commit()
            
            #if catids[i] != 4:
            query = 85
            sql_delete_multiple_assocs = """\
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
            query_start = time.time()
            cursor.execute(sql_delete_multiple_assocs)
            query85_time = time.time() - query_start
            print "\tQuery ", query, ": ", str(round(query85_time*1000,2)), "ms"
            conn.commit()
            
            #if catids[i] != 4:
            query = 9
            sql_append_known_sources_assocs = """\
              INSERT INTO assoccatsources
                (xtrsrc_id
                ,assoc_catsrc_id
                )
                SELECT xtrsrc_id
                      ,assoc_xtrsrc_id as assoc_catsrc_id
                  FROM tempmultcatbasesources 
            """
            query_start = time.time()
            cursor.execute(sql_append_known_sources_assocs)
            query9_time = time.time() - query_start
            print "\tQuery ", query, ": ", str(round(query9_time*1000,2)), "ms"
            conn.commit()
            
            query = 91
            sql_append_known_sources_assocs = """\
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
                      ,xtrsrc_id
                  FROM tempmultcatbasesources 
            """
            query_start = time.time()
            cursor.execute(sql_append_known_sources_assocs)
            query91_time = time.time() - query_start
            print "\tQuery ", query, ": ", str(round(query91_time*1000,2)), "ms"
            #if catids[i] == 4:
            y = cursor.fetchall()
            print "\tlen(y) = ", len(y)
            query = 10
            query10_start = time.time()
            for k in range(len(y)):
                #print y[k][0], y[k][1], y[k][2]
                query = 100
                sql_update_known_sources_row_by_row = """\
                  UPDATE multcatbasesources 
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
                  WHERE xtrsrc_id = %s
                """
                query_start = time.time()
                cursor.execute(sql_update_known_sources_row_by_row,(y[k][0] \
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
                                                                   ))
                query100_time = time.time() - query_start
                if (k % 100 == 0):
                    print "\t[",k,"] Query ", query, ": ", str(round(query100_time*1000,2)), "ms"
            query10_time = time.time() - query10_start
            print "\tQuery ", query, ": ", str(round(query10_time,2)), "s"
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
            
            #if catids[i] != 4:
            query = 11
            query_start = time.time()
            cursor.execute("DELETE FROM tempmultcatbasesources")
            query11_time = time.time() - query_start
            print "\tQuery ", query, ": ", str(round(query11_time*1000,2)), "ms"
            conn.commit()

            #if catids[i] != 4:
            query = 110
            sql_count_known_sources = """\
              SELECT COUNT(*)
                FROM extractedsources x0 
                    ,multcatbasesources b0 
               WHERE x0.image_id = %s
                 AND b0.zone BETWEEN x0.zone - cast(0.025 as integer) 
                                 AND x0.zone + cast(0.025 as integer) 
                 AND b0.decl_avg BETWEEN x0.decl - 0.025 
                                     AND x0.decl + 0.025 
                 AND b0.ra_avg BETWEEN x0.ra - alpha(0.025,x0.decl) 
                                   AND x0.ra + alpha(0.025,x0.decl) 
                 AND ASIN(SQRT((x0.x - b0.x)*(x0.x - b0.x)  
                              +(x0.y - b0.y)*(x0.y - b0.y)  
                              +(x0.z - b0.z)*(x0.z - b0.z) 
                              ) 
                         / 2 
                         ) 
                     / 
                     SQRT( x0.ra_err * x0.ra_err + b0.ra_err_avg * b0.ra_err_avg 
                         + x0.decl_err * x0.decl_err + b0.decl_err_avg * b0.decl_err_avg) 
                     < 7.272E-6 
            """
            query_start = time.time()
            cursor.execute(sql_count_known_sources, (imgid,))
            query110_time = time.time() - query_start
            print "\tQuery ", query, ": ", str(round(query110_time*1000,2)), "ms"
            y=cursor.fetchall()
            print "Number of known sources (or sources in NOT IN): ", y[0][0]
            conn.commit()
            
            #if catids[i] != 4:
            query = 12
            sql_insert_new_sources = """\
              INSERT INTO multcatbasesources 
                (xtrsrc_id 
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
                ) 
                SELECT x1.xtrsrcid 
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
                  FROM extractedsources x1 
                 WHERE x1.image_id = %s
                   AND x1.xtrsrcid NOT IN (SELECT x0.xtrsrcid 
                                             FROM extractedsources x0 
                                                 ,multcatbasesources b0 
                                            WHERE x0.image_id = %s
                                              AND b0.zone BETWEEN x0.zone - cast(0.025 as integer) 
                                                              AND x0.zone + cast(0.025 as integer) 
                                              AND b0.decl_avg BETWEEN x0.decl - 0.025 
                                                                  AND x0.decl + 0.025 
                                              AND b0.ra_avg BETWEEN x0.ra - alpha(0.025,x0.decl) 
                                                                AND x0.ra + alpha(0.025,x0.decl) 
                                              AND ASIN(SQRT((x0.x - b0.x)*(x0.x - b0.x)  
                                                           +(x0.y - b0.y)*(x0.y - b0.y)  
                                                           +(x0.z - b0.z)*(x0.z - b0.z) 
                                                           ) 
                                                      / 2 
                                                      ) 
                                                  / 
                                                  SQRT( x0.ra_err * x0.ra_err + b0.ra_err_avg * b0.ra_err_avg 
                                                      + x0.decl_err * x0.decl_err + b0.decl_err_avg * b0.decl_err_avg) 
                                                  < 7.272E-6 
                                          )
            """
            query_start = time.time()
            cursor.execute(sql_insert_new_sources, (imgid,imgid))
            query12_time = time.time() - query_start
            print "\tQuery ", query, ": ", str(round(query12_time*1000,2)), "ms"
            conn.commit()
            
            """
            detect_start= time.time()
            query = 13
            cursor.execute("select xtrsrc_id " + \
                           "      ,datapoints " + \
                           "      ,sqrt((i_peak_sq_sum - i_peak_sum*i_peak_sum/datapoints) / (datapoints - 1))  " + \
                           "       / (i_peak_sum/datapoints) as mag_var_peak " + \
                           "      ,weight_i_peak_sq_sum/(datapoints - 1) " + \
                           "       - datapoints * weight_i_peak_sum * weight_i_peak_sum / (datapoints - 1) " + \
                           "       as sig_var_weigthed_peak " + \
                           "  from basesources " + \
                           " where datapoints > 1 " + \
                           "   and ds_id = %s " + \
                           "order by sig_var_weigthed_peak desc ", (dsid,))
            #det = cursor.fetchall()
            #print "len(det) = ", len(det)
            conn.commit()
            """
            iter_end = time.time() - iter_start
            
            #+=========================================================================+
            #| iter | imageid | query1_time | query2_time | query5_time | query11_time |
            #+=========================================================================+
            row = str(z) + \
                  "\t" + str(i) + \
                  "\t" + str(imgid) + \
                  "\t" + str(round(query5_time*1000,1)) + \
                  " ms\t" + str(round(query8_time*1000,1)) + \
                  " ms\t" + str(round(query9_time*1000,1)) + \
                  " ms\t" + str(round(query10_time*1000,1)) + \
                  " ms\t" + str(round(query12_time*1000,1)) + \
                  " ms\t" + str(round(iter_end,3)) + ' s\n'
            #if (i % 100 == 0):
            print row
            
            logf.write(row)
            
            #if catids[i] == 4:
            #    break

        i += 1

    # To select the sources that could be associated in all three catalogs
    """
      select ac2.xtrsrc_id
            ,c3.cat_id
            ,c3.freq_eff
            ,c3.i_peak_avg
            ,c3.i_int_avg
            ,ac2.assoc_catsrc_id
            ,c4.cat_id
            ,c4.freq_eff
            ,c4.i_peak_avg
            ,c4.i_int_avg 
        from assoccatsources ac2
            ,catalogedsources c3
            ,catalogedsources c4 
       where ac2.xtrsrc_id = c3.catsrcid 
         and ac2.assoc_catsrc_id = c4.catsrcid 
         and ac2.xtrsrc_id in (select ac1.xtrsrc_id 
                                 from assoccatsources ac1
                                     ,catalogedsources c1
                                     ,catalogedsources c2 
                                where xtrsrc_id = c1.catsrcid 
                                  and assoc_catsrc_id = c2.catsrcid 
                                  and xtrsrc_id in (select xtrsrc_id 
                                                      from assoccatsources 
                                                    group by xtrsrc_id 
                                                    having count(*) > 1
                                                   ) 
                                  and c2.cat_id = 4 
                                  and c2.i_int_avg > 10 -- having a flux at 74MHz > 10Jy
                              ) 
      order by ac2.xtrsrc_id
              ,ac2.assoc_catsrc_id 
    """


    cursor.close()
    logf.close()
    print "Results stored in log file:\n", lf
except db.Error, e:
    logging.warn("Failed on query nr %s reason: %s " % (query, e))
    logf.write("Failed on query nr %s reason: %s " % (query, e))
    logf.close()
    logging.debug("Failed query nr: %s, reason: %s" % (query, e))

