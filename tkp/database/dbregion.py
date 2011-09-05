#
# LOFAR Transients Key Project
#

# Python standard library
import logging
import os
# Other external libraries
from datetime import datetime
# Local tkp_lib functionality
#import tkp.database.database as db
import monetdb
import monetdb.sql


HDF5PREAMBLE = """# Region file format: DS9 version 4.0
# Filename: %(filename)s
global color=%(icolor)s font="helvetica 10 normal" select=1 highlite=1 edit=1 move=1 delete=1 include=1 fixed=0 source
fk5
"""

def createRegionFromCat(
    icatname, ira_min, ira_max, idecl_min, idecl_max, conn, dirname, icolor='green', logger=logging.getLogger()
):
    """
    Create a region file for the specified image.
    """
    try:
        outfile = dirname + datetime.now().strftime('%Y%m%d-%H%M') + '_' + str(icatname) + '.reg'  
        if os.path.isfile(outfile):
            os.remove(outfile)
        file = open(outfile,'w')
        file.close()
        os.chmod(outfile,0777)
        cursor = conn.cursor()
        cursor.execute("COPY " + \
                       "SELECT t.line " + \
                       "  FROM (SELECT CAST('# Region file format: DS9 version 4.0' AS VARCHAR(300)) AS line " + \
                       "        UNION " + \
                       "        SELECT CAST('# Filename: ' AS VARCHAR(300)) AS line " + \
                       "        UNION " + \
                       "        SELECT CAST(CONCAT('global color=', CONCAT(%s , ' font=\"helvetica 10 normal\" select=1 highlite=1 edit=1 move=1 delete=1 include=1 fixed=0 source')) AS VARCHAR(300)) AS line " + \
                       "        UNION " + \
                       "        SELECT CAST('fk5' AS VARCHAR(300)) AS line " + \
                       "        UNION " + \
                       "        SELECT CAST(CONCAT('box(', CONCAT(ra, CONCAT(',', CONCAT(decl, CONCAT(',', CONCAT(ra_err/1800, CONCAT(',', CONCAT(decl_err/1800, CONCAT(') #color=', CONCAT(%s, CONCAT(' text={', CONCAT(catsrcid, '}')))))))))))) AS VARCHAR(300)) AS line" + \
                       "          FROM catalogedsources " + \
                       "              ,catalogs " + \
                       "          WHERE cat_id = catid " + \
                       "            AND catname = %s " + \
                       "            AND ra BETWEEN %s " + \
                       "                       AND %s " + \
                       "            AND decl BETWEEN %s " + \
                       "                         AND %s " + \
                       "       ) t " + \
                       "  INTO %s " + \
                       " DELIMITERS ';' " + \
                       "          ,'\\n' " + \
                       "          ,'' ", (icolor, icolor, icatname.strip().upper(), ira_min, ira_max, idecl_min, idecl_max, outfile))
        cursor.close()
        return outfile
    except db.Error, e:
        logger.warn("Creating region file for catalog %s failed: " % (str(icatname)))
        raise
    

def createRegionByImage(
    image_id, conn, dirname, icolor='green', logger=logging.getLogger()
):
    """
    Create a region file for the specified image.
    Be aware that the directory to which the region file is written
    is ugo+xwr
    """
    try:
        outfile = dirname + '/' + datetime.now().strftime('%Y%m%d-%H%M') + '_img' + str(image_id) + '.reg'  
        if os.path.isfile(outfile):
            os.remove(outfile)
        cursor = conn.cursor()
        # region format
        # box(a,b,c,d,e)
        #c&d in arcsec c",d" and e in angle degrees
        query = """\
          SELECT t.line 
            FROM (SELECT '# Region file format: DS9 version 4.0' AS line 
                   UNION
                  SELECT CONCAT('# Filename: ', url) AS line                                       
                    FROM images 
                   WHERE imageid = %s 
                   UNION 
                  SELECT CONCAT('global color=', CONCAT(%s , ' font=\helvetica 10 normal\ select=1 highlite=1 dash=0 edit=1 move=1 delete=1 include=1 fixed=0 source=1')) AS line 
                   UNION 
                  SELECT 'fk5' AS line 
                   UNION 
                  SELECT CONCAT('box(', CONCAT(ra, CONCAT(',', CONCAT(decl, CONCAT(',', CONCAT(ra_err/1800, CONCAT(',', CONCAT(decl_err/1800, CONCAT(') #color=', CONCAT(%s, CONCAT(' text={', CONCAT(xtrsrcid, '}')))))))))))) AS line
                    FROM extractedsources 
                   WHERE image_id = %s 
                 ) t 
        """
        cursor.execute(query, (image_id, icolor, icolor, image_id))
        y = cursor.fetchall()
        regfile = open(outfile,'w')
        for i in range(len(y)):
            regfile.write(str(y[i][0]) + '\n')
        regfile.close()
            
        cursor.close()
        return outfile
    except monetdb.monetdb_exceptions.Error, e:
        logger.warn("Creating region file for image %s failed: " % (str(image_id)))
        raise
    

def createRegionFileFromRunCat(conn
                              ,dirname
                              ,icolor = 'green'
                              ,ds_id = 0
                              ,datapoints = 0
                              ,logger=logging.getLogger()
                              ):
    """
    Create a region file from all the sources in the running catalog.
    """
    try:
        outfile = dirname + 'runcat.' + datetime.now().strftime('%Y%m%d-%H%M') + '.reg'  
        print outfile
        if os.path.isfile(outfile):
            os.remove(outfile)
        print outfile
        file = open(outfile,'w')
        file.close()
        os.chmod(outfile,0777)
        sql_copy_into_reg = """\
          COPY 
          SELECT t.line 
            FROM (SELECT CAST('# Region file format: DS9 version 4.0' AS VARCHAR(300)) AS line 
                  UNION 
                  SELECT CAST('# Filename: run cat sources' AS VARCHAR(300)) AS line 
                  UNION 
                  SELECT CAST(CONCAT('global color='
                        ,CONCAT(%s,' font=\"helvetica 10 normal\" select=1 highlite=1 edit=1 move=1 delete=1 include=1 fixed=0 source')) AS VARCHAR(300)) AS line 
                  UNION 
                  SELECT CAST('fk5' AS VARCHAR(300)) AS line 
                  UNION 
                  SELECT CAST(CONCAT('box('
                        ,CONCAT(ra_avg, CONCAT(','
                        ,CONCAT(decl_avg, CONCAT(','
                        ,CONCAT(ra_err_avg/1800, CONCAT(','
                        ,CONCAT(decl_err_avg/1800
                        ,CONCAT(') #color='
                        ,CONCAT(%s
                        ,CONCAT(' text={'
                        ,CONCAT('R', '}')
                               ))))))))))) AS VARCHAR(300)) AS line
                    FROM runningcatalog 
                   WHERE ds_id = %s
                     AND datapoints > %s
                 ) t 
            INTO %s 
          DELIMITERS ';' 
                    ,'\\n' 
                    ,'' 
        """
        cursor = conn.cursor()
        print "cursor created"
        cursor.execute(sql_copy_into_reg, (icolor, icolor, ds_id, datapoints, outfile))
        print "executed"
        cursor.close()
        return outfile
    except db.Error, e:
        logger.warn("Creating region file failed")
        raise

