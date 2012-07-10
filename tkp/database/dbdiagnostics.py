#
# LOFAR Transients Key Project
#

# Python standard library
import logging
import os
# Other external libraries
import pylab
import matplotlib.mlab
from datetime import *
# Local tkp_lib functionality
import tkp.database.database as db
import tkp.database.dbplots as dbplots


def scatterWenssNvssSigmaOverMuX2X(dsid,conn):
    """
    This makes a plot of the sigma over mu's for the associated sources
    (X2X: eXtractedsources <-> eXtractedsources)
    We discriminate between sources having less than half the number of associations 
    (default < 15) and the ones having more than half.
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT ax2.xtrsrc_id " + \
                       "      ,count(*) as datapoints " + \
                       "      ,1000 * min(x2.i_int) as min_i_int_mJy " + \
                       "      ,1000 * avg(x2.i_int) as avg_i_int_mJy " + \
                       "      ,1000 * max(x2.i_int) as max_i_int_mJy " + \
                       "      ,sqrt(count(*) * (avg(x2.i_int * x2.i_int) - avg(x2.i_int) * avg(x2.i_int))/ (count(*)-1))/avg(x2.i_int) as sigma_over_mu " + \
                       "  FROM assocxtrsources ax2 " + \
                       "      ,extractedsource x1 " + \
                       "      ,extractedsource x2 " + \
                       "      ,images im1 " + \
                       "      ,images im2 " + \
                       " WHERE ax2.xtrsrc_id = x1.xtrsrcid " + \
                       "   AND ax2.assoc_xtrsrc_id = x2.xtrsrcid " + \
                       "   AND x1.image = im1.imageid " + \
                       "   AND x2.image = im2.imageid " + \
                       "   AND im1.dataset = im2.dataset " + \
                       "   AND im1.dataset = %s " + \
                       "   AND im1.band = 14 " + \
                       "   AND im1.band = im2.band " + \
                       "GROUP BY ax2.xtrsrc_id " + \
                       "HAVING COUNT(*) = 10 " + \
                       "ORDER BY datapoints " + \
                       "        ,ax2.xtrsrc_id ", (dsid,))
        y = cursor.fetchall()
        cursor.close()
        
        xtrsrcids_upper = []
        xtrsrcids_lower = []
        sig_over_mu_upper = []
        sig_over_mu_lower = []
        
        for i in range(len(y)):
            if (y[i][1] > 15):
                xtrsrcids_upper.append(y[i][0])
                sig_over_mu_upper.append(y[i][5])
            else:
                xtrsrcids_lower.append(y[i][0])
                sig_over_mu_lower.append(y[i][5])
        
        plotfiles=[]
        p = 0
        fig = pylab.figure()
        ax1 = fig.add_subplot(111)
        ax1.set_xlabel('xtrsrcid')
        ax1.set_ylabel(r'$s / \bar{x}$', color='r')
        for tl in ax1.get_yticklabels():
            tl.set_color('r')
        if (len(xtrsrcids_upper) > 1):
            ax1.scatter(xtrsrcids_upper, sig_over_mu_upper, color='r', marker='o',label='gt 15')
        if (len(xtrsrcids_lower) > 1):
            #print "len(xtrsrcids_lower):",len(xtrsrcids_lower)
            #print "xtrsrcids_lower:",xtrsrcids_lower
            #print "sig_over_mu_lower:",sig_over_mu_lower
            ax1.scatter(xtrsrcids_lower, sig_over_mu_lower, color='b', marker='s',label='le 15')
        ax1.grid(True)
        #pylab.legend(numpoints=1,loc='best')
        pylab.title(r'Variability, $s / \bar{x}$, for extracted sources ' + \
                    'in dataset ' + str(dsid))
        plotfiles.append('sigmaovermu_dsid' + str(dsid) + '.eps')
        pylab.savefig(plotfiles[p],dpi=600)
        
        return plotfiles
    except db.Error, e:
        logging.warn("scatterSigmaOverMuX2X for dsid %s failed " % (str(dsid)))
        raise


def plotWenssNvssSpIdxFig7(dsid,catid,conn):
    """
    This makes a spectral index histogram of the WENSS-NVSS assocs
    with assoc_lr > 3 
    """
    try:
        cursor = conn.cursor()
        """
        ~10000 records, this takes to long in python, so we
        bin it in the query itself
        cursor.execute("select log10(x1.i_int / c1.i_int_avg) / log10(c1.freq_eff / im1.freq_eff) " + \
                       "  from assoccatsources ac1 " + \
                       "      ,catalogedsources c1 " + \
                       "      ,extractedsource x1 " + \
                       "      ,images im1 " + \
                       " where assoc_catsrc_id = catsrcid " + \
                       "   and xtrsrc_id = xtrsrcid " + \
                       "   and image_id = imageid " + \
                       "   and dataset = %s " + \
                       "   and cat_id = %s " + \
                       "   and assoc_lr > 3 ", (dsid,catid)) 
        """
        cursor.execute("select cnt " + \
                       "      ,cast(sp_index_bin_nr as double) / 20 as sp_index_bin " + \
                       "      ,sp_index_bin_nr " + \
                       "  from (select count(*) as cnt " + \
                       "              ,cast(1 + floor(20 * log10(x1.i_int / c1.i_int_avg) / log10(c1.freq_eff / im1.freq_eff)) as integer) as sp_index_bin_nr " + \
                       "          from assoccatsources ac1 " + \
                       "              ,catalogedsources c1 " + \
                       "              ,extractedsource x1 " + \
                       "              ,images im1 " + \
                       "         where assoc_catsrc_id = catsrcid " + \
                       "           and xtrsrc_id = xtrsrcid " + \
                       "           and image_id = imageid " + \
                       "           and dataset = %s " + \
                       "           and cat_id = %s " + \
                       "           and assoc_lr > 3 " + \
                       "        group by sp_index_bin_nr " + \
                       "       ) t " + \
                       "order by sp_index_bin_nr ", (dsid,catid))
        y = cursor.fetchall()
        cursor.close()
        
        cnt = []
        spindex_bin = []
        spindex_bin_nr = []
        
        for i in range(len(y)):
            cnt.append(y[i][0])
            spindex_bin.append(y[i][1])
            spindex_bin_nr.append(y[i][2])
        


        plotfiles=[]
        p = 0
        fig = pylab.figure()
        ax1 = fig.add_subplot(111)
        ax1.set_xlabel(r'Spectral index')
        ax1.set_ylabel('N')
        
        ax1.semilogy(spindex_bin, cnt, 'b-')
        ax1.grid(True)
        
        plotfiles.append('SAI_spectralindices_wenssnvss.eps')
        pylab.savefig(plotfiles[p],dpi=600)
        
        return plotfiles
    except db.Error, e:
        logging.warn("plotWenssNvssSpIdxFig7() for dsid %s failed " % (str(dsid)))
        raise
    

def plotWenssNvssFig6(dsid,catid,conn):
    """
    The input arguments are actually dummies because we know
    the SF are in dataset = 2, and the BG dataset between 3 and 10.
    This makes a reliability plot for the WENSS-NVSS assocs
    """
    try:
        cursor = conn.cursor()
        cursor.execute("select count(*) as npairs " + \
                       "      ,CAST(bin_lr_nr AS DOUBLE) / 2 AS bin_lr " + \
                       "      ,bin_lr_nr " + \
                       "      ,avg(reliab) " + \
                       "  from (select t2.xtrsrc_id " + \
                       "              ,t2.assoc_catsrc_id " + \
                       "              ,CAST(1 + FLOOR(2 * t2.assoc_lr) AS INTEGER) as bin_lr_nr " + \
                       "              ,t2.assoc_lr " + \
                       "              ,t2.cnt_sf " + \
                       "              ,t2.cnt_bg " + \
                       "              ,(t2.cnt_sf - t2.cnt_bg / 8) / t2.cnt_sf as reliab " + \
                       "          from (select t1.xtrsrc_id as xtrsrc_id " + \
                       "                      ,t1.assoc_catsrc_id as assoc_catsrc_id " + \
                       "                      ,t1.assoc_lr as assoc_lr " + \
                       "                      ,getCountLogLRbin_CatSF(2,(t1.assoc_lr - 0.25),(t1.assoc_lr + 0.25)) as cnt_sf " + \
                       "                      ,getCountLogLRbin_CatBG(3,10,(t1.assoc_lr - 0.25),(t1.assoc_lr + 0.25)) as cnt_bg " + \
                       "                  from (select ac1.xtrsrc_id as xtrsrc_id " + \
                       "                              ,ac1.assoc_catsrc_id as assoc_catsrc_id " + \
                       "                              ,ac1.assoc_lr as assoc_lr " + \
                       "                          from assoccatsources ac1 " + \
                       "                              ,extractedsource x1 " + \
                       "                              ,images im1 " + \
                       "                              ,catalogedsources c1 " + \
                       "                         where ac1.xtrsrc_id = x1.xtrsrcid " + \
                       "                           and x1.image = im1.imageid " + \
                       "                           and im1.dataset = %s " + \
                       "                           and ac1.assoc_catsrc_id = c1.catsrcid " + \
                       "                           and c1.cat_id = %s " + \
                       "                           and ac1.assoc_lr > -300 " + \
                       "                       ) t1 " + \
                       "               ) t2 " + \
                       "       ) t3 " + \
                       "group by bin_lr_nr " + \
                       "order by bin_lr_nr ", (dsid,catid))
        """
        cursor.execute("select count(*) as npairs " + \
                       "      ,CAST(bin_lr_nr AS DOUBLE) / 2 AS bin_lr " + \
                       "      ,bin_lr_nr " + \
                       "      ,avg(reliab) " + \
                       "  from aux_assocs_wenss " + \
                       "group by bin_lr_nr " + \
                       "order by bin_lr_nr")
        """
        y = cursor.fetchall()
        cursor.close()
        
        npairs = []
        bin_lr = []
        bin_lr_nr = []
        reliab = []
        
        for i in range(len(y)):
            npairs.append(y[i][0])
            bin_lr.append(y[i][1])
            bin_lr_nr.append(y[i][2])
            reliab.append(y[i][3])
        
        plotfiles=[]
        p = 0
        fig = pylab.figure()
        ax1 = fig.add_subplot(111)
        ax1.set_xlabel(r'$\log LR$')
        ax1.set_ylabel('Reliability')
        
        ax1.plot(bin_lr, reliab, 'b-')
        ax1.grid(True)
        
        plotfiles.append('SAI_reliability_wenssnvss.eps')
        pylab.savefig(plotfiles[p],dpi=600)
        
        return plotfiles
    except db.Error, e:
        logging.warn("plotWenssNvssFig6() for dsid %s failed " % (str(dsid)))
        raise
    

def plotWenssNvssFig5(dsid,dsid_min,dsid_max,catid,conn):
    """
    This makes a x-y, logLR-N/field step plot of the source and background fields.
    The difference between the two is also plotted as to make clear
    where a cautoff between the two exists
    SF count(*) = 288,561 (all assocs: NVSS and VLSS)
                = 259,114 (all assocs w/ NVSS) 
                =  29,447 (all assocs w/ VLSS) 
                =   2,811 (no assocs at all) 
                = 245,138 (all assocs w/ NVSS and assoc_lr > -100)
                   13,976 (all assocs w/ NVSS and assoc_lr <= -100)
    BG count(*) = 206,131 (all assocs: NVSS and VLSS)
                = 196,842 (all assocs from all fields w/ NVSS) div by 8 => 
                =  24,605 per field
                = 150,529 (all assocs w/ NVSS and assoc_lr > -100) =>
                =  18,816 per field
                   46,313 (all assocs w/ NVSS and assoc_lr <= -100) =>
                    5,789 per field

    """
    try:
        cursor = conn.cursor()
        # --- Source Field ----
        cursor.execute("SELECT * " + \
                       "  FROM (SELECT npairs " + \
                       "              ,CAST(bin_lr_nr AS DOUBLE)/2 AS bin_lr " + \
                       "              ,bin_lr_nr " + \
                       "          FROM (SELECT COUNT(*) AS npairs " + \
                       "                      ,CAST(1 + floor(2 * assoc_lr) AS INTEGER) AS bin_lr_nr " + \
                       "                  FROM assoccatsources " + \
                       "                      ,extractedsource " + \
                       "                      ,images " + \
                       "                      ,lsm " + \
                       "                  WHERE xtrsrc_id = xtrsrcid " + \
                       "                    AND image_id = imageid " + \
                       "                    AND dataset = %s " + \
                       "                    AND assoc_catsrc_id = lsmid " + \
                       "                    AND cat_id = %s " + \
                       "                    AND assoc_lr > -100 " + \
                       "                GROUP BY bin_lr_nr " + \
                       "               ) t " + \
                       "       ) t2 " + \
                       "ORDER BY t2.bin_lr ", (dsid,catid))
        sf_y = cursor.fetchall()
        
        # --- Background Fields ----
        cursor.execute("SELECT * " + \
                       "  FROM (SELECT npairs " + \
                       "              ,CAST(bin_lr_nr AS DOUBLE)/2 AS bin_lr " + \
                       "              ,bin_lr_nr " + \
                       "          FROM (SELECT COUNT(*) AS npairs " + \
                       "                      ,CAST(1 + floor(2 * assoc_lr) AS INTEGER) AS bin_lr_nr " + \
                       "                  FROM assoccatsources " + \
                       "                      ,extractedsource " + \
                       "                      ,images " + \
                       "                      ,lsm " + \
                       "                  WHERE xtrsrc_id = xtrsrcid " + \
                       "                    AND image_id = imageid " + \
                       "                    AND dataset >= %s " + \
                       "                    AND dataset <= %s " + \
                       "                    AND assoc_catsrc_id = lsmid " + \
                       "                    AND cat_id = %s " + \
                       "                    AND assoc_lr > -100 " + \
                       "                GROUP BY bin_lr_nr " + \
                       "               ) t " + \
                       "       ) t2 " + \
                       "ORDER BY t2.bin_lr ", (dsid_min,dsid_max,catid))
        bg_y = cursor.fetchall()
        cursor.close()
        
        sf_npairs = []
        sf_bin_lr = []
        sf_bin_lr_nr = []
        
        bg_npairs = []
        bg_bin_lr = []
        bg_bin_lr_nr = []
        
        sum_sf_npairs = []
        sum_bg_npairs = []
        diff_npairs = []
       
        reliab = []
       
        print "len(sf_y) = ", len(sf_y), "\nlen(bg_y) = ", len(bg_y)
        if (len(sf_y) != len(bg_y)):
            print "len(sf_y) = ", len(sf_y), " len(bg_y) = ", len(bg_y)

        sf_npairs0 = 13976. + 2811.
        # all wenss-nvss assocs + all sources that could not be associated
        sf_total = 259114. + 2811.
        for i in range(len(sf_y)):
            if (sf_y[i][2] != bg_y[i][2]):
                print "i = ", i, " sf_y[i][2] = ", sf_y[i][2], " bg_y[i][2] = ", bg_y[i][2]
                break
            
            #sf_npairs.append(sf_y[i][0]/288561.)
            sf_npairs.append(sf_y[i][0] / sf_total)
            #sf_npairs.append(sf_y[i][0]/245138.)
            sf_bin_lr.append(sf_y[i][1])
            sf_bin_lr_nr.append(sf_y[i][2])
            if i > 0:
                sum_sf_npairs.append(sum_sf_npairs[i - 1] + sf_npairs[i])
            else:
                sum_sf_npairs.append((sf_npairs0 / sf_total) + sf_npairs[i])

        bg_npairs0 = 46313. + 1649204.
        bg_total = 196842. + 1649204.
        for i in range(len(bg_y)):
            #bg_npairs.append(bg_y[i][0]/206131.)
            bg_npairs.append(bg_y[i][0] / bg_total)
            #bg_npairs.append(bg_y[i][0]/150529.)
            #bg_npairs.append(bg_y[i][0]/18816.)
            bg_bin_lr.append(bg_y[i][1])
            bg_bin_lr_nr.append(bg_y[i][2])
            if i > 0:
                sum_bg_npairs.append(sum_bg_npairs[i - 1] + bg_npairs[i])
            else:
                sum_bg_npairs.append((bg_npairs0 / bg_total) + bg_npairs[i])
            
        for i in range(len(bg_y)):
            #diff_npairs.append(1. - float(sum_bg_npairs[i]) / float(sum_sf_npairs[i]))
            #diff_npairs.append(1. - float(bg_npairs[i]) / (8 * float(sf_npairs[i])))
            """
            srcfld = sf_y[i][0]
            bgfld = bg_y[i][0]
            j = 1
            while srcfld < 1000:
                if (i - j) < 0:
                    srcfld = srcfld + sf_y[i + j][0]
                    bgfld = bgfld + bg_y[i][0]
                else:
                    srcfld = srcfld + sf_y[i - j][0] + sf_y[i + j][0]
                    bgfld = bgfld + bg_y[i - j][0] + bg_y[i + j][0]
                j += 1
            #rel = (float(sf_y[i][0]) - float(bg_y[i][0]) / 8.) / float(sf_y[i][0]) 
            #rel = (srcfld - bgfld / 8.) / srcfld
                  #"; j = ", j, \
                  #"; srcfld = ", srcfld, \
                  #"; bgfld = ", bgfld, \
                  #"  sum_sf_npairs[",i,"] = ", sum_sf_npairs[i], \
                  #"  sum_bg_npairs[",i,"] = ", sum_bg_npairs[i], \
            """
            #rel = 1. - (float(bg_npairs[i]) / 8.) / float(sf_npairs[i])      
            #rel = float(sum_sf_npairs[i]) / float(sum_bg_npairs[i])      
            rel = float(sf_npairs[i]) / float(bg_npairs[i])      
            #rel = (float(sf_npairs[i]) - float(bg_npairs[i])) / float(sf_npairs[i])      
            print "  sf_y[",i,"][0] = ", sf_y[i][0], \
                  "; bg_y[",i,"][0] = ", bg_y[i][0], \
                  "  sf_npairs[",i,"] = ", sf_npairs[i], \
                  "  bg_npairs[",i,"] = ", bg_npairs[i], \
                  "; rel = ", rel 
            # inspection reveals that at this i, R can be set to zero
            #if i < 174:
            #    rel = 0
            reliab.append(rel)
        
        xwidth = 1./len(sf_bin_lr)
        xcentr = pylab.arange(0,1,xwidth)
        
        #print "reliab=",reliab
        plotfiles=[]
        p = 0
        fig = pylab.figure()
        ax1 = fig.add_subplot(211)
        ax1.set_xlabel(r'$\log LR$')
        #ax1.set_ylabel('Cum. number of associations per Field')
        ax1.set_ylabel(r'$n(LR)$')
        
        #ax1.plot(sf_bin_lr, sum_sf_npairs, 'b-', label='SF avg')
        #ax1.plot(bg_bin_lr, sum_bg_npairs, 'k--', label='BG avg')
        ax1.semilogy(sf_bin_lr, sf_npairs, 'b-', label='Source')
        ax1.semilogy(bg_bin_lr, bg_npairs, 'k--', label='Background')
        #ax1.plot(sf_bin_lr, sf_npairs, 'b-', label='SF avg')
        #ax1.plot(bg_bin_lr, bg_npairs, 'k--', label='BG avg')
        pylab.legend(numpoints=1,loc='upper left')
        ax1.grid(True)
        
        """
        ax2 = ax1.twinx()
        ax2.set_ylabel('Reliability of LR, R(LR)', color='r')
        for tl in ax2.get_yticklabels():
            tl.set_color('r')
        #ax2.plot(sf_bin_lr, diff_npairs, 'r-', linewidth=3, label='Diff.')
        ax2.plot(sf_bin_lr, reliab, 'r-', linewidth=3, label='Reliab.')
        """
        ax2 = fig.add_subplot(212)
        ax2.set_xlabel(r'$\log LR$')
        ax2.set_ylabel(r'$n_{SF}(LR)/n_{BG}(LR)$')
        #ax2.plot(sf_bin_lr, reliab, 'r-', linewidth=3, label='Reliab.')
        ax2.semilogy(sf_bin_lr, reliab, 'r-', linewidth=3, label='Reliab.')
        #t = pylab.arange(-100.0,4.5,0.5)
        #f = 2. + 1. * pylab.exp(-(0. - t))
        #ax2.semilogy(t, f, 'b--', linewidth=3, label='Fit')
        #pylab.legend(numpoints=1,loc='upper left')
        pylab.xlim(-20.0,5.0)
        #pylab.ylim(0.6,1.0)
        
        ax2.grid(True)
        
        plotfiles.append('SAI_cumul_distr_lr_npairs_wenssnvss.eps')
        pylab.savefig(plotfiles[p],dpi=600)
        
        return plotfiles
    except db.Error, e:
        logging.warn("plotWenssNvssFig5() for dsid %s failed " % (str(dsid)))
        raise
    

def plotWenssNvssDistDistrib(dsid,dsid_min,dsid_max,catid,conn):
    """
    This makes a x-y, r-N/field step plot of the source and background fields.
    The difference between the two is also plotted as to make clear
    where a cautoff between the two exists
    SF count(*) = 259,114 (all assocs w/ NVSS)
                = 245,138 (all assocs w/ NVSS and assoc_lr > -100)
    BG count(*) = 196,842 (all assocs from all fields w/ NVSS) div by 8 => 
                =  24,605 per field
                = 150,529 (all assocs w/ NVSS and assoc_lr > -100) =>
                =  18,816 per field
    """
    try:
        cursor = conn.cursor()
        # --- Source Field ----
        cursor.execute("SELECT * " + \
                       "  FROM (SELECT nsources " + \
                       "              ,avg_dist_arcsec " + \
                       "              ,CAST(bin_dist_nr AS DOUBLE)/10 AS bin_dist " + \
                       "              ,bin_dist_nr " + \
                       "          FROM (SELECT COUNT(*) AS nsources " + \
                       "                      ,AVG(assoc_distance_arcsec) AS avg_dist_arcsec " + \
                       "                      ,CAST(1 + floor(10 * assoc_distance_arcsec) AS INTEGER) AS bin_dist_nr " + \
                       "                  FROM assoccatsources " + \
                       "                      ,extractedsource " + \
                       "                      ,images " + \
                       "                      ,lsm " + \
                       "                  WHERE xtrsrc_id = xtrsrcid " + \
                       "                    AND image_id = imageid " + \
                       "                    AND dataset = %s " + \
                       "                    AND assoc_catsrc_id = lsmid " + \
                       "                    AND cat_id = %s " + \
                       "                GROUP BY bin_dist_nr " + \
                       "               ) t " + \
                       "       ) t2 " + \
                       "ORDER BY t2.bin_dist ", (dsid,catid))
        sf_y = cursor.fetchall()
        
        # --- Background Fields ----
        cursor.execute("SELECT * " + \
                       "  FROM (SELECT nsources " + \
                       "              ,avg_dist_arcsec " + \
                       "              ,CAST(bin_dist_nr AS DOUBLE)/10 AS bin_dist " + \
                       "              ,bin_dist_nr " + \
                       "          FROM (SELECT COUNT(*) AS nsources " + \
                       "                      ,AVG(assoc_distance_arcsec) AS avg_dist_arcsec " + \
                       "                      ,CAST(1 + floor(10 * assoc_distance_arcsec) AS INTEGER) AS bin_dist_nr " + \
                       "                  FROM assoccatsources " + \
                       "                      ,extractedsource " + \
                       "                      ,images " + \
                       "                      ,lsm " + \
                       "                  WHERE xtrsrc_id = xtrsrcid " + \
                       "                    AND image_id = imageid " + \
                       "                    AND dataset >= %s " + \
                       "                    AND dataset <= %s " + \
                       "                    AND assoc_catsrc_id = lsmid " + \
                       "                    AND cat_id = %s " + \
                       "                GROUP BY bin_dist_nr " + \
                       "               ) t " + \
                       "       ) t2 " + \
                       "ORDER BY t2.bin_dist ", (dsid_min,dsid_max,catid))
        bg_y = cursor.fetchall()
        cursor.close()
        
        sf_nsources = []
        sf_avg_dist_arcsec = []
        sf_bin_dist = []
        sf_bin_dist_nr = []
        
        bg_nsources = []
        bg_avg_dist_arcsec = []
        bg_bin_dist = []
        bg_bin_dist_nr = []
        
        sum_sf_nsources = []
        sum_bg_nsources = []
        diff_nsources = []
        
        if (len(sf_y) != len(bg_y)):
            print "len(sf_y) = ", len(sf_y), " len(bg_y) = ", len(bg_y)

        for i in range(len(sf_y)):
            if (sf_y[i][3] != bg_y[i][3]):
                print "Bins differ at i = ", i, " sf_y[i][3] = ", sf_y[i][3], " bg_y[i][3] = ", bg_y[i][3]
                # this means the bin_nr are unequal, we insert one:
                if (sf_y[i][3] < bg_y[i][3]):
                    bg_y.insert(i,[0, sf_y[i][1], sf_y[i][2], sf_y[i][3]])
                    print "inserted in bg_y at i = ", i, ": sf_y[i][1:] = ", sf_y[i][1:]
                else:
                    sf_y.insert(i,[0, bg_y[i][1], bg_y[i][2], bg_y[i][3]])
                    print "inserted in sf_y at i = ", i, ": bg_y[i][1:] = ", sf_y[i][1:]
            
            sf_nsources.append(sf_y[i][0] / 259114.)
            sf_avg_dist_arcsec.append(sf_y[i][1])
            sf_bin_dist.append(sf_y[i][2])
            sf_bin_dist_nr.append(sf_y[i][3])
            if i > 0:
                sum_sf_nsources.append(sum_sf_nsources[i - 1] + sf_nsources[i])
            else:
                sum_sf_nsources.append(sf_nsources[i])

        for i in range(len(bg_y)):
            bg_nsources.append(bg_y[i][0] / 196842.)
            #bg_npairs.append(bg_y[i][0] / 18816.)
            bg_avg_dist_arcsec.append(bg_y[i][1])
            bg_bin_dist.append(bg_y[i][2])
            bg_bin_dist_nr.append(bg_y[i][3])
            if i > 0:
                sum_bg_nsources.append(sum_bg_nsources[i - 1] + bg_nsources[i])
            else:
                sum_bg_nsources.append(bg_nsources[i])
            
            #TODO: check how to do when bins differ
            diff_nsources.append(sum_sf_nsources[i] - sum_bg_nsources[i])
        
        xwidth = 1./len(sf_bin_dist)
        xcentr = pylab.arange(0,1,xwidth)
        
        plotfiles=[]
        p = 0
        fig = pylab.figure()
        ax1 = fig.add_subplot(111)
        ax1.set_xlabel('Distance [arcsec]')
        ax1.set_ylabel('N/Field')
        
        ax1.plot(sf_bin_dist, sum_sf_nsources, 'b-', label='Source')
        #ax1.plot(sf_bin_r, sum_bg_npairs, 'k--', label='BG avg')
        ax1.plot(bg_bin_dist, sum_bg_nsources, 'k--', label='Background')
        pylab.legend(numpoints=1,loc='best')
        ax1.grid(True)
        
        ax2 = ax1.twinx()
        ax2.set_ylabel('SF - BG', color='r')
        for tl in ax2.get_yticklabels():
            tl.set_color('r')
        ax2.plot(sf_bin_dist, diff_nsources, 'r-', linewidth=3, label='Diff.')
        
        plotfiles.append('SAI_cumul_distr_dist_npairs_wenssnvss.eps')
        pylab.savefig(plotfiles[p],dpi=600)
        
        return plotfiles
    except db.Error, e:
        logging.warn("plotWenssNvssFig4() for dsid %s failed " % (str(dsid)))
        raise
    

def plotWenssNvssFig4(dsid,dsid_min,dsid_max,catid,conn):
    """
    This makes a x-y, r-N/field step plot of the source and background fields.
    The difference between the two is also plotted as to make clear
    where a cautoff between the two exists
    SF count(*) = 259,114 (all assocs w/ NVSS)
                = 245,138 (all assocs w/ NVSS and assoc_lr > -100)
    BG count(*) = 196,842 (all assocs from all fields w/ NVSS) div by 8 => 
                =  24,605 per field
                = 150,529 (all assocs w/ NVSS and assoc_lr > -100) =>
                =  18,816 per field
    """
    try:
        cursor = conn.cursor()
        # --- Source Field ----
        cursor.execute("SELECT * " + \
                       "  FROM (SELECT npairs " + \
                       "              ,avg_loglr " + \
                       "              ,CAST(bin_r_nr AS DOUBLE)/40 AS bin_r " + \
                       "              ,bin_r_nr " + \
                       "          FROM (SELECT COUNT(*) AS npairs " + \
                       "                      ,AVG(assoc_lr) AS avg_loglr " + \
                       "                      ,CAST(1 + floor(40 * assoc_r) AS INTEGER) AS bin_r_nr " + \
                       "                  FROM assoccatsources " + \
                       "                      ,extractedsource " + \
                       "                      ,images " + \
                       "                      ,lsm " + \
                       "                  WHERE xtrsrc_id = xtrsrcid " + \
                       "                    AND image_id = imageid " + \
                       "                    AND dataset = %s " + \
                       "                    AND assoc_catsrc_id = lsmid " + \
                       "                    AND cat_id = %s " + \
                       "                    AND assoc_lr > -100 " + \
                       "                GROUP BY bin_r_nr " + \
                       "               ) t " + \
                       "       ) t2 " + \
                       "ORDER BY t2.bin_r ", (dsid,catid))
        sf_y = cursor.fetchall()
        
        # --- Background Fields ----
        cursor.execute("SELECT * " + \
                       "  FROM (SELECT npairs " + \
                       "              ,avg_loglr " + \
                       "              ,CAST(bin_r_nr AS DOUBLE)/40 AS bin_r " + \
                       "              ,bin_r_nr " + \
                       "          FROM (SELECT COUNT(*) AS npairs " + \
                       "                      ,AVG(assoc_lr) AS avg_loglr " + \
                       "                      ,CAST(1 + floor(40 * assoc_r) AS INTEGER) AS bin_r_nr " + \
                       "                  FROM assoccatsources " + \
                       "                      ,extractedsource " + \
                       "                      ,images " + \
                       "                      ,lsm " + \
                       "                  WHERE xtrsrc_id = xtrsrcid " + \
                       "                    AND image_id = imageid " + \
                       "                    AND dataset >= %s " + \
                       "                    AND dataset <= %s " + \
                       "                    AND assoc_catsrc_id = lsmid " + \
                       "                    AND cat_id = %s " + \
                       "                    AND assoc_lr > -100 " + \
                       "                GROUP BY bin_r_nr " + \
                       "               ) t " + \
                       "       ) t2 " + \
                       "ORDER BY t2.bin_r ", (dsid_min,dsid_max,catid))
        bg_y = cursor.fetchall()
        cursor.close()
        
        sf_npairs = []
        sf_avg_logLR = []
        sf_bin_r = []
        sf_bin_r_nr = []
        
        bg_npairs = []
        bg_avg_logLR = []
        bg_bin_r = []
        bg_bin_r_nr = []
        
        sum_sf_npairs = []
        sum_bg_npairs = []
        diff_npairs = []
        
        if (len(sf_y) != len(bg_y)):
            print "len(sf_y) = ", len(sf_y), " len(bg_y) = ", len(bg_y)

        for i in range(len(sf_y)):
            if (sf_y[i][3] != bg_y[i][3]):
                print "Bins differ: i = ", i, " sf_y[i][3] = ", sf_y[i][3], " bg_y[i][3] = ", bg_y[i][3]
                break
            
            sf_npairs.append(sf_y[i][0] / 259114.)
            sf_avg_logLR.append(sf_y[i][1])
            sf_bin_r.append(sf_y[i][2])
            sf_bin_r_nr.append(sf_y[i][3])
            if i > 0:
                sum_sf_npairs.append(sum_sf_npairs[i - 1] + sf_npairs[i])
            else:
                sum_sf_npairs.append(sf_npairs[i])

        for i in range(len(bg_y)):
            bg_npairs.append(bg_y[i][0] / 196842.)
            #bg_npairs.append(bg_y[i][0] / 18816.)
            bg_avg_logLR.append(bg_y[i][1])
            bg_bin_r.append(bg_y[i][2])
            bg_bin_r_nr.append(bg_y[i][3])
            if i > 0:
                sum_bg_npairs.append(sum_bg_npairs[i - 1] + bg_npairs[i])
            else:
                sum_bg_npairs.append(bg_npairs[i])
            
            #TODO: check how to do when bins differ
            #diff_npairs.append(sum_sf_npairs[i] - sum_bg_npairs[i])
        
        xwidth = 1./len(sf_bin_r)
        xcentr = pylab.arange(0,1,xwidth)
        
        plotfiles=[]
        p = 0
        fig = pylab.figure()
        ax1 = fig.add_subplot(111)
        ax1.set_xlabel(r'dimensionless distance $r$')
        ax1.set_ylabel('Cumulative number of association pairs per Field')
        
        ax1.plot(sf_bin_r, sum_sf_npairs, 'b-', label='SF avg')
        #ax1.plot(sf_bin_r, sum_bg_npairs, 'k--', label='BG avg')
        ax1.plot(bg_bin_r, sum_bg_npairs, 'k--', label='BG avg')
        pylab.legend(numpoints=1,loc='center right')
        ax1.grid(True)
        
        #ax2 = ax1.twinx()
        #ax2.set_ylabel('SF - BG', color='r')
        #for tl in ax2.get_yticklabels():
        #    tl.set_color('r')
        #ax2.plot(sf_bin_r, diff_npairs, 'r-', linewidth=3, label='Diff.')
        
        plotfiles.append('SAI_cumul_distr_r_npairs_wenssnvss.eps')
        pylab.savefig(plotfiles[p],dpi=600)
        
        return plotfiles
    except db.Error, e:
        logging.warn("plotWenssNvssFig4() for dsid %s failed " % (str(dsid)))
        raise
    

def plotWenssNvssFig3(dsid,dsid_min,dsid_max,catid,conn):
    """
    This makes a x-y, logLR-r plot of the source and background fields.
    The difference between the two is also plotted as to make clear
    where a cautoff between the two exists
    SF count(*) = 259114 (all assocs w/ NVSS)
    BG count(*) = 196842 (all assocs from all fields w/ NVSS) div by 8 => 
                = 24,605 per field
    """
    try:
        cursor = conn.cursor()
        # --- Source Field ----
        cursor.execute("SELECT * " + \
                       "  FROM (SELECT npairs " + \
                       "              ,CAST(bin_lr_nr AS DOUBLE)/2 AS bin_lr " + \
                       "              ,bin_lr_nr " + \
                       "          FROM (SELECT COUNT(*) AS npairs " + \
                       "                      ,CAST(1 + floor(2 * assoc_lr) AS INTEGER) AS bin_lr_nr " + \
                       "                  FROM assoccatsources " + \
                       "                      ,extractedsource " + \
                       "                      ,images " + \
                       "                      ,lsm " + \
                       "                  WHERE xtrsrc_id = xtrsrcid " + \
                       "                    AND image_id = imageid " + \
                       "                    AND dataset = %s " + \
                       "                    AND assoc_catsrc_id = lsmid " + \
                       "                    AND cat_id = %s " + \
                       "                    AND assoc_lr > -100 " + \
                       "                GROUP BY bin_lr_nr " + \
                       "               ) t " + \
                       "       ) t2 " + \
                       "ORDER BY t2.bin_lr ", (dsid,catid))
        sf_y = cursor.fetchall()
        
        # --- Background Fields ----
        cursor.execute("SELECT * " + \
                       "  FROM (SELECT npairs " + \
                       "              ,CAST(bin_lr_nr AS DOUBLE)/2 AS bin_lr " + \
                       "              ,bin_lr_nr " + \
                       "          FROM (SELECT COUNT(*) AS npairs " + \
                       "                      ,CAST(1 + floor(2 * assoc_lr) AS INTEGER) AS bin_lr_nr " + \
                       "                  FROM assoccatsources " + \
                       "                      ,extractedsource " + \
                       "                      ,images " + \
                       "                      ,lsm " + \
                       "                  WHERE xtrsrc_id = xtrsrcid " + \
                       "                    AND image_id = imageid " + \
                       "                    AND dataset >= %s " + \
                       "                    AND dataset <= %s " + \
                       "                    AND assoc_catsrc_id = lsmid " + \
                       "                    AND cat_id = %s " + \
                       "                    AND assoc_lr > -100 " + \
                       "                GROUP BY bin_lr_nr " + \
                       "               ) t " + \
                       "       ) t2 " + \
                       "ORDER BY t2.bin_lr ", (dsid_min,dsid_max,catid))
        bg_y = cursor.fetchall()
        cursor.close()
        
        sf_npairs = []
        sf_bin_lr = []
        sf_bin_lr_nr = []
        
        bg_npairs = []
        bg_bin_lr = []
        bg_bin_lr_nr = []
        
        sum_sf_npairs = []
        sum_bg_npairs = []
        ratio_npairs = []
        
        if (len(sf_y) != len(bg_y)):
            print "len(sf_y) = ", len(sf_y), " len(bg_y) = ", len(bg_y)
            
        for i in range(len(sf_y)):
            # if we do not process the same bin_nr for SF and BG we quit
            if (sf_y[i][2] != bg_y[i][2]):
                print "i = ", i, " sf_y[i][2] = ", sf_y[i][2], " bg_y[i][2] = ", bg_y[i][2]
                break
            
            sf_npairs.append(sf_y[i][0] / 259114.)
            sf_bin_lr.append(sf_y[i][1])
            sf_bin_lr_nr.append(sf_y[i][2])
            
            bg_npairs.append(bg_y[i][0] / 196842./8.)
            bg_bin_lr.append(bg_y[i][1])
            bg_bin_lr_nr.append(bg_y[i][2])
           
            ratio_npairs.append(sf_npairs[i] / bg_npairs[i])
            
        plotfiles=[]
        p = 0
        fig = pylab.figure()
        ax1 = fig.add_subplot(111)
        ax1.set_xlabel(r'$\log LR$')
        ax1.set_ylabel('sources per Field per LR bin (normalized)')
        
        ax1.semilogy(sf_bin_lr, sf_npairs, 'b-', label='SF avg')
        ax1.semilogy(bg_bin_lr, bg_npairs, 'g--', label='BG avg')
        pylab.legend(numpoints=1,loc='upper left')
        ax1.grid(True)
        
        ax2 = ax1.twinx()
        ax2.set_ylabel(r'Ratio $N_{SF} / N_{BG}$', color='r')
        for tl in ax2.get_yticklabels():
            tl.set_color('r')
        ax2.semilogy(sf_bin_lr, ratio_npairs, 'r-', linewidth=3, label='Diff. avg')
        
        #plotfiles.append('SAI_reliab_logLR_wenssnvss.eps')
        plotfiles.append('SAI_normdistr_logLR_SFBG_wenssnvss.eps')
        pylab.savefig(plotfiles[p],dpi=600)
        
        return plotfiles
    except db.Error, e:
        logging.warn("plotWenssNvssFig3() for dsid %s failed " % (str(dsid)))
        raise
    

def plotWenssNvssFig2(dsid,dsid_min,dsid_max,catid,conn):
    """
    This makes a scatter plot of the min avg and max log(LR)
    as a function of binned assoc_r, with binwidth = 0.01.
    """
    try:
        cursor = conn.cursor()
        # --- Source Field ----
        cursor.execute("SELECT * " + \
                       "  FROM (SELECT npairs " + \
                       "              ,min_loglr " + \
                       "              ,avg_loglr " + \
                       "              ,max_loglr " + \
                       "              ,CAST(bin_r_nr AS DOUBLE)/40 AS bin_r " + \
                       "              ,bin_r_nr " + \
                       "          FROM (SELECT COUNT(*) AS npairs " + \
                       "                      ,MIN(assoc_lr) AS min_loglr " + \
                       "                      ,AVG(assoc_lr) AS avg_loglr " + \
                       "                      ,MAX(assoc_lr) AS max_loglr " + \
                       "                      ,CAST(1 + floor(40 * assoc_r) AS INTEGER) AS bin_r_nr " + \
                       "                  FROM assoccatsources " + \
                       "                      ,extractedsource " + \
                       "                      ,images " + \
                       "                      ,lsm " + \
                       "                  WHERE xtrsrc_id = xtrsrcid " + \
                       "                    AND image_id = imageid " + \
                       "                    AND dataset = %s " + \
                       "                    AND assoc_catsrc_id = lsmid " + \
                       "                    AND cat_id = %s " + \
                       #"                    AND assoc_lr > -100 " + \
                       "                GROUP BY bin_r_nr " + \
                       "               ) t " + \
                       "       ) t2 " + \
                       " WHERE t2.bin_r <= 30 " + \
                       "ORDER BY t2.bin_r ", (dsid,catid))
        sf_y = cursor.fetchall()
        
        # --- Background Fields ----
        cursor.execute("SELECT * " + \
                       "  FROM (SELECT npairs " + \
                       "              ,min_loglr " + \
                       "              ,avg_loglr " + \
                       "              ,max_loglr " + \
                       "              ,CAST(bin_r_nr AS DOUBLE)/40 AS bin_r " + \
                       "              ,bin_r_nr " + \
                       "          FROM (SELECT COUNT(*) AS npairs " + \
                       "                      ,MIN(assoc_lr) AS min_loglr " + \
                       "                      ,AVG(assoc_lr) AS avg_loglr " + \
                       "                      ,MAX(assoc_lr) AS max_loglr " + \
                       "                      ,CAST(1 + floor(40 * assoc_r) AS INTEGER) AS bin_r_nr " + \
                       "                  FROM assoccatsources " + \
                       "                      ,extractedsource " + \
                       "                      ,images " + \
                       "                      ,lsm " + \
                       "                  WHERE xtrsrc_id = xtrsrcid " + \
                       "                    AND image_id = imageid " + \
                       "                    AND dataset >= %s " + \
                       "                    AND dataset <= %s " + \
                       "                    AND assoc_catsrc_id = lsmid " + \
                       "                    AND cat_id = %s " + \
                       #"                    AND assoc_lr > -100 " + \
                       "                GROUP BY bin_r_nr " + \
                       "               ) t " + \
                       "       ) t2 " + \
                       " WHERE t2.bin_r <= 30 " + \
                       "ORDER BY t2.bin_r ", (dsid_min,dsid_max,catid))
        bg_y = cursor.fetchall()
        cursor.close()
        
        sf_npairs = []
        sf_min_logLR = []
        sf_avg_logLR = []
        sf_max_logLR = []
        sf_bin_r = []
        sf_bin_r_nr = []
        
        bg_npairs = []
        bg_min_logLR = []
        bg_avg_logLR = []
        bg_max_logLR = []
        bg_bin_r = []
        bg_bin_r_nr = []
        
        min_logLR_ratio = []
        avg_logLR_ratio = []
        max_logLR_ratio = []
        
        if (len(sf_y) != len(bg_y)):
            print "len(sf_y) = ", len(sf_y), " len(bg_y) = ", len(bg_y)
            
        for i in range(len(sf_y)):
            # if we do not process the same bin_nr for SF and BG we quit
            if (sf_y[i][5] != bg_y[i][5]):
                print "i = ", i, " sf_y[i][5] = ", sf_y[i][5], " bg_y[i][5] = ", bg_y[i][5]
                break
            sf_npairs.append(sf_y[i][0])
            sf_min_logLR.append(sf_y[i][1])
            sf_avg_logLR.append(sf_y[i][2])
            sf_max_logLR.append(sf_y[i][3])
            sf_bin_r.append(sf_y[i][4])
            sf_bin_r_nr.append(sf_y[i][5])
            
            bg_npairs.append(bg_y[i][0])
            bg_min_logLR.append(bg_y[i][1])
            bg_avg_logLR.append(bg_y[i][2])
            bg_max_logLR.append(bg_y[i][3])
            bg_bin_r.append(bg_y[i][4])
            bg_bin_r_nr.append(bg_y[i][5])
            
            min_logLR_ratio.append(sf_min_logLR[i] / bg_min_logLR[i])
            avg_logLR_ratio.append(sf_avg_logLR[i] - bg_avg_logLR[i])
            max_logLR_ratio.append(sf_max_logLR[i] / bg_max_logLR[i])
            
            #print i,sf_avg_logLR[i],bg_avg_logLR[i],avg_logLR_ratio[i]
        
        plotfiles=[]
        p = 0
        fig = pylab.figure()
        ax1 = fig.add_subplot(111)
        ax1.set_xlabel(r'dimensionless distance $r$')
        ax1.set_ylabel(r'$\log LR$')
        
        ax1.plot(sf_bin_r, sf_avg_logLR, 'b-', label='SF avg')
        ax1.plot(bg_bin_r, bg_avg_logLR, 'k--', label='BG avg')
        pylab.legend(numpoints=1,loc='upper right')
        ax1.grid(True)
        
        ax2 = ax1.twinx()
        ax2.set_ylabel(r'difference $\log LR$', color='r')
        for tl in ax2.get_yticklabels():
            tl.set_color('r')
        ax2.plot(sf_bin_r, avg_logLR_ratio, 'r-', linewidth=2, label='Diff. avg')
        
        #pylab.title(r'Source - Cat Association Indices $r, \log LR$ ' + \
        #            'and ratios for datasets ' + str(dsid_min) + ' - ' + str(dsid_max))
        plotfiles.append('SAI_r_ratios_catid' + str(catid) + '_dsids' + str(dsid_min) + '_' + str(dsid_max) + '.eps')
        pylab.savefig(plotfiles[p],dpi=600)
        
        return plotfiles
    except db.Error, e:
        logging.warn("scatterWenssNvssSourceFieldplusBackGround() for dsid %s failed " % (str(dsid)))
        raise
    

def scatterSourceAssocIndexX2CBackGround(dsid_min,dsid_max,catid,conn):
    """
    This makes a scatter plot of the min avg and max log(LR)
    as a function of binned assoc_r, with binwidth = 0.01.
    """
    try:
        cursor = conn.cursor()
        cursor.execute("Select * " + \
                       "  from ( " + \
                       "select npairs " + \
                       "      ,min_loglr " + \
                       "      ,avg_loglr " + \
                       "      ,max_loglr " + \
                       "      ,cast(bin_r_nr as double)/100 as bin_r " + \
                       "      ,avg_dist " + \
                       "  from (select count(*) as npairs " + \
                       "              ,min(assoc_lr) as min_loglr " + \
                       "              ,avg(assoc_lr) as avg_loglr " + \
                       "              ,max(assoc_lr) as max_loglr " + \
                       "              ,cast(1 + floor(100 * assoc_r) as integer) as bin_r_nr " + \
                       "              ,avg(assoc_distance_arcsec) as avg_dist " + \
                       "          from assoccatsources " + \
                       "              ,extractedsource " + \
                       "              ,images " + \
                       "              ,lsm " + \
                       "         where xtrsrc_id = xtrsrcid " + \
                       "           and image_id = imageid " + \
                       "           and dataset >= %s " + \
                       "           and dataset <= %s " + \
                       "           and assoc_catsrc_id = lsmid " + \
                       "           and cat_id = %s " + \
                       "           and assoc_lr > -20 " + \
                       "        group by bin_r_nr " + \
                       "       ) t " + \
                       "       ) t2 " + \
                       " where t2.bin_r < 2 " + \
                       "order by t2.bin_r ", (dsid_min,dsid_max,catid))
        y = cursor.fetchall()
        cursor.close()
        
        npairs = []
        min_logLR = []
        avg_logLR = []
        max_logLR = []
        bin_r = []
        avg_dist = []
        
        for i in range(len(y)):
            npairs.append(y[i][0])
            min_logLR.append(y[i][1])
            avg_logLR.append(y[i][2])
            max_logLR.append(y[i][3])
            bin_r.append(y[i][4])
            avg_dist.append(y[i][5])
        
        plotfiles=[]
        p = 0
        fig = pylab.figure()
        ax1 = fig.add_subplot(111)
        ax1.set_xlabel(r'dimensionless distance $r$')
        ax1.set_ylabel(r'$\log LR$')
        ax1.scatter(bin_r, min_logLR, color='r', marker='o', label='min')
        ax1.scatter(bin_r, avg_logLR, color='b', marker='o', label='avg')
        ax1.scatter(bin_r, max_logLR, color='g', marker='o', label='max')
        ax1.grid(True)
        pylab.title(r'Source - Cat Association Indices $r, \log LR$ ' + \
                    'for datasets ' + str(dsid_min) + ' - ' + str(dsid_max))
        pylab.legend(numpoints=1,loc='best')
        plotfiles.append('SAI_catid' + str(catid) + '_dsids' + str(dsid_min) + '_' + str(dsid_max) + '.eps')
        pylab.savefig(plotfiles[p],dpi=600)
        
        """
        p += 1
        disti = pylab.linspace(min(avg_dist),max(avg_dist),100)
        ri = pylab.linspace(min(bin_r),max(bin_r),100)
        lri = pylab.linspace(min(min_logLR),max(max_logLR),100)
        
        fig = pylab.figure()
        zi = matplotlib.mlab.griddata(bin_r,avg_logLR,avg_dist,ri,lri)
        cs = pylab.contour(ri,lri,zi,15,linewidths=0.5,colors='k')
        cs = pylab.contourf(ri,lri,zi,15,cmap=pylab.cm.jet)
        pylab.colorbar()
        pylab.scatter(bin_r,avg_logLR,marker='o',c='b',s=5)
        pylab.xlim(min(bin_r),max(bin_r))
        pylab.ylim(min(min_logLR),max(max_logLR))
        pylab.xlabel(r'dimensionless radius $r$')
        pylab.ylabel(r'\log LR')
        pylab.grid(True)
        pylab.title(r'$r, \log LR$, distance for dataset ' + str(dsid) )
        plotfiles.append('contour_bin_r__rLRdist_dsid' + str(dsid) + '.eps')
        pylab.savefig(plotfiles[p],dpi=600)
        """
        
        return plotfiles
    except db.Error, e:
        logging.warn("scatterSourceAssocIndexX2X() for dsid %s failed " % (str(dsid)))
        raise
    

def scatterSourceAssocIndexX2C(dsid,catid,conn):
    """
    This makes a scatter plot of the min avg and max log(LR)
    as a function of binned assoc_r, with binwidth = 0.01.
    """
    try:
        cursor = conn.cursor()
        cursor.execute("Select * " + \
                       "  from ( " + \
                       "select npairs " + \
                       "      ,min_loglr " + \
                       "      ,avg_loglr " + \
                       "      ,max_loglr " + \
                       "      ,cast(bin_r_nr as double)/100 as bin_r " + \
                       "      ,avg_dist " + \
                       "  from (select count(*) as npairs " + \
                       "              ,min(assoc_lr) as min_loglr " + \
                       "              ,avg(assoc_lr) as avg_loglr " + \
                       "              ,max(assoc_lr) as max_loglr " + \
                       "              ,cast(1 + floor(100 * assoc_r) as integer) as bin_r_nr " + \
                       "              ,avg(assoc_distance_arcsec) as avg_dist " + \
                       "          from assoccatsources " + \
                       "              ,extractedsource " + \
                       "              ,images " + \
                       "              ,lsm " + \
                       "         where xtrsrc_id = xtrsrcid " + \
                       "           and image_id = imageid " + \
                       "           and dataset = %s " + \
                       "           and assoc_catsrc_id = lsmid " + \
                       "           and cat_id = %s " + \
                       "           and assoc_lr > -20 " + \
                       "        group by bin_r_nr " + \
                       "       ) t " + \
                       "       ) t2 " + \
                       " where t2.bin_r < 2 " + \
                       "order by t2.bin_r ", (dsid,catid))
        y = cursor.fetchall()
        cursor.close()
        
        npairs = []
        min_logLR = []
        avg_logLR = []
        max_logLR = []
        bin_r = []
        avg_dist = []
        
        for i in range(len(y)):
            npairs.append(y[i][0])
            min_logLR.append(y[i][1])
            avg_logLR.append(y[i][2])
            max_logLR.append(y[i][3])
            bin_r.append(y[i][4])
            avg_dist.append(y[i][5])
        
        plotfiles=[]
        p = 0
        fig = pylab.figure()
        ax1 = fig.add_subplot(111)
        ax1.set_xlabel(r'dimensionless distance $r$')
        ax1.set_ylabel(r'$\log LR$')
        ax1.scatter(bin_r, min_logLR, color='r', marker='o', label='min')
        ax1.scatter(bin_r, avg_logLR, color='b', marker='o', label='avg')
        ax1.scatter(bin_r, max_logLR, color='g', marker='o', label='max')
        ax1.legend(numpoints=1,loc='best')
        ax1.grid(True)
        pylab.title(r'Source - Cat Association Indices $r, \log LR$ in dataset ' + str(dsid))
        #pylab.legend(numpoints=1,loc='best')
        plotfiles.append('SAI_catid' + str(catid) + '_dsid' + str(dsid) + '.eps')
        pylab.savefig(plotfiles[p],dpi=600)
        
        """
        p += 1
        disti = pylab.linspace(min(avg_dist),max(avg_dist),100)
        ri = pylab.linspace(min(bin_r),max(bin_r),100)
        lri = pylab.linspace(min(min_logLR),max(max_logLR),100)
        
        fig = pylab.figure()
        zi = matplotlib.mlab.griddata(bin_r,avg_logLR,avg_dist,ri,lri)
        cs = pylab.contour(ri,lri,zi,15,linewidths=0.5,colors='k')
        cs = pylab.contourf(ri,lri,zi,15,cmap=pylab.cm.jet)
        pylab.colorbar()
        pylab.scatter(bin_r,avg_logLR,marker='o',c='b',s=5)
        pylab.xlim(min(bin_r),max(bin_r))
        pylab.ylim(min(min_logLR),max(max_logLR))
        pylab.xlabel(r'dimensionless radius $r$')
        pylab.ylabel(r'\log LR')
        pylab.grid(True)
        pylab.title(r'$r, \log LR$, distance for dataset ' + str(dsid) )
        plotfiles.append('contour_bin_r__rLRdist_dsid' + str(dsid) + '.eps')
        pylab.savefig(plotfiles[p],dpi=600)
        """
        
        return plotfiles
    except db.Error, e:
        logging.warn("scatterSourceAssocIndexX2X() for dsid %s failed " % (str(dsid)))
        raise
    

def scatterSourceAssocIndexX2X(dsid,conn):
    """
    This makes a scatter plot of the min avg and max log(LR)
    as a function of binned assoc_r, with binwidth = 0.01.
    """
    try:
        cursor = conn.cursor()
        cursor.execute("select npairs " + \
                       "      ,min_loglr " + \
                       "      ,avg_loglr " + \
                       "      ,max_loglr " + \
                       "      ,cast(bin_r_nr as double)/100 as bin_r " + \
                       "      ,avg_dist " + \
                       "  from (select count(*) as npairs " + \
                       "              ,min(assoc_lr) as min_loglr " + \
                       "              ,avg(assoc_lr) as avg_loglr " + \
                       "              ,max(assoc_lr) as max_loglr " + \
                       "              ,cast(1 + floor(100 * assoc_r) as integer) as bin_r_nr " + \
                       "              ,avg(assoc_distance_arcsec) as avg_dist " + \
                       "          from assocxtrsources " + \
                       "              ,extractedsource " + \
                       "              ,images " + \
                       "         where xtrsrc_id = xtrsrcid " + \
                       "           and image_id = imageid " + \
                       "           and xtrsrc_id <> assoc_xtrsrc_id " + \
                       "           and dataset = %s " + \
                       "        group by bin_r_nr " + \
                       "       ) t " + \
                       "order by bin_r ", (dsid,))
        y = cursor.fetchall()
        cursor.close()
        
        npairs = []
        min_logLR = []
        avg_logLR = []
        max_logLR = []
        bin_r = []
        avg_dist = []
        
        for i in range(len(y)):
            npairs.append(y[i][0])
            min_logLR.append(y[i][1])
            avg_logLR.append(y[i][2])
            max_logLR.append(y[i][3])
            bin_r.append(y[i][4])
            avg_dist.append(y[i][5])
        
        plotfiles=[]
        p = 0
        fig = pylab.figure()
        ax1 = fig.add_subplot(111)
        ax1.set_xlabel(r'dimensionless distance $r$')
        ax1.set_ylabel(r'$\log LR$')
        ax1.scatter(bin_r, min_logLR, color='r', marker='o', label='min')
        ax1.scatter(bin_r, avg_logLR, color='b', marker='o', label='avg')
        ax1.scatter(bin_r, max_logLR, color='g', marker='o', label='max')
        ax1.grid(True)
        pylab.title(r'Source-Source Association Indices $r, \log LR$ in dataset ' + str(dsid))
        pylab.legend(numpoints=1,loc='best')
        plotfiles.append('SAI_dsid' + str(dsid) + '.eps')
        pylab.savefig(plotfiles[p],dpi=600)
        
        """
        p += 1
        disti = pylab.linspace(min(avg_dist),max(avg_dist),100)
        ri = pylab.linspace(min(bin_r),max(bin_r),100)
        lri = pylab.linspace(min(min_logLR),max(max_logLR),100)
        
        fig = pylab.figure()
        zi = matplotlib.mlab.griddata(bin_r,avg_logLR,avg_dist,ri,lri)
        cs = pylab.contour(ri,lri,zi,15,linewidths=0.5,colors='k')
        cs = pylab.contourf(ri,lri,zi,15,cmap=pylab.cm.jet)
        pylab.colorbar()
        pylab.scatter(bin_r,avg_logLR,marker='o',c='b',s=5)
        pylab.xlim(min(bin_r),max(bin_r))
        pylab.ylim(min(min_logLR),max(max_logLR))
        pylab.xlabel(r'dimensionless radius $r$')
        pylab.ylabel(r'\log LR')
        pylab.grid(True)
        pylab.title(r'$r, \log LR$, distance for dataset ' + str(dsid) )
        plotfiles.append('contour_bin_r__rLRdist_dsid' + str(dsid) + '.eps')
        pylab.savefig(plotfiles[p],dpi=600)
        """
        
        return plotfiles
    except db.Error, e:
        logging.warn("scatterSourceAssocIndexX2X() for dsid %s failed " % (str(dsid)))
        raise
    

def contourX2CDistLRRho(conn,dsid, catid):
    try:
        cursor = conn.cursor()
        cursor.execute("select xtrsrc_id " + \
                       "      ,assoc_catsrc_id " + \
                       "      ,cast(1 + floor(10 * assoc_distance_arcsec) as integer) as bin_dist " + \
                       "      ,assoc_distance_arcsec " + \
                       "      ,assoc_r " + \
                       "      ,assoc_lr " + \
                       "  from assoccatsources " + \
                       "      ,extractedsource " + \
                       "      ,images " + \
                       "      ,lsm " + \
                       " where xtrsrc_id = xtrsrcid " + \
                       "   and image_id = imageid " + \
                       "   and dataset = %s " + \
                       "   and assoc_catsrc_id = lsmid " + \
                       "   and cat_id = %s " + \
                       "order by assoc_distance_arcsec ", (dsid,catid))
        y = cursor.fetchall()
        cursor.close()
        xtrsrcid = []
        assoc_id = []
        bin_dist = []
        assoc_dist = []
        assoc_rho = []
        assoc_lr = []
        for i in range(len(y)):
            xtrsrcid.append(y[i][0])
            assoc_id.append(y[i][1])
            bin_dist.append(y[i][2])
            assoc_dist.append(y[i][3])
            assoc_rho.append(y[i][4])
            assoc_lr.append(y[i][5])
        
        disti = pylab.linspace(min(assoc_dist),max(assoc_dist),100)
        rhoi = pylab.linspace(min(assoc_rho),max(assoc_rho),100)
        lri = pylab.linspace(min(assoc_lr),max(assoc_lr),100)
        
        plotfiles = []
        p = 0
        """
        fig = pylab.figure()
        zi = matplotlib.mlab.griddata(assoc_dist,assoc_lr,assoc_rho,disti,lri)
        cs = pylab.contour(disti,lri,zi,15,linewidths=0.5,colors='k')
        cs = pylab.contourf(disti,lri,zi,15,cmap=pylab.cm.jet)
        pylab.colorbar()
        pylab.scatter(assoc_dist,assoc_lr,marker='o',c='b',s=5)
        pylab.xlim(min(assoc_dist),max(assoc_dist))
        pylab.ylim(min(assoc_lr),max(assoc_lr))
        pylab.xlabel('distance [arcsec]')
        pylab.ylabel('log LR')
        pylab.grid(True)
        pylab.title('Distance, LR, rho for xtr-cat assocs in dataset ' + str(dsid) )
        plotfiles.append('contour_xtrcat_' + str(catid) + '_distLRrho_dsid' + str(dsid) + '.eps')
        pylab.savefig(plotfiles[p],dpi=600)

        p += 1
        fig = pylab.figure()
        zi = matplotlib.mlab.griddata(assoc_dist,assoc_rho,assoc_lr,disti,rhoi)
        cs = pylab.contour(disti,rhoi,zi,15,linewidths=0.5,colors='k')
        cs = pylab.contourf(disti,rhoi,zi,15,cmap=pylab.cm.jet)
        pylab.colorbar()
        pylab.scatter(assoc_dist,assoc_rho,marker='o',c='b',s=5)
        pylab.xlim(min(assoc_dist),max(assoc_dist))
        pylab.ylim(min(assoc_rho),max(assoc_rho))
        pylab.xlabel('distance [arcsec]')
        pylab.ylabel(r'dimensionless radius $\rho$')
        pylab.grid(True)
        pylab.title('Distance, rho, LR for dataset ' + str(dsid) )
        plotfiles.append('contour_xtrcat_' + str(catid) + '_distrhoLR_dsid' + str(dsid) + '.eps')
        pylab.savefig(plotfiles[p],dpi=600)
        
        p += 1
        """
        fig = pylab.figure()
        zi = matplotlib.mlab.griddata(assoc_rho,assoc_lr,assoc_dist,rhoi,lri)
        cs = pylab.contour(rhoi,lri,zi,15,linewidths=0.5,colors='k')
        cs = pylab.contourf(rhoi,lri,zi,15,cmap=pylab.cm.jet)
        pylab.colorbar()
        pylab.scatter(assoc_rho,assoc_lr,marker='o',c='b',s=5)
        pylab.xlim(min(assoc_rho),max(assoc_rho))
        pylab.ylim(min(assoc_lr),max(assoc_lr))
        pylab.xlabel(r'dimensionless radius $\rho$')
        pylab.ylabel('log LR')
        pylab.grid(True)
        pylab.title('rho, LR, distance for dataset ' + str(dsid) )
        plotfiles.append('contour_xtrcat_' + str(catid) + '_rhoLRdist_dsid' + str(dsid) + '.eps')
        pylab.savefig(plotfiles[p],dpi=600)

        return plotfiles
    except db.Error, e:
        logging.warn("contourX2XDistLRRho() for dsid %s failed " % (str(dsid)))
        raise
    

def contourX2XDistLRRho(conn,dsid):
    try:
        cursor = conn.cursor()
        cursor.execute("select xtrsrc_id " + \
                       "      ,assoc_xtrsrc_id " + \
                       "      ,cast(1 + floor(10 * assoc_distance_arcsec) as integer) as bin_dist " + \
                       "      ,assoc_distance_arcsec " + \
                       "      ,assoc_r " + \
                       "      ,assoc_lr " + \
                       "  from assocxtrsources " + \
                       "      ,extractedsource " + \
                       "      ,images " + \
                       " where xtrsrc_id = xtrsrcid " + \
                       "   and image_id = imageid " + \
                       "   and xtrsrc_id <> assoc_xtrsrc_id " + \
                       "   and dataset = %s " + \
                       "order by assoc_distance_arcsec ", (dsid,))
        y = cursor.fetchall()
        cursor.close()
        xtrsrcid = []
        assoc_id = []
        bin_dist = []
        assoc_dist = []
        assoc_rho = []
        assoc_lr = []
        for i in range(len(y)):
            xtrsrcid.append(y[i][0])
            assoc_id.append(y[i][1])
            bin_dist.append(y[i][2])
            assoc_dist.append(y[i][3])
            assoc_rho.append(y[i][4])
            assoc_lr.append(y[i][5])
        
        disti = pylab.linspace(min(assoc_dist),max(assoc_dist),100)
        rhoi = pylab.linspace(min(assoc_rho),max(assoc_rho),100)
        lri = pylab.linspace(min(assoc_lr),max(assoc_lr),100)
        
        plotfiles = []
        p = 0
        """
        fig = pylab.figure()
        zi = matplotlib.mlab.griddata(assoc_dist,assoc_lr,assoc_rho,disti,lri)
        cs = pylab.contour(disti,lri,zi,15,linewidths=0.5,colors='k')
        cs = pylab.contourf(disti,lri,zi,15,cmap=pylab.cm.jet)
        pylab.colorbar()
        pylab.scatter(assoc_dist,assoc_lr,marker='o',c='b',s=5)
        pylab.xlim(min(assoc_dist),max(assoc_dist))
        pylab.ylim(min(assoc_lr),max(assoc_lr))
        pylab.xlabel('distance [arcsec]')
        pylab.ylabel('log LR')
        pylab.grid(True)
        pylab.title('Distance, LR, rho for dataset ' + str(dsid) )
        plotfiles.append('contour_distLRrho_dsid' + str(dsid) + '.eps')
        pylab.savefig(plotfiles[p],dpi=600)

        p += 1
        fig = pylab.figure()
        zi = matplotlib.mlab.griddata(assoc_dist,assoc_rho,assoc_lr,disti,rhoi)
        cs = pylab.contour(disti,rhoi,zi,15,linewidths=0.5,colors='k')
        cs = pylab.contourf(disti,rhoi,zi,15,cmap=pylab.cm.jet)
        pylab.colorbar()
        pylab.scatter(assoc_dist,assoc_rho,marker='o',c='b',s=5)
        pylab.xlim(min(assoc_dist),max(assoc_dist))
        pylab.ylim(min(assoc_rho),max(assoc_rho))
        pylab.xlabel('distance [arcsec]')
        pylab.ylabel(r'dimensionless radius $r$')
        pylab.grid(True)
        pylab.title('Distance, rho, LR for dataset ' + str(dsid) )
        plotfiles.append('contour_distrhoLR_dsid' + str(dsid) + '.eps')
        pylab.savefig(plotfiles[p],dpi=600)
        
        p += 1
        """
        fig = pylab.figure()
        zi = matplotlib.mlab.griddata(assoc_rho,assoc_lr,assoc_dist,rhoi,lri)
        cs = pylab.contour(rhoi,lri,zi,15,linewidths=0.5,colors='k')
        cs = pylab.contourf(rhoi,lri,zi,15,cmap=pylab.cm.jet)
        pylab.colorbar()
        pylab.scatter(assoc_rho,assoc_lr,marker='o',c='b',s=5)
        pylab.xlim(min(assoc_rho),max(assoc_rho))
        pylab.ylim(min(assoc_lr),max(assoc_lr))
        pylab.xlabel(r'dimensionless positional difference, $r$')
        pylab.ylabel(r'Log Likelihood Ratio, $\log LR$')
        pylab.grid(True)
        #pylab.title(r'$r, \log LR, \Delta\theta$ for association pairs in dataset ' + str(dsid) )
        plotfiles.append('sim_contour_rhoLRdist_dsid' + str(dsid) + '.eps')
        pylab.savefig(plotfiles[p],dpi=600)

        return plotfiles
    except db.Error, e:
        logging.warn("contourX2XDistLRRho() for dsid %s failed " % (str(dsid)))
        raise
    

def plotLightCurveLevelVar_v1(conn,dsid,level=None):
    """
    This makes a lightcurve plot of the sources that have a
    variability of sigma over mu higher than 'level'.
    """
    if not level:
        level = 1

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT t.xtrsrc_id " + \
                       "      ,t.v1 " + \
                       "  FROM (SELECT ax2.xtrsrc_id " + \
                       "              ,sqrt(count(*) " + \
                       "                   * (avg(x2.i_int * x2.i_int) - avg(x2.i_int) * avg(x2.i_int)) " + \
                       "                   / (count(*)-1)) " + \
                       "               / avg(x2.i_int) as v1 " + \
                       "          FROM assocxtrsources ax2 " + \
                       "              ,extractedsource x1 " + \
                       "              ,extractedsource x2 " + \
                       "              ,images im1 " + \
                       "         WHERE ax2.xtrsrc_id = x1.xtrsrcid " + \
                       "           AND ax2.assoc_xtrsrc_id = x2.xtrsrcid " + \
                       "           AND x1.image = im1.imageid " + \
                       "           AND im1.dataset = %s " + \
                       "        GROUP BY ax2.xtrsrc_id " + \
                       "       ) t " + \
                       " WHERE t.v1 >= %s ", (dsid, level))
        y = cursor.fetchall()
        cursor.close()
        
        xtrsrcid = []
        sigmu = []
        
        for i in range(len(y)):
            xtrsrcid.append(y[i][0])
            sigmu.append(y[i][1])
        
        plotfiles = []
        for i in range(len(xtrsrcid)):
            plotfiles.append(dbplots.plotLightCurveSecByXSource(xtrsrcid[i],conn))
        
        for i in range(len(plotfiles)):
            os.rename(plotfiles[i], 'sigmu_' + str(round(sigmu[i],3)) +'_' + plotfiles[i])
            plotfiles[i] = 'sigmu_' + str(round(sigmu[i],3)) +'_' + plotfiles[i]
        
        return plotfiles
    except db.Error, e:
        logging.warn("plotLightCurveLevelSigmaOverMu failed for dsid = " % (str(dsid)))
        raise
    

def plotLightCurveMaxVar_v1(dsid,conn):
    """
    This makes a lightcurve plot of the source that has the maximum value of sigma over mu
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT t.xtrsrc_id " + \
                       "      ,t.sigma_over_mu " + \
                       "  FROM (SELECT ax2.xtrsrc_id " + \
                       "              ,sqrt(count(*) * (avg(x2.i_int * x2.i_int) - avg(x2.i_int) * avg(x2.i_int))/ (count(*)-1)) /avg(x2.i_int) as sigma_over_mu " + \
                       "          FROM assocxtrsources ax2 " + \
                       "              ,extractedsource x1 " + \
                       "              ,extractedsource x2 " + \
                       "              ,images im1 " + \
                       "         WHERE ax2.xtrsrc_id = x1.xtrsrcid " + \
                       "           AND ax2.assoc_xtrsrc_id = x2.xtrsrcid " + \
                       "           AND x1.image = im1.imageid " + \
                       "           AND im1.dataset = %s " + \
                       "        GROUP BY ax2.xtrsrc_id " + \
                       "        HAVING COUNT(*) > 1 " + \
                       "       ) t " + \
                       " WHERE t.sigma_over_mu = (SELECT MAX(t0.sigma_over_mu) " + \
                       "                            FROM (SELECT sqrt(count(*) * (avg(x2.i_int * x2.i_int) - avg(x2.i_int) * avg(x2.i_int)) / (count(*) - 1)) / avg(x2.i_int) AS sigma_over_mu " + \
                       "                                    FROM assocxtrsources ax2 " + \
                       "                                        ,extractedsource x1 " + \
                       "                                        ,extractedsource x2 " + \
                       "                                        ,images im1 " + \
                       "                                   WHERE ax2.xtrsrc_id = x1.xtrsrcid " + \
                       "                                     AND ax2.assoc_xtrsrc_id = x2.xtrsrcid " + \
                       "                                     AND x1.image = im1.imageid " + \
                       "                                     AND im1.dataset = %s " + \
                       "                                  GROUP BY ax2.xtrsrc_id " + \
                       "                                  HAVING COUNT(*) > 1 " + \
                       "                                 ) t0 " + \
                       "                         ) ", (dsid, dsid))
        y = cursor.fetchall()
        cursor.close()
        
        xtrsrcid = []
        sigmu = []
        
        for i in range(len(y)):
            xtrsrcid.append(y[i][0])
            sigmu.append(y[i][1])
        
        plotfiles = []
        for i in range(len(xtrsrcid)):
            plotfiles.append(dbplots.plotLightCurveSecByXSource(xtrsrcid[i],conn))

        for i in range(len(plotfiles)):
            os.rename(plotfiles[i], 'sigmumax_' + str(round(sigmu[i],3)) +'_' + plotfiles[i])
            plotfiles[i] = 'sigmumax_' + str(round(sigmu[i],3)) +'_' + plotfiles[i]
        
        return plotfiles
    except db.Error, e:
        logging.warn("plotLightCurveMaxVar_v1 failed for dsid = " % (str(dsid)))
        raise
    

def plotLightCurveMaxVar_v2(dsid,conn):
    """
    This makes a lightcurve plot of the source that has the maximum value of sigma over mu
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT t.xtrsrc_id " + \
                       "      ,t.var_v2 " + \
                       "  FROM (SELECT ax2.xtrsrc_id " + \
                       "              ,avg(x2.i_int * x2.i_int / (x2.i_int_err * x2.i_int_err)) " + \
                       "               - 2 * avg(x2.i_int / (x2.i_int_err * x2.i_int_err)) * avg(x2.i_int) " + \
                       "               + avg(1 / (x2.i_int_err * x2.i_int_err)) * avg(x2.i_int) * avg(x2.i_int) as var_v2 " + \
                       "          FROM assocxtrsources ax2 " + \
                       "              ,extractedsource x1 " + \
                       "              ,extractedsource x2 " + \
                       "              ,images im1 " + \
                       "         WHERE ax2.xtrsrc_id = x1.xtrsrcid " + \
                       "           AND ax2.assoc_xtrsrc_id = x2.xtrsrcid " + \
                       "           AND x1.image = im1.imageid " + \
                       "           AND im1.dataset = %s " + \
                       "        GROUP BY ax2.xtrsrc_id " + \
                       "        HAVING COUNT(*) > 1 " + \
                       "       ) t " + \
                       " WHERE t.var_v2 = (SELECT MAX(t0.var_v2) " + \
                       "                     FROM (SELECT avg(x2.i_int * x2.i_int / (x2.i_int_err * x2.i_int_err)) " + \
                       "                                  - 2 * avg(x2.i_int / (x2.i_int_err * x2.i_int_err)) * avg(x2.i_int) " + \
                       "                                  + avg(1 / (x2.i_int_err * x2.i_int_err)) * avg(x2.i_int) * avg(x2.i_int) as var_v2 " + \
                       "                             FROM assocxtrsources ax2 " + \
                       "                                 ,extractedsource x1 " + \
                       "                                 ,extractedsource x2 " + \
                       "                                 ,images im1 " + \
                       "                            WHERE ax2.xtrsrc_id = x1.xtrsrcid " + \
                       "                              AND ax2.assoc_xtrsrc_id = x2.xtrsrcid " + \
                       "                              AND x1.image = im1.imageid " + \
                       "                              AND im1.dataset = %s " + \
                       "                           GROUP BY ax2.xtrsrc_id " + \
                       "                           HAVING COUNT(*) > 1 " + \
                       "                          ) t0 " + \
                       "                  ) ", (dsid, dsid))
        y = cursor.fetchall()
        cursor.close()
        
        xtrsrcid = []
        sigmu = []
        
        for i in range(len(y)):
            xtrsrcid.append(y[i][0])
            sigmu.append(y[i][1])
        
        plotfiles = []
        for i in range(len(xtrsrcid)):
            plotfiles.append(dbplots.plotLightCurveSecByXSource(xtrsrcid[i],conn))

        for i in range(len(plotfiles)):
            os.rename(plotfiles[i], 'var_v2_max_' + str(round(sigmu[i],3)) +'_' + plotfiles[i])
            plotfiles[i] = 'var_v2_max_' + str(round(sigmu[i],3)) +'_' + plotfiles[i]
        
        return plotfiles
    except db.Error, e:
        logging.warn("plotLightCurveMaxVar_v2 failed for dsid = " % (str(dsid)))
        raise
    

def scatterVar_v1_v2_X2X(dsid,conn):
    """
    This makes a plot of the sigma over mu's for the associated sources
    (X2X: eXtractedsources <-> eXtractedsources)
    We discriminate between sources having less than half the number of associations 
    (default < 15) and the ones having more than half.
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT ax2.xtrsrc_id " + \
                       "      ,count(*) as datapoints " + \
                       "      ,1000 * min(x2.i_int) as min_i_int_mJy " + \
                       "      ,1000 * avg(x2.i_int) as avg_i_int_mJy " + \
                       "      ,1000 * max(x2.i_int) as max_i_int_mJy " + \
                       "      ,sqrt(count(*) " + \
                       "           * (avg(x2.i_int * x2.i_int) - avg(x2.i_int) * avg(x2.i_int)) " + \
                       "           / (count(*)-1) " + \
                       "           ) / avg(x2.i_int) as sigma_over_mu " + \
                       "      ,avg((x2.i_int / x2.i_int_err) * (x2.i_int / x2.i_int_err)) " + \
                       "       - 2 * avg(x2.i_int) * avg(x2.i_int / (x2.i_int_err * x2.i_int_err)) " + \
                       "       + avg(x2.i_int) * avg(x2.i_int) * avg(1 / (x2.i_int_err * x2.i_int_err)) as chi2 " + \
                       "  FROM assocxtrsources ax2 " + \
                       "      ,extractedsource x1 " + \
                       "      ,extractedsource x2 " + \
                       "      ,images im1 " + \
                       " WHERE ax2.xtrsrc_id = x1.xtrsrcid " + \
                       "   AND ax2.assoc_xtrsrc_id = x2.xtrsrcid " + \
                       "   AND x1.image = im1.imageid " + \
                       "   AND im1.dataset = %s " + \
                       "GROUP BY ax2.xtrsrc_id " + \
                       "HAVING COUNT(*) > 1 " + \
                       "ORDER BY datapoints " + \
                       "        ,ax2.xtrsrc_id ", (dsid,))
        y = cursor.fetchall()
        cursor.close()
        
        xtrsrcids_upper = []
        xtrsrcids_lower = []
        sig_over_mu_upper = []
        sig_over_mu_lower = []
        chi2_lower = []
        chi2_upper = []
        
        for i in range(len(y)):
            if (y[i][1] > 15):
                xtrsrcids_upper.append(y[i][0])
                sig_over_mu_upper.append(y[i][5])
                chi2_upper.append(y[i][6])
            else:
                xtrsrcids_lower.append(y[i][0])
                sig_over_mu_lower.append(y[i][5])
                chi2_lower.append(y[i][6])
        
        plotfiles=[]
        p = 0
        fig = pylab.figure()
        ax1 = fig.add_subplot(111)
        ax1.set_xlabel(r'Extracted Source ID')
        ax1.set_ylabel(r'Variability Index 1, $v_1$')
        #for tl in ax1.get_yticklabels():
        #    tl.set_color('r')
        if (len(xtrsrcids_upper) > 1):
            ax1.scatter(xtrsrcids_upper, sig_over_mu_upper, color='r', marker='o',label='gt 15')
        if (len(xtrsrcids_lower) > 1):
            #print "len(xtrsrcids_lower):",len(xtrsrcids_lower)
            #print "xtrsrcids_lower:",xtrsrcids_lower
            #print "sig_over_mu_lower:",sig_over_mu_lower
            ax1.scatter(xtrsrcids_lower, sig_over_mu_lower, color='b', marker='s',label='le 15')
        ax1.grid(True)
        #pylab.xlim(0,70)
        #pylab.legend(numpoints=1,loc='best')
        #pylab.title(r'Variability, $v_1$, for extracted sources ' + \
        #            'in dataset ' + str(dsid))
        plotfiles.append('tsigmaovermu_dsid' + str(dsid) + '.eps')
        pylab.savefig(plotfiles[p],dpi=600)
        
        p += 1
        fig = pylab.figure()
        ax1 = fig.add_subplot(111)
        ax1.set_xlabel(r'Extracted Source ID')
        ax1.set_ylabel(r'Log of Variability Index 2, $\log v_2$')
        #print chi2_upper
        #for tl in ax1.get_yticklabels():
        #    tl.set_color('r')
        if (len(xtrsrcids_upper) > 1):
            ax1.scatter(xtrsrcids_upper, pylab.log10(chi2_upper), color='r', marker='o',label='gt 15')
        if (len(xtrsrcids_lower) > 1):
            #print "len(xtrsrcids_lower):",len(xtrsrcids_lower)
            #print "xtrsrcids_lower:",xtrsrcids_lower
            #print "sig_over_mu_lower:",sig_over_mu_lower
            ax1.scatter(xtrsrcids_lower, chi2_lower, color='b', marker='s',label='le 15')
        ax1.grid(True)
        #pylab.xlim(0,70)
        #pylab.legend(numpoints=1,loc='best')
        #pylab.title(r'Variability, $v_2$, for extracted sources ' + \
        #            'in dataset ' + str(dsid))
        plotfiles.append('chi2_dsid' + str(dsid) + '.eps')
        pylab.savefig(plotfiles[p],dpi=600)

        return plotfiles
    except db.Error, e:
        logging.warn("scatterVar_v1_v2_X2X() for dsid %s failed " % (str(dsid)))
        raise
    

def plotSigmaMuAssocs2XtrByDsid(dsid,cnt,conn):
    """
    This method makes two plots.
    Q1: A plot of the number of extractedsource per image
    Q2: A histogram of the number of associations
    that could be made per extractedsource throughout all the 
    processed images.
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT ax2.xtrsrc_id " + \
                       "      ,count(*) as datapoints " + \
                       "      ,1000 * min(x2.i_int) as min_i_int_mJy " + \
                       "      ,1000 * avg(x2.i_int) as avg_i_int_mJy " + \
                       "      ,1000 * max(x2.i_int) as max_i_int_mJy " + \
                       "      ,sqrt(count(*) * (avg(x2.i_int * x2.i_int) - avg(x2.i_int) * avg(x2.i_int))/ (count(*)-1))/avg(x2.i_int) as sigma_over_mu " + \
                       "  FROM assocxtrsources ax2 " + \
                       "      ,extractedsource x1 " + \
                       "      ,extractedsource x2 " + \
                       "      ,images im1 " + \
                       " WHERE ax2.xtrsrc_id = x1.xtrsrcid " + \
                       "   AND ax2.assoc_xtrsrc_id = x2.xtrsrcid " + \
                       "   AND x1.image = im1.imageid " + \
                       "   AND im1.dataset = %s " + \
                       "GROUP BY ax2.xtrsrc_id " + \
                       "HAVING COUNT(*) = %s " + \
                       "ORDER BY datapoints " + \
                       "        ,ax2.xtrsrc_id ", (dsid,cnt))
        y = cursor.fetchall()
        cursor.close()
        
        xtrsrcids = []
        dtpnts_grp = []
        sig_mu = []
        """
        # we skip sources with 1 datapoint
        ndatapoints = 1
        idx = -1
        print 'len(y):',len(y)
        for i in range(len(y)):
            #print 'i:',i
            #print 'before idx:',idx
            #print 'ndatapoints:',ndatapoints
            #print 'y[',i,'][1]:',y[i][1]
            if ndatapoints == y[i][1]:
                #print 'in if idx:',idx
                xtrsrcids[idx].append(y[i][0])
                sig_mu[idx].append(y[i][5])
            else:
                ndatapoints = ndatapoints + 1
                #print 'ndatapoints:',ndatapoints
                xtrsrcids.append([])
                sig_mu.append([])
                idx = idx + 1
                #print 'in else idx:',idx
                xtrsrcids[idx].append(y[i][0])
                sig_mu[idx].append(y[i][5])
        """
        for i in range(len(y)):
            xtrsrcids.append(y[i][0])
            sig_mu.append(y[i][5])
        
        plotfiles=[]
        p = 0
        fig = pylab.figure()
        ax1 = fig.add_subplot(111)
        #for i in range(len(sig_mu)):
        #width = 1./len(sig_mu[i])
        width = 1./len(sig_mu)
        ind = pylab.arange(0,1,width)
        if (len(sig_mu) < 10):
            every = 1
        else:
            every = len(sig_mu) / 10
        ax1.set_xticks((ind + width / 2.)[::every])
        #ax1.set_xticklabels(xtrsrcids[i])
        ax1.set_xticklabels(xtrsrcids[::every])
        ax1.set_xlabel('xtrsrcid')
        ax1.set_ylabel('Sigma over Average ', color='r')
        for tl in ax1.get_yticklabels():
            tl.set_color('r')
        #ax1.plot(ind + width / 2., sig_mu[i], linewidth=2)
        ax1.plot(ind + width / 2., sig_mu, color='b',linewidth=2)
        ax1.grid(True)
        pylab.title('Sigma over mu for extracted sources \n' + \
                    'in dataset ' + str(dsid))
        plotfiles.append('plot_sigmamu_cnt' + str(cnt) + '_dsid' + str(dsid) + '.eps')
        pylab.savefig(plotfiles[p],dpi=600)
        
        return plotfiles
    except db.Error, e:
        logging.warn("Retrieving info for dsid %s failed: " % (str(dsid)))
        raise
    

def plotSourcesPerImage(dsid,conn):
    """
    This makes a plot file of the all the images in the dataset (x-axis)
    against the number of sources detected in an image (y-axis)
    """
    try:
        cursor = conn.cursor()
        cursor.execute("select image_id " + \
                       "      ,count(*) " + \
                       "  from extractedsource " + \
                       "      ,images " + \
                       " where image_id = imageid " + \
                       "   and dataset = %s " + \
                       "group by image_id " + \
                       "order by image_id ", (dsid,))
        z = cursor.fetchall()
        # this is the image_id (used as bin_nr)
        imgid = []
        # this is the number of sources extracted from each image
        src_img = []
        for i in range(len(z)):
            imgid.append(z[i][0])
            src_img.append(z[i][1])

        plotfiles = []
        p = 0
        fig = pylab.figure()
        ax1 = fig.add_subplot(111)
        # we do not want more than 10 labels on the xaxis
        if (len(z) < 10):
            every = 1
        else:
            every = len(z) / 10
        ax1.set_xticks(imgid[::every])
        ax1.set_xticklabels(imgid[::every])
        ax1.set_xlabel('image_id')
        ax1.set_ylabel('Number of sources ', color='b')
        for tl in ax1.get_yticklabels():
            tl.set_color('b')
        ax1.plot(imgid, src_img, color='b',linewidth=2)
        ax1.grid(True)
        pylab.title('Number of extracted sources per image \n' + \
                    'in dataset ' + str(dsid))
        plotfiles.append('plot_sourcesperimg_dsid' + str(dsid) + '.eps')
        pylab.savefig(plotfiles[p],dpi=600)
        
        return plotfiles
    except db.Error, e:
        logging.warn("plotSourcesPerImage failed for dsid =  %s " % (str(dsid)))
        raise
    

def histNumberOfAssociations(dsid,conn):
    """
    This makes a barchart of how many times a source could be associated through all
    the images being processed.
    x-axis: bins of the number of times a source could be associated
    y-axis: the number of sources belonging to a bin
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT assoc_cnt " + \
                       "      ,COUNT(*) " + \
                       "  FROM (SELECT xtrsrc_id " + \
                       "              ,COUNT(*) AS assoc_cnt " + \
                       "          FROM assocxtrsources " + \
                       "              ,extractedsource " + \
                       "              ,images " + \
                       "         WHERE xtrsrc_id = xtrsrcid " + \
                       "           AND image_id = imageid " + \
                       "           AND dataset = %s " + \
                       "        GROUP BY xtrsrc_id " + \
                       "       ) t " + \
                       "GROUP BY t.assoc_cnt " + \
                       "ORDER BY t.assoc_cnt ", (dsid,))
        y = cursor.fetchall()
        cursor.close()
        
        # this is the number of associations that could be made for a source
        assoc_cnt = []
        # this is the number of sources having assoc_cnt associations
        num = []
        for i in range(len(y)):
            assoc_cnt.append(y[i][0])
            num.append(y[i][1])
        
        plotfiles=[]
        p = 0
        fig = pylab.figure()
        ax1 = fig.add_subplot(111)
        width = 1./len(y)
        ind = pylab.arange(0,1,width)
        ax1.set_xticks((ind + width / 2.))
        ax1.set_xticklabels(assoc_cnt)
        ax1.set_xlabel('Number of Associations')
        ax1.set_ylabel('Number of sources ', color='r')
        for tl in ax1.get_yticklabels():
            tl.set_color('r')
        rects = ax1.bar(ind, num, width, color='r')
        ax1.grid(True)
        pylab.title('Number of associations for xtr-xtr sources \n' + \
                    'in dataset ' + str(dsid))
        plotfiles.append('hist_xtrxtrassocs_dsid' + str(dsid) + '.eps')
        pylab.savefig(plotfiles[p],dpi=600)
        
        return plotfiles
    except db.Error, e:
        logging.warn("Retrieving info for dsid %s failed: " % (str(dsid)))
        raise
    

def plotXtrBarLR(dsid, conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT bin_nr " + \
                       "      ,COUNT(*) " + \
                       "      ,AVG(assoc_distance_arcsec) " + \
                       "      ,MIN(assoc_distance_arcsec) " + \
                       "      ,MAX(assoc_distance_arcsec) " + \
                       "      ,AVG(assoc_r) " + \
                       "      ,MIN(assoc_r) " + \
                       "      ,MAX(assoc_r) " + \
                       "  FROM (SELECT CAST(1 + FLOOR(2 * assoc_lr) AS INTEGER) AS bin_nr " + \
                       "              ,ax1.assoc_lr " + \
                       "              ,ax1.assoc_distance_arcsec " + \
                       "              ,ax1.assoc_r " + \
                       "          FROM assocxtrsources ax1 " + \
                       "              ,extractedsource x1 " + \
                       "              ,images im1 " + \
                       "         WHERE ax1.xtrsrc_id = x1.xtrsrcid " + \
                       "           AND ax1.xtrsrc_id <> ax1.assoc_xtrsrc_id " + \
                       "           AND ax1.assoc_lr >= -100.5 " + \
                       "           AND x1.image = im1.imageid " + \
                       "           AND im1.dataset = %s " + \
                       "       ) t " + \
                       "GROUP BY bin_nr " + \
                       "ORDER BY bin_nr ", (dsid,))
        y = cursor.fetchall()
        cursor.close()
        bins = []
        x = []
        dist = []
        mindist = []
        maxdist = []
        assoc_r = []
        minassoc_r = []
        maxassoc_r = []
        for i in range(len(y)):
            # divide by 2 because we bin every log lr = 0.5
            bins.append(y[i][0]/2.)
            x.append(y[i][1])
            dist.append(y[i][2])
            mindist.append(y[i][3])
            maxdist.append(y[i][4])
            assoc_r.append(y[i][5])
            minassoc_r.append(y[i][5])
            maxassoc_r.append(y[i][5])
        
        width = 1./len(x)
        ind = pylab.arange(0, 1, width)  # the x locations for the groups
        
        xlog = pylab.log10(x)
        xsum = 0
        for i in range(len(x)):
            xsum = xsum + x[i]
        xnorm = []
        for i in range(len(x)):
            xnorm.append(x[i]/xsum)
        
        plotfiles=[]
        p=0
        pylab.figure()
        pylab.xticks((ind+width/2.),bins)
        pylab.xlabel('log LR')
        pylab.ylabel('N (log LR)')
        pylab.title('Distribution of log(LR) for \n ' + \
                    'xtr-xtr candidate associations in dataset ' + str(dsid) )
        pylab.grid(True)
        rects = pylab.bar(ind, x, width, color='r')
        plotfiles.append('hist_xtrxtrassocs_binlr_dsid' + str(dsid) + '.eps')
        pylab.savefig(plotfiles[p],dpi=600)
        
        p = p + 1
        every = 1
        fig = pylab.figure()
        ax1 = fig.add_subplot(111)
        ax1.set_xticks((ind+width/2.)[::every])
        ax1.set_xticklabels(bins[::every])
        ax1.set_xlabel('log LR')
        ax1.set_ylabel('log N (log LR)', color='r')
        for tl in ax1.get_yticklabels():
            tl.set_color('r')
        rects = ax1.bar(ind, xlog, width, color='r', edgecolor='r')
        ax1.grid(True)
        
        ax2 = ax1.twinx()
        ax2.set_xticks((ind+width/2.)[::every])
        ax2.set_xticklabels(bins[::every])
        #ax2.set_yticks([0,10,20,30,40,50,60,70,80,90,100])
        #ax2.set_yticklabels((0,10,20,30,40,50,60,70,80,90,100))
        ax2.set_ylabel('distance [arcsec]', color='b')
        for tl in ax2.get_yticklabels():
            tl.set_color('b')
        ax2.plot(ind+width/2., dist, 'b-', linewidth=2)
        ax2.plot(ind+width/2., mindist, 'y-', linewidth=2)
        ax2.plot(ind+width/2., maxdist, 'g-', linewidth=2)

        pylab.title('Distribution of log(LR) and distances for \n ' + \
                    'xtr-xtr associations in dataset ' + str(dsid))
        plotfiles.append('hist_xtrxtrassocs_binlrdist_dsid' + str(dsid) + '.eps')
        pylab.savefig(plotfiles[p],dpi=600)
        
        p = p + 1
        fig = pylab.figure()
        ax1 = fig.add_subplot(111)
        every = 1
        ax1.set_xticks((ind+width/2.)[::every])
        ax1.set_xticklabels(bins[::every])
        ax1.set_xlabel('log LR')
        ax1.set_ylabel('log N (log LR)', color='r')
        for tl in ax1.get_yticklabels():
            tl.set_color('r')
        rects = ax1.bar(ind, xlog, width, color='r', edgecolor='r')
        ax1.grid(True)
        
        ax2 = ax1.twinx()
        ax2.set_xticks((ind+width/2.)[::every])
        ax2.set_xticklabels(bins[::every])
        ax2.set_ylabel(r'average dimensionless distance $\rho$', color='b')
        for tl in ax2.get_yticklabels():
            tl.set_color('b')
        ax2.plot(ind+width/2., assoc_r, 'b-', linewidth=2)
        #ax2.plot(ind, minassoc_r, 'y-', linewidth=2)
        #ax2.plot(ind, maxassoc_r, 'g-', linewidth=2)

        pylab.title('Distribution of log(LR) and dim.less dist for \n ' + \
                    'xtr-xtr candidate associations in dataset ' + str(dsid))
        plotfiles.append('hist_xtrxtrassocs_binlrrho_dsid' + str(dsid) + '.eps')
        pylab.savefig(plotfiles[p],dpi=600)
        
        return plotfiles
    except db.Error, e:
        logging.warn("Retrieving info for dsid %s failed: " % (str(dsid)))
        raise
    

def plotCatBarLR(dsid, catid,conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT bin_nr " + \
                       "      ,COUNT(*) " + \
                       "      ,AVG(assoc_distance_arcsec) " + \
                       "      ,MIN(assoc_distance_arcsec) " + \
                       "      ,MAX(assoc_distance_arcsec) " + \
                       "      ,AVG(assoc_r) " + \
                       "      ,MIN(assoc_r) " + \
                       "      ,MAX(assoc_r) " + \
                       "  FROM (SELECT CAST(1 + FLOOR(2 * assoc_lr) AS INTEGER) AS bin_nr " + \
                       "              ,ac1.assoc_lr " + \
                       "              ,ac1.assoc_distance_arcsec " + \
                       "              ,ac1.assoc_r " + \
                       "          FROM assoccatsources ac1 " + \
                       "              ,extractedsource x1 " + \
                       "              ,images im1 " + \
                       "              ,lsm lsm1 " + \
                       "         WHERE ac1.xtrsrc_id = x1.xtrsrcid " + \
                       "           AND ac1.assoc_lr >= -100.5 " + \
                       "           AND x1.image = im1.imageid " + \
                       "           AND ac1.assoc_catsrc_id = lsm1.lsmid " + \
                       "           AND im1.dataset = %s " + \
                       "           AND lsm1.cat_id = %s " + \
                       "       ) t " + \
                       "GROUP BY bin_nr " + \
                       "ORDER BY bin_nr ", (dsid,catid))
        y = cursor.fetchall()
        cursor.close()
        bins = []
        x = []
        dist = []
        mindist = []
        maxdist = []
        assoc_r = []
        minassoc_r = []
        maxassoc_r = []
        for i in range(len(y)):
            # divide by 2 because we bin every log lr = 0.5
            bins.append(y[i][0]/2.)
            x.append(y[i][1])
            dist.append(y[i][2])
            mindist.append(y[i][3])
            maxdist.append(y[i][4])
            assoc_r.append(y[i][5])
            minassoc_r.append(y[i][5])
            maxassoc_r.append(y[i][5])
        
        width = 1./len(x)
        ind = pylab.arange(0, 1, width)  # the x locations for the groups
        
        xlog = pylab.log10(x)
        xsum = 0
        for i in range(len(x)):
            xsum = xsum + x[i]
        xnorm = []
        for i in range(len(x)):
            xnorm.append(x[i]/xsum)
        
        plotfiles=[]
        p=0
        every = 5
        fig = pylab.figure()
        ax1 = fig.add_subplot(111)
        ax1.set_xticks((ind+width/2.),bins[::every])
        ax1.set_xticklabels(bins[::every])
        ax1.set_xlabel('log LR')
        ax1.set_ylabel('N (log LR)')
        for tl in ax1.get_yticklabels():
            tl.set_color('r')
        rects = ax1.bar(ind, x, width, color='r')
        ax1.grid(True)
        pylab.title('Distribution of log(LR) for \n ' + \
                    'xtr-nvss candidate associations in dataset ' + str(dsid) )
        plotfiles.append('hist_xtrcatassocs_binlr_dsid' + str(dsid) + '.eps')
        pylab.savefig(plotfiles[p],dpi=600)
        
        p = p + 1
        fig = pylab.figure()
        ax1 = fig.add_subplot(111)
        ax1.set_xticks((ind+width/2.)[::every])
        ax1.set_xticklabels(bins[::every])
        ax1.set_xlabel('log LR')
        ax1.set_ylabel('log N (log LR)', color='r')
        for tl in ax1.get_yticklabels():
            tl.set_color('r')
        rects = ax1.bar(ind, xlog, width, color='r', edgecolor='r')
        ax1.grid(True)
        
        ax2 = ax1.twinx()
        ax2.set_xticks((ind+width/2.)[::every])
        ax2.set_xticklabels(bins[::every])
        #ax2.set_yticks([0,10,20,30,40,50,60,70,80,90,100])
        #ax2.set_yticklabels((0,10,20,30,40,50,60,70,80,90,100))
        ax2.set_ylabel('distance [arcsec]', color='b')
        for tl in ax2.get_yticklabels():
            tl.set_color('b')
        ax2.plot(ind+width/2., dist, 'b-', linewidth=2)
        ax2.plot(ind+width/2., mindist, 'y-', linewidth=2)
        ax2.plot(ind+width/2., maxdist, 'g-', linewidth=2)

        pylab.title('Distribution of log(LR) and distances for \n ' + \
                    'xtr-nvss associations in dataset ' + str(dsid))
        plotfiles.append('hist_xtrcatassocs_binlrdist_dsid' + str(dsid) + '.eps')
        pylab.savefig(plotfiles[p],dpi=600)
        
        p = p + 1
        fig = pylab.figure()
        ax1 = fig.add_subplot(111)
        ax1.set_xticks((ind+width/2.)[::every])
        ax1.set_xticklabels(bins[::every])
        ax1.set_xlabel('log LR')
        ax1.set_ylabel('log N (log LR)', color='r')
        for tl in ax1.get_yticklabels():
            tl.set_color('r')
        rects = ax1.bar(ind, xlog, width, color='r', edgecolor='r')
        ax1.grid(True)
        
        ax2 = ax1.twinx()
        ax2.set_xticks((ind+width/2.)[::every])
        ax2.set_xticklabels(bins[::every])
        ax2.set_ylabel(r'average dimensionless distance $\rho$', color='b')
        for tl in ax2.get_yticklabels():
            tl.set_color('b')
        ax2.plot(ind+width/2., assoc_r, 'b-', linewidth=2)
        #ax2.plot(ind, minassoc_r, 'y-', linewidth=2)
        #ax2.plot(ind, maxassoc_r, 'g-', linewidth=2)

        pylab.title('Distribution of log(LR) and dim.less dist for \n ' + \
                    'xtr-nvss candidate associations in dataset ' + str(dsid))
        plotfiles.append('hist_xtrcatassocs_binlrrho_dsid' + str(dsid) + '.eps')
        pylab.savefig(plotfiles[p],dpi=600)
        
        return plotfiles
    except db.Error, e:
        logging.warn("Retrieving info for dsid %s failed: " % (str(dsid)))
        raise
