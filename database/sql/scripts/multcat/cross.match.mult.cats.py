import os
import time
import sys
from datetime import datetime

import monetdb.sql as db

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
db_dbase = "crossmatch2"
db_user = "crossmatch2" 
db_passwd = "ch4"

monetdbtkphome = os.getenv('MONETDBTKPHOME') 
#monetdbtkphome = '/scratch/bscheers'
path = monetdbtkphome + '/scripts/multcat'

#f = '/copy.into.extractedsources.' + str(ns) + '.csv'
#infile = path + f

logtime = time.strftime("%Y%m%d-%H%M")
lf = '/logs/cross.match.multcat.assoc.' + host + '.' + logtime + '.log'
logfile = path + lf
logf = open(logfile, 'w')
row = 'csv log file of processing times of the multi-catalog association. \n'
logf.write(row)
row = '+========================================================================+\n'
logf.write(row)
row = '| iter | imageid | query1_time | ........... | query20_time | total_time |\n'
logf.write(row)
row = '+========================================================================+\n'
logf.write(row)

conn = db.connect(hostname=db_host,database=db_dbase,username=db_user,password=db_passwd)
#conn = db.connect(host=db_host,db=db_dbase,user=db_user,passwd=db_passwd, unix_socket="/scratch/bscheers/databases/mysql/var/mysql.sock")

query = 0
query_time = []
sql_st = []

try:
    iter_start = time.time()
    cursor = conn.cursor()
    
    if loadlsm == 'Y':
        query = -2
        sql_st.append("""\
        CALL LoadLSM(0,360,30,90,'NVSS','VLSS','WENSS')
        """)
        #sql_load_lsm = """\
        #  CALL LoadLSM(90,120,30,60,'NVSS','VLSS','WENSS')
        #CALL LoadLSM(95,100,40,45,'NVSS','VLSS','WENSS')
        #"""
        query_start = time.time()
        cursor.execute(sql_st[-1])
        query_time.append((time.time() - query_start))
        print "\tQuery ", query, ": ", str(round(query_time[-1] * 1000, 2)), "ms"
        conn.commit()
        print "LSM Loaded"
    else:
        print "LSM NOT Loaded"
    
    """
    This corresponds to missing less than 0.1% of the assocs 
    """
    deRuiter_r = 3.717/3600.

    query = -1
    sql_st.append("""\
    SELECT insertDataset('Cross-Match Multiple Catalogues')
    """)
    query_start = time.time()
    cursor.execute(sql_st[-1])
    query_time.append((time.time() - query_start))
    print "\tQuery ", query, ": ", str(round(query_time[-1]*1000,2)), "ms"
    dsid = cursor.fetchone()[0]
    conn.commit()
    print "dsid = ", dsid
    
    #catids = [3,4,5] #[NVSS,VLSS,WENSS]
    catids = [3,5,4] #[NVSS,WENSS,VLSS]
    for i in range(len(catids)):
        #for z in range(38,39):
        for z in range(30,91):
            query = 0
            query_time = []
            print "Processing sources from catids[", i, "] = ", catids[i]
            print "Zone ", z, "start"
            obstime = datetime.now()
            params = [dsid \
                     ,42000000. \
                     ,4000000. \
                     ,obstime.strftime("%Y-%m-%d-%H:%M:%S") + '.' + str(obstime.microsecond) \
                     ,'sources from catid: ' + str(catids[i]) + ': zone = ' + str(z)
                     ]
            query +=1
            #cursor.execute("SELECT insertImage(%s,%s,%s,%s,%s)", params)
            sql_st.append("""\
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
            """)
            query_start = time.time()
            cursor.execute(sql_st[-1], (params[0],params[1],params[2],params[3],params[4]))
            query_time.append((time.time() - query_start))
            print "\tQuery ", query, ": ", str(round(query_time[-1]*1000,2)), "ms"
            #imgid = cursor.fetchone()[0]
            imgid = int(cursor.lastrowid)
            conn.commit()
            #print "imgid = ", imgid
            
            query +=1
            sql_st.append("""\
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
            """)
            query_start = time.time()
            cursor.execute(sql_st[-1], (imgid,catids[i],z))
            query_time.append((time.time() - query_start))
            print "\tQuery ", query, ": ", str(round(query_time[-1]*1000,2)), "ms"
            conn.commit()
            
            query +=1
            query_start = time.time()
            sql_st.append("""\
            DELETE FROM tempmultcatbasesources
            """)
            cursor.execute(sql_st[-1])
            query_time.append((time.time() - query_start))
            print "\tQuery ", query, ": ", str(round(query_time[-1]*1000,2)), "ms"
            conn.commit()
            
            """
            Here we select the extractedsources that have a positional match with the 
            sources in the running catalogue (multcatbasesources)
            """
            query +=1
            # May be replaced by procedure AssocXSrc2RunningCat
            #CALL AssocXSrc2RunningCat(%s, %s)
            sql_st.append("""\
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
                         AND SQRT((x0.ra - b0.ra_avg) * COS(RADIANS(x0.decl)) 
                                  * (x0.ra - b0.ra_avg) * COS(RADIANS(x0.decl))
                                  /(x0.ra_err * x0.ra_err + b0.ra_err_avg * b0.ra_err_avg)
                                 +(x0.decl - b0.decl_avg) * (x0.decl - b0.decl_avg)
                                  /(x0.decl_err * x0.decl_err + b0.decl_err_avg * b0.decl_err_avg)
                                 ) < %s 
                     ) t0
            """)
            # This result set might contain multiple associations (1-n,n-1)
            # for a single known source in multcatbasesources.
            # The n-1 assocs will treated similar as the 1-1 assocs.
            query_start = time.time()
            cursor.execute(sql_st[-1], (imgid, deRuiter_r))
            query_time.append((time.time() - query_start))
            print "\tQuery ", query, ": ", str(round(query_time[-1]*1000,2)), "ms"
            conn.commit()
           
            """
            Before we continue, we first take care of the sources 
            that have multiple associations in both directions.
            
            -1- running-catalogue sources  <- extracted source
            An extracted source has multiple counterparts in the
            running catalogue.
            We only keep the ones with the lowest deRuiter_r value,
            the rest we throw away.
            NOTE :
            It is worth considering whether this might be changed to
            selecting the brightest neighbour source, instead of
            just the closest neighbour.
            (There are case [when flux_lim > 10Jy] that the nearest source
             has a lower flux level, causing unexpected spectral indices)
            """
            query +=1
            sql_st.append("""\
            SELECT t1.xtrsrc_id
                  ,t1.assoc_xtrsrc_id
              FROM (SELECT tb0.assoc_xtrsrc_id
                          ,MIN(SQRT((x0.ra - b0.ra_avg) * COS(RADIANS(x0.decl))  
                          * (x0.ra - b0.ra_avg) * COS(RADIANS(x0.decl))
                          /(x0.ra_err * x0.ra_err + b0.ra_err_avg * b0.ra_err_avg)
                          +(x0.decl - b0.decl_avg) * (x0.decl - b0.decl_avg)
                          /(x0.decl_err * x0.decl_err + b0.decl_err_avg * b0.decl_err_avg)
                          )) as min_r1     
                      FROM tempmultcatbasesources tb0
                          ,multcatbasesources b0
                          ,extractedsources x0
                     WHERE tb0.assoc_xtrsrc_id IN (SELECT assoc_xtrsrc_id
                                                     FROM tempmultcatbasesources 
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
                      FROM tempmultcatbasesources tb1 
                          ,multcatbasesources b1
                          ,extractedsources x1
                     WHERE tb1.assoc_xtrsrc_id IN (SELECT assoc_xtrsrc_id
                                                     FROM tempmultcatbasesources 
                                                   GROUP BY assoc_xtrsrc_id 
                                                   HAVING COUNT(*) > 1
                                                  )
                       AND tb1.xtrsrc_id = b1.xtrsrc_id
                       AND tb1.assoc_xtrsrc_id = x1.xtrsrcid
                   ) t1
             WHERE t1.assoc_xtrsrc_id = t0.assoc_xtrsrc_id
               AND t1.r1 > t0.min_r1
            """)
            query_start = time.time()
            cursor.execute(sql_st[-1])
            query_time.append((time.time() - query_start))
            print "\tQuery ", query, ": ", str(round(query_time[-1]*1000,2)), "ms"
            results = zip(*cursor.fetchall())
            if len(results) != 0:
                xtrsrc_id = results[0]
                assoc_xtrsrc_id = results[1]
            
                query += 1
                # TODO: Consider setting row to inactive instead of deleting
                sql_st.append("""\
                DELETE
                  FROM tempmultcatbasesources 
                 WHERE xtrsrc_id = %s
                   AND assoc_xtrsrc_id = %s
                """)
                query_start = time.time()
                for j in range(len(xtrsrc_id)):
                    cursor.execute(sql_st[-1], (xtrsrc_id[j],assoc_xtrsrc_id[j]))
                query_time.append((time.time() - query_start))
                print "\tQuery ", query, ": ", str(round(query_time[-1]*1000,2)), "ms"
                conn.commit()
            
            """
            -2- Now, we take care of the sources in the running catalogue 
            that have more than one counterpart among the extracted sources.
            We now make two entries in the running catalogue, in stead of the one we
            had before. Therefore, we 'swap' the ids.
            """
            query += 1
            sql_st.append("""\
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
            """)
            query_start = time.time()
            cursor.execute(sql_st[-1])
            query_time.append((time.time() - query_start))
            print "\tQuery ", query, ": ", str(round(query_time[-1]*1000,2)), "ms"
            conn.commit()
            
            """
            -3- And, we have to insert identical ids to identify a
            light curve starting point.
            """
            query += 1
            sql_st.append("""\
            INSERT INTO assoccatsources
              (xtrsrc_id
              ,assoc_catsrc_id
              )
              SELECT assoc_xtrsrc_id
                    ,assoc_xtrsrc_id
                FROM tempmultcatbasesources 
               WHERE xtrsrc_id IN (SELECT xtrsrc_id 
                                     FROM tempmultcatbasesources 
                                   GROUP BY xtrsrc_id 
                                   HAVING COUNT(*) > 1
                                  )
            """)
            query_start = time.time()
            cursor.execute(sql_st[-1])
            query_time.append((time.time() - query_start))
            print "\tQuery ", query, ": ", str(round(query_time[-1]*1000,2)), "ms"
            conn.commit()
            
            """
            -4- And, we throw away the swapped id
            Maybe TODO, It might be better to flag this record...
            """
            query += 1
            # TODO: Consider setting rows to inactive instead of deleting
            sql_st.append("""\
            DELETE 
              FROM assoccatsources
             WHERE xtrsrc_id IN (SELECT xtrsrc_id 
                                   FROM tempmultcatbasesources 
                                 GROUP BY xtrsrc_id 
                                 HAVING COUNT(*) > 1
                                )
            """)
            query_start = time.time()
            cursor.execute(sql_st[-1])
            query_time.append((time.time() - query_start))
            print "\tQuery ", query, ": ", str(round(query_time[-1]*1000,2)), "ms"
            conn.commit()
            
            """
            Here we insert new ids of the sources in the running catalogue
            """
            query += 1
            sql_st.append("""\
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
            """)
            query_start = time.time()
            cursor.execute(sql_st[-1])
            query_time.append((time.time() - query_start))
            print "\tQuery ", query, ": ", str(round(query_time[-1]*1000,2)), "ms"
            conn.commit()
            
            query += 1
            # TODO: Consider setting row to inactive instead of deleting
            sql_st.append("""\
            DELETE 
              FROM multcatbasesources 
             WHERE xtrsrc_id IN (SELECT xtrsrc_id 
                                   FROM tempmultcatbasesources 
                                 GROUP BY xtrsrc_id 
                                 HAVING COUNT(*) > 1
                                )
            """)
            query_start = time.time()
            cursor.execute(sql_st[-1])
            query_time.append((time.time() - query_start))
            print "\tQuery ", query, ": ", str(round(query_time[-1]*1000,2)), "ms"
            conn.commit()
            
            query += 1
            # TODO: Consider setting row to inactive instead of deleting
            sql_st.append("""\
            DELETE 
              FROM tempmultcatbasesources 
             WHERE xtrsrc_id IN (SELECT xtrsrc_id 
                                   FROM tempmultcatbasesources 
                                 GROUP BY xtrsrc_id 
                                 HAVING COUNT(*) > 1
                                )
            """)
            # The resulting content of tempmultcatbasesources
            # will be the 1-1 and n-1 assocs.
            query_start = time.time()
            cursor.execute(sql_st[-1])
            query_time.append((time.time() - query_start))
            print "\tQuery ", query, ": ", str(round(query_time[-1]*1000,2)), "ms"
            conn.commit()
            
            """
            After all this, we are now left with the 1-1 assocs
            """

            query += 1
            sql_st.append("""\
            INSERT INTO assoccatsources
              (xtrsrc_id
              ,assoc_catsrc_id
              )
              SELECT xtrsrc_id
                    ,assoc_xtrsrc_id as assoc_catsrc_id
                FROM tempmultcatbasesources 
            """)
            query_start = time.time()
            cursor.execute(sql_st[-1])
            query_time.append((time.time() - query_start))
            print "\tQuery ", query, ": ", str(round(query_time[-1]*1000,2)), "ms"
            conn.commit()
            
            """
            Since Jun2010 version we cannot use the massive update statement anymore.
            Therefore, unfortunately, we cursor through the tempsources table
            """
            query += 1
            sql_st.append("""\
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
            """)
            query_start = time.time()
            cursor.execute(sql_st[-1])
            query_time.append((time.time() - query_start))
            print "\tQuery ", query, ": ", str(round(query_time[-1]*1000,2)), "ms"
            
            y = cursor.fetchall()
            print "\t\tlen(y) = ", len(y)
            
            query += 1
            sql_st.append("""\
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
            """)
            query_start = time.time()
            for k in range(len(y)):
                #print y[k][0], y[k][1], y[k][2]
                cursor.execute(sql_st[-1], (y[k][0] \
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
                if (k % 100 == 0):
                    print "\t\tQuery ", query, "; iter", k
            query_time.append((time.time() - query_start))
            print "\tQuery ", query, ": ", str(round(query_time[-1]*1000,2)), "ms"
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
            query += 1
            query_start = time.time()
            sql_st.append("""\
            DELETE FROM tempmultcatbasesources
            """)
            cursor.execute(sql_st[-1])
            query_time.append((time.time() - query_start))
            print "\tQuery ", query, ": ", str(round(query_time[-1]*1000,2)), "ms"
            conn.commit()

            #if catids[i] != 4:
            query += 1
            sql_st.append("""\
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
               AND SQRT((x0.ra - b0.ra_avg) * COS(RADIANS(x0.decl)) 
                        * (x0.ra - b0.ra_avg) * COS(RADIANS(x0.decl))
                        /(x0.ra_err * x0.ra_err + b0.ra_err_avg * b0.ra_err_avg)
                       +(x0.decl - b0.decl_avg) * (x0.decl - b0.decl_avg)
                        /(x0.decl_err * x0.decl_err + b0.decl_err_avg * b0.decl_err_avg)
                       ) < %s 
            """)
            query_start = time.time()
            cursor.execute(sql_st[-1], (imgid,deRuiter_r))
            query_time.append((time.time() - query_start))
            print "\tQuery ", query, ": ", str(round(query_time[-1]*1000,2)), "ms"
            y=cursor.fetchall()
            print "\t\tNumber of known sources (or sources in NOT IN): ", y[0][0]
            conn.commit()
            
            query += 1
            sql_st.append("""\
            INSERT INTO assoccatsources 
              (xtrsrc_id 
              ,assoc_catsrc_id
              ) 
              SELECT x1.xtrsrcid as xtrsrc_id
                    ,x1.xtrsrcid as assoc_catsrc_id
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
            """)
            query_start = time.time()
            cursor.execute(sql_st[-1], (imgid,imgid,deRuiter_r))
            query_time.append((time.time() - query_start))
            print "\tQuery ", query, ": ", str(round(query_time[-1]*1000,2)), "ms"
            conn.commit()
            
            query += 1
            sql_st.append("""\
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
            """)
            query_start = time.time()
            cursor.execute(sql_st[-1], (imgid,imgid,deRuiter_r))
            query_time.append((time.time() - query_start))
            print "\tQuery ", query, ": ", str(round(query_time[-1]*1000,2)), "ms"
            conn.commit()
            
            iter_end = time.time() - iter_start
            print "Elapsed time:", str(round(iter_end,2)), "seconds"
            
            #+=========================================================================+
            #| iter | imageid | query1_time | ........... | query20_time | total_time  |
            #+=========================================================================+
            
            row = str(z) + ';' + str(i) + ';' + str(imgid) + ';'
            for s in range(len(query_time)):
                row += ';' + str(s) + ':' + str(round(query_time[s]*1000,1))
            row += ';' + str(round(iter_end,3)) + '\n'
            #if (i % 100 == 0):
            #  print row
            
            logf.write(row)
            
            #if catids[i] == 4:
            #    break
            print "Zone ", z, "ready"

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
    print "Results stored in log file:\n", logfile
except db.Error, e:
    logging.warn("Failed on query nr %s reason: %s " % (query, e))
    logging.warn("Failed on query: %s " % (sql_st[-1], ))
    logf.write("Failed on query nr %s reason: %s " % (query, e))
    logf.close()
    logging.debug("Failed query nr: %s, reason: %s" % (query, e))

