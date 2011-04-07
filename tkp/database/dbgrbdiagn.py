#
# LOFAR Transients Key Project
#

# Python standard library
import logging
# Other external libraries
import pylab
from datetime import *
# Local tkp_lib functionality
import tkp.database.database as db
import tkp.database.dbplots as dbplots

def scatter_SoI_X2X(conn,dsid=None,band=None,datapoints=None,pointdist=None,title=None):
    """
    This makes a plot of the sigma over mu's for the associated sources
    (X2X: eXtractedsources <-> eXtractedsources)
    We discriminate between sources having less than half the number of associations 
    (default < 15) and the ones having more than half.
    """
    try:
        if not dsid:
            dsid = 13
        if not band:
            band = 14
        if not datapoints:
            datapoints = 7
        
        if band == 13:
            grbdist = 1800
        if band == 14:
            grbdist = 1000
        elif band == 15:
            grbdist = 660
        elif band == 16:
            grbdist = 300

        if pointdist:
            grbdist = pointdist
        
        cursor = conn.cursor()
        cursor.execute("SELECT t1.xtrsrc_id " + \
                       "      ,COUNT(*) AS datapoints " + \
                       #"      ,1000 * min(t1.i_peak) AS min_i_peak_mJy " + \
                       #"      ,1000 * AVG(t1.i_peak) AS AVG_i_peak_mJy " + \
                       #"      ,1000 * max(t1.i_peak) AS max_i_peak_mJy " + \
                       #"      ,1000 * min(t1.i_int) AS min_i_int_mJy " + \
                       #"      ,1000 * AVG(t1.i_int) AS AVG_i_int_mJy " + \
                       #"      ,1000 * max(t1.i_int) AS max_i_int_mJy " + \
                       #"      ,1000 * AVG(t1.i_int_AVG) AS max_i_int_cat_mJy " + \
                       "      ,SQRT(count(*) * (AVG(t1.i_peak * t1.i_peak) - AVG(t1.i_peak) * AVG(t1.i_peak))/ (count(*)-1))/AVG(t1.i_peak) AS s_over_i_peak " + \
                       "      ,SQRT(count(*) * (AVG(t1.i_int * t1.i_int) - AVG(t1.i_int) * AVG(t1.i_int))/ (count(*)-1))/AVG(t1.i_int) AS s_over_i_int " + \
                       "      ,SQRT(count(*) * sum(t1.nvar_cat) / (count(*) - 1)) / AVG(t1.i_int_AVG) AS s_over_i_cat " + \
                       "      ,avg((t1.i_int / t1.i_int_err) * (t1.i_int / t1.i_int_err)) " + \
                       "       - 2 * avg(t1.i_int) * avg(t1.i_int / (t1.i_int_err * t1.i_int_err)) " + \
                       "       + avg(t1.i_int) * avg(t1.i_int) * avg(1 / (t1.i_int_err * t1.i_int_err)) as chi2 " + \
                       "  FROM (SELECT t0.* " + \
                       "              ,(t0.i_int - t0.i_int_AVG) * (t0.i_int - t0.i_int_AVG) AS nvar_cat " + \
                       "          FROM (SELECT ax1.xtrsrc_id " + \
                       "                      ,ax1.assoc_xtrsrc_id " + \
                       "                      ,ax1.assoc_distance_arcsec " + \
                       "                      ,ax1.assoc_lr " + \
                       "                      ,im2.imageid " + \
                       "                      ,x2.i_peak " + \
                       "                      ,x2.i_int " + \
                       "                      ,x2.i_peak_err " + \
                       "                      ,x2.i_int_err " + \
                       "                      ,x2.ra_err " + \
                       "                      ,x2.decl_err " + \
                       "                      ,im2.url " + \
                       "                      ,ac2.assoc_catsrc_id " + \
                       "                      ,c2.i_int_avg " + \
                       "                      ,3600 * DEGREES(2 * ASIN(SQRT((x2.x - c1.x) * (x2.x - c1.x)+ (x2.y - c1.y) * (x2.y - c1.y)+ (x2.z - c1.z) * (x2.z - c1.z)) / 2) ) as grb_dist" + \
                       "                  FROM assocxtrsources ax1 " + \
                       "                      LEFT OUTER JOIN assoccatsources ac2 ON ax1.assoc_xtrsrc_id = ac2.xtrsrc_id " + \
                       "                      LEFT OUTER JOIN catalogedsources c2 ON c2.catsrcid = ac2.assoc_catsrc_id " + \
                       "                      ,extractedsources x1 " + \
                       "                      ,extractedsources x2 " + \
                       "                      ,images im1 " + \
                       "                      ,images im2 " + \
                       "                      ,catalogedsources c1 " + \
                       "                 WHERE ax1.xtrsrc_id = x1.xtrsrcid " + \
                       "                   AND ax1.assoc_xtrsrc_id = x2.xtrsrcid " + \
                       "                   AND x1.image_id = im1.imageid " + \
                       "                   AND x2.image_id = im2.imageid " + \
                       "                   AND ax1.assoc_lr > -10 " + \
                       "                   AND c1.catsrcid = 2071216 " + \
                       "                   AND (ac2.assoc_lr > -76 " + \
                       "                        OR ac2.assoc_lr IS NULL " + \
                       "                       ) " + \
                       "                   AND im1.ds_id = %s " + \
                       "                   AND im1.band <> 17 " + \
                       "                   AND im2.band = %s " + \
                       "                   AND ax1.assoc_xtrsrc_id NOT IN (10876, 11018, 10543, 13386, 13494, 13206, 13401) " + \
                       "                   AND ax1.assoc_xtrsrc_id NOT IN (13924, 14064, 14149) " + \
                       #"                  sources in band 13 (840MHz) that are excluded due to bad fitting 
                       "                   AND ax1.assoc_xtrsrc_id NOT IN (15272,15449,15542,15704) " + \
                       "                   AND ax1.xtrsrc_id <> 13230 " + \
                       # NOTE: for a source for which an association could be found, we also
                       #       check whether the previous association is valid. If not, we insert
                       #       only the current and the assoc that was valid.
                       #       TODO: this is not necessary when the assoc that could be found has
                       #             multiple previous ids.
                       "                   AND ax1.xtrsrc_id NOT IN (13168,15018,15055,15068,15098,15128) " + \
                       "               ) t0 " + \
                       "         WHERE t0.grb_dist <= %s " + \
                       "       ) t1 " + \
                       "GROUP BY t1.xtrsrc_id " + \
                       "HAVING COUNT(*) >= %s " + \
                       "ORDER BY datapoints ", (dsid,band,grbdist,datapoints))
        y = cursor.fetchall()
        cursor.close()
        
        xtrsrcids = []
        xtrsrcids_upper = []
        xtrsrcids_lower = []
        datapoints = []
        s_over_i_int = []
        chi2 = []
        s_over_i_int_upper = []
        s_over_i_int_lower = []
        
        for i in range(len(y)):
            """
            if (y[i][1] > 15):
                xtrsrcids_upper.append(y[i][0])
                sig_over_mu_upper.append(y[i][5])
            else:
                xtrsrcids_lower.append(y[i][0])
                sig_over_mu_lower.append(y[i][5])
            """
            xtrsrcids.append(y[i][0])
            datapoints.append(y[i][1])
            s_over_i_int.append(y[i][3])
            chi2.append(y[i][5])

        #print "datapoints =",datapoints
        #print "xtrsrcids =",xtrsrcids
        #print "s_over_i_int =",s_over_i_int

        plotfiles=[]
        p = 0
        
        m = -1
        fmt = ['s','o','^','d','>','v','<','d','p','h','8','+','x']

        pylab.figure()
        if (len(xtrsrcids) > 1):
            # we want to plot different symbols per number of datapoints
            idx_start = 0
            dp0 = datapoints[0]
            for i in range(len(xtrsrcids)):
                if datapoints[i] != dp0:
                    #print "xtrsrcids[",idx_start,":",i,"] =",xtrsrcids[idx_start:i]
                    #print "datapoints[",idx_start,":",i,"] =",datapoints[idx_start:i]
                    #print "datapoints[",i," - 1] =",datapoints[i - 1]
                    if m > len(fmt):
                        m = len(fmt) - 1
                    else:
                        m = m + 1
                    pylab.errorbar(xtrsrcids[idx_start:i], s_over_i_int[idx_start:i] \
                                  ,fmt=fmt[m],label=str(datapoints[i-1]) + ' datapoints')
                    dp0 = datapoints[i]
                    idx_start = i
            #print "xtrsrcids[",idx_start,":] =",xtrsrcids[idx_start:]
            #print "datapoints[",idx_start,":] =",datapoints[idx_start:]
            #print "datapoints[",i," - 1] =",datapoints[i - 1]
            if m > len(fmt):
                m = len(fmt) - 1
            else:
                m = m + 1
            pylab.errorbar(xtrsrcids[idx_start:], s_over_i_int[idx_start:] \
                          ,fmt=fmt[m], label=str(datapoints[i]) + ' datapoints')
        
        pylab.grid(True)
        pylab.xlabel('extracted source ID')
        pylab.ylabel(r'Variability Index, $s / \bar{I_{\nu}}$')
        if max(s_over_i_int) < 1.0:
            pylab.ylim(0,1)
        pylab.legend(numpoints=1,loc='best')
        if title:
            pylab.title(r'Variability Index for associated sources at 1.4 GHz')
        plotfiles.append('ts_over_i_band' + str(band) + '_dsid' + str(dsid) + '.eps')
        pylab.savefig(plotfiles[p],dpi=600)
        
        p += 1
        m = -1
        fmt = ['s','o','^','d','>','v','<','d','p','h','8','+','x']

        pylab.figure()
        if (len(xtrsrcids) > 1):
            # we want to plot different symbols per number of datapoints
            idx_start = 0
            dp0 = datapoints[0]
            for i in range(len(xtrsrcids)):
                if datapoints[i] != dp0:
                    if m > len(fmt):
                        m = len(fmt) - 1
                    else:
                        m = m + 1
                    pylab.errorbar(xtrsrcids[idx_start:i], chi2[idx_start:i] \
                                  ,fmt=fmt[m],label=str(datapoints[i-1]) + ' datapoints')
                    dp0 = datapoints[i]
                    idx_start = i
            if m > len(fmt):
                m = len(fmt) - 1
            else:
                m = m + 1
            pylab.errorbar(xtrsrcids[idx_start:], chi2[idx_start:] \
                          ,fmt=fmt[m], label=str(datapoints[i]) + ' datapoints')
        
        pylab.grid(True)
        pylab.xlabel('extracted source ID')
        pylab.ylabel(r'Variability Index, $\chi^2$')
        #if max(s_over_i_int) < 1.0:
        #    pylab.ylim(0,1)
        pylab.legend(numpoints=1,loc='best')
        if title:
            pylab.title(r'Variability Index for associated sources at 1.4 GHz')
        plotfiles.append('chi2_band' + str(band) + '_dsid' + str(dsid) + '.eps')
        pylab.savefig(plotfiles[p],dpi=600)

        return plotfiles
    except db.Error, e:
        logging.warn("scatter_SoI_X2X for dsid %s failed " % (str(dsid)))
        logging.warn("Failed on query in scatter_SoI_X2X for reason: %s " % (e))
        logging.debug("Failed scatter_SoI_X2X plotquery: %s" % (e))

