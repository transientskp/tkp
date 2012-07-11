#
# LOFAR Transients Key Project
#

# Python standard library
import logging
import os
# Other external libraries
from datetime import datetime
import monetdb.sql as db

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

def extractedsourcesInImage(conn, image_id, dirname, icolor='magenta'):
    """
    Create a region file that contains all the extracted
    sources in the specified image.
    """
    try:
        outfile = dirname + '/xtrsrc_' + datetime.now().strftime('%Y%m%d-%H%M') + '_img' + str(image_id) + '.reg'  
        if os.path.isfile(outfile):
            os.remove(outfile)
        
        regfile = open(outfile,'w')
        regfile.write('# Region file format: DS9 version 4.1\n')
        
        cursor = conn.cursor()
        query = """\
        SELECT x0.id
              ,ra
              ,decl
              ,ra_err/2
              ,decl_err/2
              ,url
          FROM extractedsource x0
              ,image
         WHERE image.id = %s
           AND x0.image = image.id
        """
        cursor.execute(query, (image_id,))
        results = zip(*cursor.fetchall())
        cursor.close()
        
        if len(results) != 0:
            xtrsrcid = results[0]
            ra = results[1]
            decl = results[2]
            width = results[3]
            height = results[4]
            url = results[5]
        if len(results) != 0:
            regfile.write('# Filename: %s \n' % (url[0],))
            regfile.write('global color=%s dashlist=8 3 width=1 font="helvetica 10 normal roman" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1\n' % (icolor,))
            regfile.write('fk5\n')
            for i in range(len(xtrsrcid)):
                # region file format: box(ra,decl,width,height,angle)
                row = "box(" + str(ra[i]) + ", " + str(decl[i]) + ", " + str(width[i]) + "\", " + str(height[i]) + "\", " + "0.0) # color=" + icolor + " text={" + str(xtrsrcid[i]) + "}\n"
                regfile.write(row)
        regfile.close()
            
        return outfile
    except db.Error, e:
        logging.warn("Failed on Query %s \nfor reason: %s" % (query, e))
        raise
    
def runcatInDataset(conn, dataset_id, dirname, icolor='yellow'):
    """
    Create a region file that contains all the extracted
    sources in the specified image.
    """
    try:
        outfile = dirname + '/runcat_' + datetime.now().strftime('%Y%m%d-%H%M') + '_ds_' + str(dataset_id) + '.reg'  
        if os.path.isfile(outfile):
            os.remove(outfile)
        
        regfile = open(outfile,'w')
        regfile.write('# Region file format: DS9 version 4.1\n')
        
        cursor = conn.cursor()
        query = """\
        SELECT id
              ,wm_ra
              ,wm_decl
              ,wm_ra_err/2
              ,wm_decl_err/2
          FROM runningcatalog
         WHERE dataset = %s
        """
        cursor.execute(query, (dataset_id,))
        results = zip(*cursor.fetchall())
        cursor.close()
        
        if len(results) != 0:
            runcat = results[0]
            ra = results[1]
            decl = results[2]
            width = results[3]
            height = results[4]
        if len(results) != 0:
            regfile.write('# Filename: \n')
            regfile.write('global color=%s dashlist=8 3 width=1 font="helvetica 10 normal roman" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1\n' % (icolor,))
            regfile.write('fk5\n')
            for i in range(len(runcat)):
                # region file format: box(ra,decl,width,height,angle)
                row = "box(" + str(ra[i]) + ", " + str(decl[i]) + ", " + str(width[i]) + "\", " + str(height[i]) + "\", " + "0.0) # color=" + icolor + " text={" + str(runcat[i]) + "}\n"
                regfile.write(row)
        regfile.close()
            
        return outfile
    except db.Error, e:
        logging.warn("Failed on Query %s \nfor reason: %s" % (query, e))
        raise
    
def assoccatsourcesInImage(conn, image_id, dirname, icolor='yellow'):
    """
    Create a region file that contains all the associated cataloged
    sources with the extracted sources in the specified image.
    """
    try:
        outfile = dirname + '/assoccat_' + datetime.now().strftime('%Y%m%d-%H%M') + '_img' + str(image_id) + '.reg'  
        if os.path.isfile(outfile):
            os.remove(outfile)
        
        regfile = open(outfile,'w')
        regfile.write('# Region file format: DS9 version 4.1\n')
        
        cursor = conn.cursor()
        query = """\
        SELECT assoc_catsrc_id
              ,ra
              ,decl
              ,ra_err/2
              ,decl_err/2
              ,url 
          FROM assoccatsources
              ,extractedsource
              ,images 
         WHERE image_id = %s
           AND image_id = imageid 
           AND xtrsrc_id = xtrsrcid
        """
        cursor.execute(query, (image_id,))
        results = zip(*cursor.fetchall())
        cursor.close()
        
        if len(results) != 0:
            assoc_catsrc_id = results[0]
            ra = results[1]
            decl = results[2]
            width = results[3]
            height = results[4]
            url = results[5]
        if len(results) != 0:
            regfile.write('# Filename: %s \n' % (url[0],))
            regfile.write('global color=%s dashlist=8 3 width=1 font="helvetica 10 normal roman" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1\n' % (icolor,))
            regfile.write('fk5\n')
            for i in range(len(assoc_catsrc_id)):
                # region file format: box(ra,decl,width,height,angle)
                row = "box(" + str(ra[i]) + ", " + str(decl[i]) + ", " + str(width[i]) + "\", " + str(height[i]) + "\", " + "0.0) # color=" + icolor + " text={" + str(assoc_catsrc_id[i]) + "}\n"
                regfile.write(row)
        regfile.close()
        return outfile
    except db.Error, e:
        logging.warn("Failed on Query %s \nfor reason: %s" % (query, e))
        raise
    
def catsourcesInRegion(conn, image_id, ra_min, ra_max, decl_min, decl_max, dirname, flux_lim=0.001, icolor='red'):
    """
    Create a region file that contains all the associated cataloged
    sources with the extracted sources in the specified image.
    """
    try:    
        outfile = dirname + '/catsrc_' + datetime.now().strftime('%Y%m%d-%H%M') + '_img' + str(image_id) + '.reg'  
        if os.path.isfile(outfile):
            os.remove(outfile)
        
        regfile = open(outfile,'w')
        regfile.write('# Region file format: DS9 version 4.1\n')
        
        cursor = conn.cursor()
        query = """\
        SELECT catsrcid
              ,ra
              ,decl
              ,ra_err/2
              ,decl_err/2
              ,url 
          FROM catalogedsources
              ,images 
         WHERE imageid = %s
           AND ra BETWEEN %s AND %s
           AND decl BETWEEN %s AND %s
           AND i_int_avg > %s
        """
        cursor.execute(query, (image_id, ra_min, ra_max, decl_min, decl_max, flux_lim))
        results = zip(*cursor.fetchall())
        cursor.close()
        
        if len(results) != 0:
            catsrcid = results[0]
            ra = results[1]
            decl = results[2]
            width = results[3]
            height = results[4]
            url = results[5]
        if len(results) != 0:
            regfile.write('# Filename: %s \n' % (url[0],))
            regfile.write('global color=%s dashlist=8 3 width=1 font="helvetica 10 normal roman" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1\n' % (icolor,))
            regfile.write('fk5\n')
            for i in range(len(catsrcid)):
                # region file format: box(ra,decl,width,height,angle)
                row = "box(" + str(ra[i]) + ", " + str(decl[i]) + ", " + str(width[i]) + "\", " + str(height[i]) + "\", " + "0.0) # color=" + icolor + " text={" + str(catsrcid[i]) + "}\n"
                regfile.write(row)
        regfile.close()
        return outfile
    except db.Error, e:
        logging.warn("Failed on Query %s \nfor reason: %s" % (query, e))
        raise
    

def createRegionFileFromRunCat(conn
                              ,dirname
                              ,icolor = 'green'
                              ,dataset = 0
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
                   WHERE dataset = %s
                     AND datapoints > %s
                 ) t 
            INTO %s 
          DELIMITERS ';' 
                    ,'\\n' 
                    ,'' 
        """
        cursor = conn.cursor()
        print "cursor created"
        cursor.execute(sql_copy_into_reg, (icolor, icolor, dataset, datapoints, outfile))
        print "executed"
        cursor.close()
        return outfile
    except db.Error, e:
        logger.warn("Creating region file failed")
        raise

