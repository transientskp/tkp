import os, errno, time, sys
from datetime import datetime
import monetdb.sql as db
from monetdb.sql import Error as Error
#import MySQLdb as db
#from MySQLdb import Error as Error
import logging

host = sys.argv[1] # number of sources per image
ns = int(sys.argv[2]) # number of sources per image
iter = int(sys.argv[3]) # number of images to process

db_type = "MonetDB"
#db_type = "MySQL"
db_host = host
db_port = 50000
#db_dbase = "simrsm" + str(ns)
db_dbase = "simrsm"
#db_user = "simrsm" + str(ns)
db_user = "simrsm" 
db_passwd = "ch2"

monetdbtkphome = os.getenv('MONETDBTKPHOME') 
#monetdbtkphome = '/scratch/bscheers'
path = monetdbtkphome + '/scripts/simrsm'

f = '/copy.into.extractedsources.' + str(ns) + '.csv'
infile = path + f

logtime = time.strftime("%Y%m%d-%H%M")
lf = '/logs/insert.assoc.' + host + '.' + db_type + '.' + str(ns) + '.sources.per.image.' + str(iter) + '.images.' + logtime + '.log'
logfile = path + lf
logf = open(logfile, 'w')
row = 'csv log file of processing times of the insertion and association ' + \
'of detected sources.\n' + \
str(ns) + ' sources per image, ' + str(iter) + ' images.\n'
logf.write(row)
row = '+===================================================================================================+\n'
logf.write(row)
row = '| iter | imageid | insert_xtr_time | update_base_time | insert_base_time | detect_time | total_time |\n'
logf.write(row)
row = '+===================================================================================================+\n'
logf.write(row)

conn = db.connect(hostname=db_host,database=db_dbase,username=db_user,password=db_passwd)
#conn = db.connect(host=db_host,db=db_dbase,user=db_user,passwd=db_passwd, unix_socket="/scratch/bscheers/databases/mysql/var/mysql.sock")

try:
    cursor = conn.cursor()
    # ThIS query concatenates the requested columns per row in a single string in the correct BBS format.
    query = 1
    cursor.execute("SELECT insertDataset('In Python')")
    dsid = cursor.fetchone()[0]
    conn.commit()
    print "dsid = ", dsid
    
    for i in range(iter):
        obstime = datetime.now()
        params = [dsid \
                 ,42000000. \
                 ,4000000. \
                 ,obstime.strftime("%Y-%m-%d-%H:%M:%S") + '.' + str(obstime.microsecond) \
                 ,'/no/file'
                 ]
        query = 2
        #cursor.execute("SELECT insertImage(%s,%s,%s,%s,%s)", params)
        cursor.execute("INSERT INTO images " + \
                       "  (ds_id " + \
                       "  ,tau " + \
                       "  ,band " + \
                       "  ,tau_time " + \
                       "  ,freq_eff " + \
                       "  ,freq_bw " + \
                       "  ,taustart_ts " + \
                       "  ,url " + \
                       "  )  " + \
                       "VALUES " + \
                       "  (%s " + \
                       "  ,1 " + \
                       "  ,4 " + \
                       "  ,3600 " + \
                       "  ,%s " + \
                       "  ,%s " + \
                       "  ,%s " + \
                       "  ,%s " + \
                       "  ) ",  (params[0],params[1],params[2],params[3],params[4]))
        #imgid = cursor.fetchone()[0]
        imgid = int(cursor.lastrowid)
        conn.commit()
        #print "imgid = ", imgid
        
        insert_xtr_start = time.time()
        """
        if (i > 0 and i % 1000 == 0):
            cursor.execute("DROP TABLE loadxtrsources")
            conn.commit()
            cursor.execute("CREATE TABLE loadxtrsources " + \
                           "  (limage_id INT NOT NULL " + \
                           "  ,lra DOUBLE NOT NULL " + \
                           "  ,ldecl DOUBLE NOT NULL " + \
                           "  ,lra_err DOUBLE NOT NULL " + \
                           "  ,ldecl_err DOUBLE NOT NULL " + \
                           "  ,lI_peak DOUBLE NULL " + \
                           "  ,lI_peak_err DOUBLE NULL " + \
                           "  ,lI_int DOUBLE NULL " + \
                           "  ,lI_int_err DOUBLE NULL " + \
                           "  ,ldet_sigma DOUBLE NOT NULL " + \
                           "  )")
            conn.commit()
        else:
        """
        query = 3
        cursor.execute("DELETE FROM loadxtrsources")
        conn.commit()
        
        query = 4
        cursor.execute("COPY %s RECORDS " + \
                       "INTO loadxtrsources " + \
                       "FROM %s " + \
                       "USING DELIMITERS ',' " + \
                       "                ,'\n' " + \
                       "NULL AS '' ", (ns, infile))
        #conn.commit()
        
        query = 5
        cursor.execute("INSERT INTO extractedsources " + \
                       "  (image_id  " + \
                       "  ,zone " + \
                       "  ,ra " + \
                       "  ,decl " + \
                       "  ,ra_err " + \
                       "  ,decl_err " + \
                       "  ,x " + \
                       "  ,y " + \
                       "  ,z " + \
                       "  ,det_sigma " + \
                       "  ,I_peak " + \
                       "  ,I_peak_err " + \
                       "  ,I_int " + \
                       "  ,I_int_err " + \
                       "  ) " + \
                       "  SELECT %s " + \
                       "        ,CAST(FLOOR(ldecl/1) AS INTEGER) " + \
                       "        ,lra " + \
                       "        ,ldecl " + \
                       "        ,lra_err * 3600 " + \
                       "        ,ldecl_err * 3600 " + \
                       "        ,COS(RADIANS(ldecl)) * COS(RADIANS(lra)) " + \
                       "        ,COS(RADIANS(ldecl)) * SIN(RADIANS(lra)) " + \
                       "        ,SIN(RADIANS(ldecl)) " + \
                       "        ,ldet_sigma " + \
                       "        ,lI_peak " + \
                       "        ,lI_peak_err " + \
                       "        ,lI_int " + \
                       "        ,lI_int_err " + \
                       "    FROM loadxtrsources ", (imgid,))
        #conn.commit()
        
        query = 6
        cursor.execute("DELETE FROM loadxtrsources")
        conn.commit()
        
        update_base_start = time.time()
        
        query = 7
        cursor.execute("DELETE FROM tempbasesources")
        conn.commit()
        
        query = 8
        cursor.execute("INSERT INTO tempbasesources " + \
                       "  (xtrsrc_id " + \
                       "  ,datapoints " + \
                       "  ,I_peak_sum " + \
                       "  ,I_peak_sq_sum " + \
                       "  ,weight_peak_sum " + \
                       "  ,weight_I_peak_sum  " + \
                       "  ,weight_I_peak_sq_sum  " + \
                       "  ) " + \
                       "  SELECT b0.xtrsrc_id " + \
                       "        ,b0.datapoints  " + \
                       "         + 1 as datapoints " + \
                       "        ,b0.I_peak_sum  " + \
                       "         + x0.I_peak as i_peak_sum " + \
                       "        ,b0.I_peak_sq_sum  " + \
                       "         + x0.I_peak * x0.I_peak as i_peak_sq_sum " + \
                       "        ,b0.weight_peak_sum  " + \
                       "         + 1 / (x0.I_peak_err * x0.I_peak_err) as weight_peak_sum " + \
                       "        ,b0.weight_I_peak_sum  " + \
                       "         + x0.I_peak / (x0.I_peak_err * x0.I_peak_err) as weight_i_peak_sum " + \
                       "        ,b0.weight_I_peak_sq_sum  " + \
                       "         + x0.I_peak * x0.I_peak / (x0.I_peak_err * x0.I_peak_err) as weight_i_peak_sq_sum " + \
                       "    FROM basesources b0 " + \
                       "        ,extractedsources x0 " + \
                       "   WHERE x0.image_id = %s " + \
                       "     AND b0.zone BETWEEN x0.zone - 1 AND x0.zone + 1 " + \
                       "     AND ASIN(SQRT((x0.x - b0.x)*(x0.x - b0.x)  " + \
                       "                  +(x0.y - b0.y)*(x0.y - b0.y)  " + \
                       "                  +(x0.z - b0.z)*(x0.z - b0.z) " + \
                       "                  )/2 " + \
                       "             )  " + \
                       "         / " + \
                       "         SQRT(x0.ra_err * x0.ra_err + b0.ra_err * b0.ra_err " + \
                       "             +x0.decl_err * x0.decl_err + b0.decl_err * b0.decl_err) " + \
                       "         < 7.272E-6 ", (imgid,))
        # Check commit here 
        conn.commit()
        
        query = 9
        cursor.execute("UPDATE basesources " + \
                       "   SET datapoints = (SELECT datapoints " + \
                       "                       FROM tempbasesources " + \
                       "                      WHERE tempbasesources.xtrsrc_id = basesources.xtrsrc_id " + \
                       "                    ) " + \
                       "      ,i_peak_sum = (SELECT i_peak_sum " + \
                       "                       FROM tempbasesources " + \
                       "                      WHERE tempbasesources.xtrsrc_id = basesources.xtrsrc_id " + \
                       "                    ) " + \
                       "      ,i_peak_sq_sum = (SELECT i_peak_sq_sum " + \
                       "                       FROM tempbasesources " + \
                       "                      WHERE tempbasesources.xtrsrc_id = basesources.xtrsrc_id " + \
                       "                    ) " + \
                       "      ,weight_peak_sum = (SELECT weight_peak_sum " + \
                       "                       FROM tempbasesources " + \
                       "                      WHERE tempbasesources.xtrsrc_id = basesources.xtrsrc_id " + \
                       "                    ) " + \
                       "      ,weight_i_peak_sum = (SELECT weight_i_peak_sum " + \
                       "                       FROM tempbasesources " + \
                       "                      WHERE tempbasesources.xtrsrc_id = basesources.xtrsrc_id " + \
                       "                    ) " + \
                       "      ,weight_i_peak_sq_sum = (SELECT weight_i_peak_sq_sum " + \
                       "                       FROM tempbasesources " + \
                       "                      WHERE tempbasesources.xtrsrc_id = basesources.xtrsrc_id " + \
                       "                    ) " + \
                       " WHERE EXISTS (SELECT xtrsrc_id " + \
                       "                 FROM tempbasesources " + \
                       "                WHERE tempbasesources.xtrsrc_id = basesources.xtrsrc_id " + \
                       "              ) ")
        conn.commit()
        
        query = 10
        cursor.execute("DELETE FROM tempbasesources")
        conn.commit()

        query = 11
        insert_base_start = time.time()
        cursor.execute("INSERT INTO basesources " + \
                       "  (xtrsrc_id " + \
                       "  ,ds_id " + \
                       "  ,image_id " + \
                       "  ,zone " + \
                       "  ,ra " + \
                       "  ,decl " + \
                       "  ,ra_err " + \
                       "  ,decl_err " + \
                       "  ,x " + \
                       "  ,y " + \
                       "  ,z " + \
                       "  ,datapoints " + \
                       "  ,I_peak_sum " + \
                       "  ,I_peak_sq_sum " + \
                       "  ,weight_peak_sum " + \
                       "  ,weight_I_peak_sum " + \
                       "  ,weight_I_peak_sq_sum " + \
                       "  ) " + \
                       "  SELECT x1.xtrsrcid " + \
                       "        ,im1.ds_id " + \
                       "        ,im1.imageid " + \
                       "        ,x1.zone " + \
                       "        ,x1.ra " + \
                       "        ,x1.decl " + \
                       "        ,x1.ra_err " + \
                       "        ,x1.decl_err " + \
                       "        ,x1.x " + \
                       "        ,x1.y " + \
                       "        ,x1.z " + \
                       "        ,1 " + \
                       "        ,x1.I_peak " + \
                       "        ,x1.I_peak * x1.I_peak " + \
                       "        ,1 / (x1.I_peak_err * x1.I_peak_err) " + \
                       "        ,x1.I_peak / (x1.I_peak_err * x1.I_peak_err) " + \
                       "        ,x1.I_peak * x1.I_peak / (x1.I_peak_err * x1.I_peak_err) " + \
                       "    FROM extractedsources x1 " + \
                       "        ,images im1 " + \
                       "   WHERE x1.image_id = %s " + \
                       "     AND im1.imageid = x1.image_id " + \
                       "     AND x1.xtrsrcid NOT IN (SELECT x0.xtrsrcid " + \
                       "                               FROM extractedsources x0 " + \
                       "                                   ,basesources b0 " + \
                       "                              WHERE x0.image_id = %s " + \
                       "                                and b0.zone between x0.zone -1 and x0.zone + 1 " + \
                       "                                AND ASIN(SQRT((x0.x - b0.x)*(x0.x - b0.x)  " + \
                       "                                             +(x0.y - b0.y)*(x0.y - b0.y)  " + \
                       "                                             +(x0.z - b0.z)*(x0.z - b0.z) " + \
                       "                                             ) " + \
                       "                                         /2 " + \
                       "                                        ) " + \
                       "                                    / " + \
                       "                                    SQRT( x0.ra_err * x0.ra_err + b0.ra_err * b0.ra_err " + \
                       "                                        + x0.decl_err * x0.decl_err + b0.decl_err * b0.decl_err) " + \
                       "                                    < 7.272E-6 " + \
                       "                            ) ", (imgid,imgid))
        conn.commit()
         
        detect_start= time.time()
        query = 12
        """
        cursor.execute("select b0.xtrsrc_id " + \
                       "      ,count(*) as datapoints " + \
                       "      ,sqrt(count(*) * (avg(x2.i_peak * x2.i_peak) - avg(x2.i_peak) * avg(x2.i_peak)) " + \
                       "           / (count(*) - 1) " + \
                       "           ) / avg(x2.i_peak) as mag_var_peak " + \
                       "      ,count(*) * ( avg((x2.i_peak / x2.i_peak_err) * (x2.i_peak / x2.i_peak_err)) " + \
                       "                  - avg(x2.i_peak / (x2.i_peak_err * x2.i_peak_err)) " + \
                       "                    * avg(x2.i_peak / (x2.i_peak_err * x2.i_peak_err)) " + \
                       "                    / avg(1 / (x2.i_peak_err * x2.i_peak_err)) " + \
                       "                  ) " + \
                       "                    / (count(*) - 1) " + \
                       "                    as sig_var_weigthed_peak " + \
                       "  from basesources b0 " + \
                       "      ,extractedsources x2 " + \
                       "      ,images im2 " + \
                       " where b0.ds_id = im2.ds_id " + \
                       "   and im2.imageid = x2.image_id " + \
                       "   and im2.ds_id = %s " + \
                       "   and x2.zone between b0.zone - 1 and b0.zone + 1 " + \
                       "   AND ASIN(SQRT((b0.x - x2.x)*(b0.x - x2.x) + (b0.y - x2.y)*(b0.y - x2.y) + (b0.z - x2.z)*(b0.z - x2.z))/2) " + \
                       "       / " + \
                       "       SQRT( b0.ra_err * b0.ra_err + x2.ra_err * x2.ra_err + b0.decl_err * b0.decl_err + x2.decl_err * x2.decl_err) " + \
                       "       < 7.272E-6 " + \
                       "group by b0.xtrsrc_id " + \
                       "having count(*) > 1 " + \
                       "order by sig_var_weigthed_peak desc ", (dsid,))
        """
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
        iter_end = time.time()
        
        #+===================================================================================================+
        #| iter | imageid | insert_xtr_time | update_base_time | insert_base_time | detect_time | total_time |
        #+===================================================================================================+
        row = str(i) + \
              "," + str(imgid) + \
              "," + str(update_base_start - insert_xtr_start) + \
              "," + str(insert_base_start - update_base_start) + \
              "," + str(detect_start - insert_base_start) + \
              "," + str(iter_end - detect_start) + \
              "," + str(iter_end - insert_xtr_start) + '\n'
        if (i % 100 == 0):
            print row
        
        logf.write(row)

        i += 1
    
    cursor.close()
    logf.close()
    print "Results stored in log file:\n", lf
except db.Error, e:
    logging.warn("Failed on query nr %s reason: %s " % (query, e))
    logf.write("Failed on query nr %s reason: %s " % (query, e))
    logf.close()
    logging.debug("Failed query nr: %s, reason: %s" % (query, e))

