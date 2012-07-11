#
# LOFAR Transients Key Project
#

# Python standard library
import logging
# Local tkp_lib functionality
import tkp.database.database as db

def brightestInField(conn,icatname,itheta,ira,idecl,logger=logging.getLogger()):

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT catsrcid " + \
                       "      ,ra " + \
                       "      ,decl " + \
                       "      ,freq_eff " + \
                       "      ,i_int_avg " + \
                       "      ,i_int_avg_err " + \
                       "      ,dist_arcsec " + \
                       "  FROM getNeighborBrightestInCat(%s " + \
                       "                                ,%s " + \
                       "                                ,%s " + \
                       "                                ,%s " + \
                       "                                ) ", (icatname, itheta, ira, idecl))
        y = cursor.fetchall()
        print y
        cursor.close()
    except db.Error, e:
        logger.warn("Selecting %s sources for field %s, %s failed: " % (icatname,ira,idecl))
        logger.warn("Failed for reason %s : " % (e))
        logger.debug("Failed creating region file: %s" % (e))

def printBrightestSourceInField(conn,iter,cat_id,irahms,idecldms,itheta,logger=logging.getLogger()):

    try:
        izoneheight = 1.

        cursor = conn.cursor()
        cursor.execute("SELECT catsrcid " + \
                       "       ,orig_catsrcid " + \
                       "       ,ra " + \
                       "       ,decl " + \
                       "       ,ra2hms(ra) " + \
                       "       ,decl2dms(decl) " + \
                       "       ,i_int_avg " + \
                       "       ,i_int_avg_err " + \
                       "       ,3600 * DEGREES(2 * ASIN(SQRT((COS(radians(c1.decl)) * COS(radians(c1.ra)) - COS(radians(decl2deg(%s))) * COS(radians(ra2deg(%s)))) " + \
                       "                                     * (COS(radians(c1.decl)) * COS(radians(c1.ra)) - COS(radians(decl2deg(%s))) * COS(radians(ra2deg(%s)))) " + \
                       "                                    + (COS(radians(c1.decl)) * SIN(radians(c1.ra)) - COS(radians(decl2deg(%s))) * SIN(radians(ra2deg(%s)))) " + \
                       "                                      * (COS(radians(c1.decl)) * SIN(radians(c1.ra)) - COS(radians(decl2deg(%s))) * SIN(radians(ra2deg(%s)))) " + \
                       "                                    + (SIN(radians(c1.decl)) - SIN(radians(decl2deg(%s)))) * (SIN(radians(c1.decl)) - SIN(radians(decl2deg(%s)))) " + \
                       "                                    ) / 2)) as dist_arcsec" + \
                       "     FROM catalogedsources c1 " + \
                       "    WHERE c1.cat_id = 4 " + \
                       "      AND c1.x * COS(radians(decl2deg(%s))) * COS(radians(ra2deg(%s))) " + \
                       "          + c1.y * COS(radians(decl2deg(%s))) * SIN(radians(ra2deg(%s))) " + \
                       "          + c1.z * SIN(radians(decl2deg(%s))) > COS(RADIANS(%s)) " + \
                       "      AND c1.zone BETWEEN CAST(FLOOR((decl2deg(%s) - %s) / %s) AS INTEGER) " + \
                       "                      AND CAST(FLOOR((decl2deg(%s) + %s) / %s) AS INTEGER) " + \
                       "      AND c1.ra BETWEEN ra2deg(%s) - alpha(%s, decl2deg(%s)) " + \
                       "                    AND ra2deg(%s) + alpha(%s, decl2deg(%s)) " + \
                       "      AND c1.decl BETWEEN decl2deg(%s) - %s " + \
                       "                      AND decl2deg(%s) + %s " + \
                       " ORDER BY i_int_avg ", (idecldms,irahms,idecldms,irahms,idecldms,irahms,idecldms,irahms,idecldms,idecldms,idecldms, irahms,idecldms,irahms,idecldms,itheta,idecldms,itheta,izoneheight,idecldms,itheta,izoneheight,irahms,itheta,idecldms,irahms,itheta,idecldms,idecldms,itheta,idecldms,itheta))
                       #" ORDER BY i_int_avg ", (idecldms, irahms,idecldms,irahms,idecldms,itheta,idecldms,itheta,izoneheight,idecldms,itheta,izoneheight,irahms,itheta,idecldms,irahms,itheta,idecldms,idecldms,itheta,idecldms,itheta))
        y = cursor.fetchall()
        fl = []
        for i in range(len(y)):
            fl.append(y[i][6])
            print iter, y[i] 
        #print iter, max(fl)
        cursor.close()
    except db.Error, e:
        logger.warn("Creating region file for image %s failed: " % (irahms))
        logger.warn("Failed for reason %s : " % (e))
        logger.debug("Failed creating region file: %s" % (e))


