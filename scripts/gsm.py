import os, errno
import monetdb.sql as db
from monetdb.sql import Error as Error
import logging

db_type = "MonetDB"
db_host = "ldb001"
db_port = 50000
db_dbase = "gsm"
db_user = "gsm"
db_passwd = "msss"
#db_lang = "sql"

conn = db.connect(hostname=db_host \
                ,port=db_port \
                ,database=db_dbase \
                ,username=db_user \
                ,password=db_passwd \
                )

outpath = os.getenv('HOME') + '/bbs'
try:
    os.makedirs(outpath)
except OSError, failure:
    if failure.errno == errno.EEXIST:
        pass
outfile = os.path.join(outpath, 'gsm2bbs.txt')
if os.path.isfile(outfile):
   os.remove(outfile)

# Here we set the catalog constraints:
# You should know that cat_id = 3 => NVSS
# cat_id = 4 => VLSS
# cat_id = 5 => WENSS
cat_id_min = 4 
cat_id_max = 4
# ra and decl both in degrees
ra_min = 50.5
ra_max = 55.5
decl_min = 52
decl_max = 57
# flux [in Jy] above which the sources will be selected
i_min = 0.5

try:
   cursor = conn.cursor()
   # ThIS query concatenates the requested columns per row in a single string in the correct BBS format.
   cursor.execute(#"COPY " + \
                  "SELECT t.line " + \
                  "  FROM (SELECT CAST('#(Name, Type, Ra, Dec, I, Q, U, V, MajorAxis, MinorAxis, Orientation, ReferenceFrequency=\\'60e6\\', SpectralIndexDegree=\\'0\\', SpectralIndex:0=\\'0.0\\', SpectralIndex:1=\\'0.0\\') = format' AS VARCHAR(300)" + \
                  "                   ) AS line " + \
                  "        UNION " + \
                  "        SELECT CAST(CONCAT(t0.catsrcname, CONCAT(',',  " + \
                  "                    CONCAT(t0.src_type, CONCAT(',',  " + \
                  "                    CONCAT(ra2bbshms(t0.ra), CONCAT(',',  " + \
                  "                    CONCAT(decl2bbsdms(t0.decl), CONCAT(',',  " + \
                  "                    CONCAT(t0.i, CONCAT(',',  " + \
                  "                    CONCAT(t0.q, CONCAT(',',  " + \
                  "                    CONCAT(t0.u, CONCAT(',',  " + \
                  "                    CONCAT(t0.v, CONCAT(',',  " + \
                  "                    CONCAT(t0.MajorAxis, CONCAT(',',  " + \
                  "                    CONCAT(t0.MinorAxis, CONCAT(',',  " + \
                  "                    CONCAT(t0.Orientation, CONCAT(',',  " + \
                  "                    CONCAT(t0.ReferenceFrequency, CONCAT(',',  " + \
                  "                    CONCAT(t0.SpectralIndexDegree, CONCAT(',',  " + \
                  "                    CONCAT(t0.SpectralIndex_0, CONCAT(',', " + \
                  "                           t0.SpectralIndex_1)))))))))))))))))))))))))))" + \
                  "                          ) AS VARCHAR(300)) AS line " + \
                  "          FROM (SELECT CAST(TRIM(c1.catsrcname) AS VARCHAR(20)) AS catsrcname " + \
                  "                      ,CASE WHEN c1.pa IS NULL " + \
                  "                            THEN CAST('POINT' AS VARCHAR(20)) " + \
                  "                            ELSE CAST('GAUSSIAN' AS VARCHAR(20)) " + \
                  "                       END AS src_type " + \
                  "                      ,CAST(c1.ra AS VARCHAR(20))  AS ra " + \
                  "                      ,CAST(c1.decl AS VARCHAR(20)) AS decl " + \
                  "                      ,CAST(c1.i_int_avg AS VARCHAR(20)) AS i " + \
                  "                      ,CAST(0 AS VARCHAR(20)) AS q " + \
                  "                      ,CAST(0 AS VARCHAR(20)) AS u " + \
                  "                      ,CAST(0 AS VARCHAR(20)) AS v " + \
                  "                      ,CASE WHEN c1.pa IS NULL " + \
                  "                            THEN CAST('' AS VARCHAR(20)) " + \
                  "                            ELSE CASE WHEN c1.major IS NULL " + \
                  "                                      THEN CAST('' AS VARCHAR(20)) " + \
                  "                                      ELSE CAST(c1.major AS varchar(20)) " + \
                  "                                 END " + \
                  "                       END AS MajorAxis " + \
                  "                      ,CASE WHEN c1.pa IS NULL " + \
                  "                            THEN CAST('' AS VARCHAR(20)) " + \
                  "                            ELSE CASE WHEN c1.minor IS NULL " + \
                  "                                      THEN CAST('' AS VARCHAR(20)) " + \
                  "                                      ELSE CAST(c1.minor AS varchar(20)) " + \
                  "                                 END " + \
                  "                       END AS MinorAxis " + \
                  "                      ,CASE WHEN c1.pa IS NULL " + \
                  "                            THEN CAST('' AS VARCHAR(20)) " + \
                  "                            ELSE CAST(c1.pa AS varchar(20)) " + \
                  "                       END AS Orientation " + \
                  "                      ,CAST(c1.freq_eff AS VARCHAR(20)) AS ReferenceFrequency " + \
                  "                      ,CASE WHEN si.spindx_degree IS NULL " + \
                  "                            THEN CAST('' AS VARCHAR(20)) " + \
                  "                            ELSE CAST(si.spindx_degree AS VARCHAR(20)) " + \
                  "                       END AS SpectralIndexDegree " + \
                  "                      ,CASE WHEN si.spindx_degree IS NULL  " + \
                  "                            THEN CASE WHEN si.c0 IS NULL " + \
                  "                                      THEN CAST(0 AS varchar(20)) " + \
                  "                                      ELSE CAST(si.c0 AS varchar(20)) " + \
                  "                                 END " + \
                  "                            ELSE CASE WHEN si.c0 IS NULL " + \
                  "                                      THEN CAST('' AS varchar(20)) " + \
                  "                                      ELSE CAST(si.c0 AS varchar(20)) " + \
                  "                                 END " + \
                  "                       END AS SpectralIndex_0 " + \
                  "                      ,CASE WHEN si.c1 IS NULL  " + \
                  "                            THEN CAST('' AS varchar(20)) " + \
                  "                            ELSE CAST(si.c1 AS varchar(20)) " + \
                  "                       END AS SpectralIndex_1 " + \
                  "                  FROM catalogedsources c1 " + \
                  "                       LEFT OUTER JOIN spectralindices si ON c1.catsrcid = si.catsrc_id " + \
                  "                 WHERE c1.cat_id BETWEEN %s AND %s " + \
                  "                   AND c1.ra BETWEEN %s AND %s " + \
                  "                   AND c1.decl BETWEEN %s AND %s " + \
                  "                   AND c1.i_int_avg > %s " + \
                  "               ) t0 " + \
                  #"       ) t " + \
                  #"INTO %s " + \
                  #"DELIMITERS ',' " + \
                  #"          ,'\\n' " + \
                  #"          ,'' ", (cat_id_min,cat_id_max, ra_min, ra_max, decl_min, decl_max, i_min, outfile))
                  "       ) t ", (cat_id_min,cat_id_max, ra_min, ra_max, decl_min, decl_max, i_min))
   y = cursor.fetchall()
   cursor.close()
   #print "y:", y

except db.Error, e:
   logging.warn("writeBBSFile %s failed " % (outfile))
   logging.warn("Failed on query in writeBBSFile() for reason: %s " % (e))
   logging.debug("Failed writeBBSFile() select query: %s" % (e))

file = open(outfile,'w')
for i in range(len(y)):
   file.write(y[i][0] + '\n')
file.close()
print "BBS File written in: ", outfile
