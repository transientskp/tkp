#
# LOFAR Transients Key Project
#

# Python standard library
import logging
import os
# Other external libraries
import pylab
from datetime import *
import time as tm
# Local tkp_lib functionality
import tkp.database.database as db

def plotHistAssocXtrDist(dsid, conn):
    """
    Not implemented
    #raise NotImplementedError
    """
    cursor = conn.cursor()
    x=[]
    try:
        query = "SELECT assoc_distance_arcsec " + \
                "  FROM assocxtrsource " + \
                "      ,extractedsource " + \
                "      ,images " + \
                " WHERE xtrsrc = xtrsrcid " +\
                "   AND image_id = imageid " +\
                "   AND dataset = " + str(dsid)
        cursor.execute(query)
        x = cursor.fetchall()
        #print "x:",x
        cursor.close()
        plotfiles = []
        fig = pylab.figure()
        pylab.hist(x,bins=50)
        pylab.grid(True)
        pylab.xlabel('distance [arcsec]')
        pylab.ylabel('Number of Sources')
        pylab.title('Distribution of distance between associated sources in dataset ' + str(dsid))
        plotfiles.append('histxtrdist_' + str(dsid) + '.eps')
        for i in range(len(plotfiles)):
            pylab.savefig(plotfiles[i],dpi=600)
        return plotfiles
    except db.Error, e:
        logging.warn("Retrieving info for dataset %s failed: " % (str(dsid)))
        logging.debug("Failed plotquery: %s" % (query))

def plotHistAssocCatDist(dsid, conn):
    """
    Not implemented
    #raise NotImplementedError
    """
    try:
        cursor = conn.cursor()
        query = "SELECT assoc_distance_arcsec " + \
                "  FROM assoccatsources " + \
                "      ,catalogedsources " + \
                "      ,images " + \
                "      ,extractedsource " + \
                " WHERE xtrsrc_id = xtrsrcid " +\
                "   AND image_id = imageid " +\
                "   AND assoc_catsrc_id = catsrcid " +\
                "   AND dataset = %d " %(dsid)
        cursor.execute(query)
        x = cursor.fetchall()
        print "x:",x
        cursor.close()
        #n, bins, patches = pylab.hist(x,50)
        pylab.hist(x,bins=20,normed=1)
        pylab.xlabel('Distance [arcsec]')
        pylab.ylabel('N')
        pylab.grid(True)
        pylab.title('Distance between extracted and cataloged sources')
        plotfile = 'histcatdist_' + str(dsid) + '.eps'
        pylab.savefig(plotfile,dpi=600)
        return plotfile
    except db.Error, e:
        logging.warn("Retrieving info for dataset %s failed: " % (str(dsid)))
        logging.warn("Failed on query %s : " % (query))
        logging.debug("Failed plotquery: %s" % (query))

def plotBarDist(dsid, catid, conn):
    try:
        cursor = conn.cursor()
        cursor.execute("select bin_dist " + \
                       "      ,count(*) " + \
                       "      ,avg(assoc_r) " + \
                       "      ,avg(assoc_lr) " + \
                       "  from (select cast(floor(assoc_distance_arcsec) as integer) as bin_dist " + \
                       "              ,assoc_r " + \
                       "              ,assoc_lr " + \
                       "         from assoccatsources ac1 " + \
                       "             ,extractedsource x1 " + \
                       "             ,images im1 " + \
                       "             ,obscatsources oc1 " + \
                       "        where ac1.xtrsrc = x1.id " + \
                       "         and assoc_lr >= -100 " + \
                       "         and x1.image = im1.id " + \
                       "         AND im1.dataset = %s " + \
                       "         and ac1.assoc_catsrc_id = oc1.obscatsrcid " + \
                       "         and oc1.cat_id = %s " + \
                       "       ) t " + \
                       "GROUP BY bin_dist " + \
                       "ORDER BY bin_dist", (dsid,catid))
        y = cursor.fetchall()
        cursor.close()
        bins = []
        x = []
        assoc_r = []
        assoc_lr = []
        for i in range(len(y)):
            bins.append(y[i][0])
            x.append(y[i][1])
            assoc_r.append(y[i][2])
            assoc_lr.append(y[i][3])
        
        xsum = 0
        for i in range(len(x)):
            xsum = xsum + x[i]
        
        width = 1./len(x)
        ind = pylab.arange(0, 1, width)  # the x locations for the groups
        
        xnorm = []
        for i in range(len(x)):
            xnorm.append(float(x[i]) / xsum)
        
        #print "bins=",bins
        #print "x=",x
        #print "dist=",dist
        #print "xnorm=",xnorm
        #print "xsum=",xsum

        plotfiles=[]
        p = 0
        fig = pylab.figure()
        ax1 = fig.add_subplot(111)
        ax1.set_xticks((ind+width/2.)[::20])
        ax1.set_xticklabels(bins[::20])
        ax1.set_xlabel('distance [arcsec]')
        ax1.set_ylabel('N', color='r')
        for tl in ax1.get_yticklabels():
            tl.set_color('r')
        #rects = ax1.bar(ind, x, width, color='r', edgecolor='r')
        rects = ax1.bar(ind, x, width, color='r', edgecolor='r')
        ax1.grid(True)
        
        """
        ax2 = ax1.twinx()
        ax2.set_xticks((ind+width/2.)[::20])
        ax2.set_xticklabels(bins[::20])
        i#ax2.set_yticks([])
        #ax2.set_yticklabels([])
        ax2.set_ylabel('Rayleigh distribution', color='b')
        ax2.plot(ind, assoc_r, 'b-', linewidth=2)
        """

        pylab.title('Distribution of distances for \n WENSS-NVSS candidate associations (' + str(xsum) + ')')
        #plotfiles.append('wenss-nvss_assocs_dist_dsid' + str(dsid) + '.eps')
        plotfiles.append('wenss-nvss_assocs_dist_dsid' + str(dsid) + '.eps')
        pylab.savefig(plotfiles[p],dpi=600)
        
        return plotfiles
    except db.Error, e:
        logging.warn("Retrieving info for dsid %s failed: " % (str(dsid)))
        logging.warn("Failed on query %s : " % (e))
        logging.debug("Failed plotquery: %s" % (e))

def plotBarRho(dsid, catid, conn):
    try:
        cursor = conn.cursor()
        cursor.execute("select bin_r " + \
                       "      ,count(*) " + \
                       "      ,avg(assoc_distance_arcsec) " + \
                       "      ,avg(assoc_r) " + \
                       "  from (select cast(floor(4*assoc_r) as integer) as bin_r " + \
                       "              ,assoc_distance_arcsec " + \
                       "              ,assoc_r " + \
                       "         from assoccatsources ac1 " + \
                       "             ,extractedsource x1 " + \
                       "             ,images im1 " + \
                       "             ,obscatsources oc1 " + \
                       "        where ac1.xtrsrc = x1.id " + \
                       "         and assoc_lr >= -300 " + \
                       "         and x1.image = im1.id " + \
                       "         AND im1.dataset = %s " + \
                       "         and ac1.assoc_catsrc_id = oc1.obscatsrcid " + \
                       "         and oc1.cat_id = %s " + \
                       "       ) t " + \
                       "GROUP BY bin_r " + \
                       "ORDER BY bin_r", (dsid,catid))
        y = cursor.fetchall()
        cursor.close()
        bins = []
        x = []
        dist = []
        assoc_r = []
        for i in range(len(y)):
            bins.append(y[i][0]/4.)
            x.append(y[i][1])
            dist.append(y[i][2])
            assoc_r.append(y[i][3])
        
        xks = []
        xsum = 0
        for i in range(len(x)):
            xsum = xsum + x[i]
            xks.append(xsum)
        
        width = 1./len(x)
        ind = pylab.arange(0, 1, width)  # the x locations for the groups
        
        xnorm = []
        for i in range(len(x)):
            xnorm.append(float(x[i]) / xsum)
        
        #print "bins=",bins
        print "x=",x
        #print "dist=",dist
        #print "xnorm=",xnorm
        #print "xsum=",xsum
        print "xks=",xks

        plotfiles=[]
        p = 0
        fig = pylab.figure()
        ax1 = fig.add_subplot(111)
        ax1.set_xticks((ind+width/2.)[::20])
        ax1.set_xticklabels(bins[::20])
        #ax1.set_xlabel('distance [arcsec]')
        ax1.set_xlabel('rho [dim.less]')
        ax1.set_ylabel('N', color='r')
        for tl in ax1.get_yticklabels():
            tl.set_color('r')
        #rects = ax1.bar(ind, x, width, color='r', edgecolor='r')
        rects = ax1.bar(ind, xnorm, width, color='r', edgecolor='r')
        ax1.grid(True)
        
        """
        ax2 = ax1.twinx()
        ax2.set_xticks((ind+width/2.)[::20])
        ax2.set_xticklabels(bins[::20])
        i#ax2.set_yticks([])
        #ax2.set_yticklabels([])
        ax2.set_ylabel('Rayleigh distribution', color='b')
        fit = []
        for i in range(len(bins)):
            fit.append(assoc_r[i] * pylab.exp(-assoc_r[i]*assoc_r[i]/2.))
        ax2.plot(ind, fit, 'b-', linewidth=2)
        """
        
        ax3 = ax1.twinx()
        ax3.set_xticks((ind+width/2.)[::20])
        ax3.set_xticklabels(bins[::20])
        ax3.set_ylabel('distance [arcsec]', color='g', labelpad=10)
        for tl in ax3.get_yticklabels():
            tl.set_color('g')
        ax3.plot(ind, dist, 'g-', linewidth=2)

        pylab.title('Distribution of rho and distances for \n WENSS-NVSS candidate associations (' + str(xsum) + ')')
        #plotfiles.append('wenss-nvss_assocs_dist_dsid' + str(dsid) + '.eps')
        plotfiles.append('wenss-nvss_assocs_rho_dsid' + str(dsid) + '.eps')
        pylab.savefig(plotfiles[p],dpi=600)
        
        p = p + 1
        fig = pylab.figure()
        ax1 = fig.add_subplot(111)
        ax1.set_xticks((ind+width/2.)[::20])
        ax1.set_xticklabels(bins[::20])
        #ax1.set_xlabel('distance [arcsec]')
        ax1.set_xlabel('rho [dim.less]')
        ax1.set_ylabel('N', color='r')
        for tl in ax1.get_yticklabels():
            tl.set_color('r')
        rects = ax1.bar(ind, xks, width, color='r', edgecolor='r')
        ax1.grid(True)
        
        pylab.title('Distribution of rho and distances for \n WENSS-NVSS candidate associations (' + str(xsum) + ')')
        #plotfiles.append('wenss-nvss_assocs_dist_dsid' + str(dsid) + '.eps')
        plotfiles.append('wenss-nvss_assocs_rhoks_dsid' + str(dsid) + '.eps')
        pylab.savefig(plotfiles[p],dpi=600)
        
        return plotfiles
    except db.Error, e:
        logging.warn("Retrieving info for dsid %s failed: " % (str(dsid)))
        logging.warn("Failed on query %s : " % (e))
        logging.debug("Failed plotquery: %s" % (e))

def plotBarSrcBGLR(dsid, dsid_min, dsid_max, catid, conn):
    """
    Background sources associated (by chance) to cat sources
    Wenss sources (in the source fields) asssociated with cat sources.
    """
    try:
        cursor = conn.cursor()
        
        #------------- BG Query ----------------------------------
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
                       "              ,obscatsources oc1 " + \
                       "         WHERE ac1.xtrsrc = x1.id " + \
                       "           AND ac1.assoc_lr >= -100.5 " + \
                       "           AND x1.image = im1.id " + \
                       "           AND im1.dataset BETWEEN %s " + \
                       "                             AND %s " + \
                       "           AND ac1.assoc_catsrc_id = oc1.obscatsrcid " + \
                       "           AND oc1.cat_id = %s " + \
                       "       ) t " + \
                       "GROUP BY bin_nr " + \
                       "ORDER BY bin_nr ", (dsid_min, dsid_max,catid))
        y = cursor.fetchall()
        bins_bg = []
        x_bg = []
        dist_bg = []
        mindist_bg = []
        #maxdist = []
        assoc_r_bg = []
        #minassoc_r = []
        #maxassoc_r = []
        for i in range(len(y)):
            # divide by 2 because we bin every log lr = 0.5
            bins_bg.append(y[i][0]/2.)
            x_bg.append(y[i][1])
            dist_bg.append(y[i][2])
            mindist_bg.append(y[i][3])
            #maxdist.append(y[i][4])
            assoc_r_bg.append(y[i][5])
            #minassoc_r.append(y[i][6])
            #maxassoc_r.append(y[i][7])
        
        #print "bins=", bins
        #print "x_bg=", x_bg
        #print "dist=", dist

        xsum_bg = 0
        for i in range(len(x_bg)):
            xsum_bg = xsum_bg + x_bg[i]
        
        # Here we force the data to be plot in a histogram. The query
        # already selected the bins (width: logLR=0.5) and the corresponding values.
        # bin[i] <-> x_bg[i] = number of assocs with value in this bin
        x_bg_mut = []
        for i in range(len(bins_bg)):
            for j in range(x_bg[i]):
                x_bg_mut.append(bins_bg[i] + 0.25)

        #-------------- Source Query --------------------------------------
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
                       "              ,obscatsources oc1 " + \
                       "         WHERE ac1.xtrsrc = x1.id " + \
                       "           AND ac1.assoc_lr >= -100.5 " + \
                       "           AND x1.image = im1.id " + \
                       "           AND im1.dataset = %s " + \
                       "           AND ac1.assoc_catsrc_id = oc1.obscatsrcid " + \
                       "           AND oc1.cat_id = %s " + \
                       "       ) t " + \
                       "GROUP BY bin_nr " + \
                       "ORDER BY bin_nr ", (dsid,catid))
        y = cursor.fetchall()
        cursor.close()
        bins_src = []
        x_src = []
        dist_src = []
        mindist_src = []
        #maxdist = []
        assoc_r_src = []
        #minassoc_r = []
        #maxassoc_r = []
        for i in range(len(y)):
            # divide by 2 because we bin every log lr = 0.5
            bins_src.append(y[i][0]/2.)
            x_src.append(y[i][1])
            dist_src.append(y[i][2])
            mindist_src.append(y[i][3])
            #maxdist.append(y[i][4])
            assoc_r_src.append(y[i][5])
            #minassoc_r.append(y[i][6])
            #maxassoc_r.append(y[i][7])
        
        #print "bins=", bins
        #print "x=", x
        #print "dist_src =", dist_src

        xsum_src = 0
        for i in range(len(x_src)):
            xsum_src = xsum_src + x_src[i]
        
        if (len(bins_bg) != len(bins_src)):
            raise NotImplementedError

        x_src_mut = []
        for i in range(len(bins_bg)):
            for j in range(x_src[i]):
                x_src_mut.append(bins_bg[i] + 0.25)

        x_div = []
        for i in range(len(x_bg)):
           x_div.append(float(x_bg[i])/float(x_src[i]))
        
        xt = pylab.arange(min(bins_bg), max(bins_bg), 20)
        
        plotfiles=[]
        p=0
        
        fig = pylab.figure()
        ax1 = fig.add_subplot(111)
        #ax1.set_xticks(xt)
        #ax1.set_xticklabels(xt)
        ax1.set_xlabel('log LR')
        ax1.set_ylabel('N (log LR)', color='r')
        #for tl in ax1.get_yticklabels():
        #    tl.set_color('r')
        # move hist() downward
        #ax1.grid(True)
        
        ax1.plot(bins_bg, x_div, 'y-', linewidth=1)
        n, bins, patches = ax1.hist(x_src_mut, bins=bins_bg,histtype='stepfilled',edgecolor='r',color='r',log=True,normed=True)
        n, bins, patches = ax1.hist(x_bg_mut, bins=bins_bg,histtype='step',edgecolor='k',log=True,hatch='/',linewidth=1, normed=True)
        ax1.grid(True)
        
        ax2 = ax1.twinx()
        #ax2.set_xticks((ind+width/2.)[::every])
        #ax2.set_xticklabels(bins[::every])
        ax2.set_ylabel('distance [arcsec]', color='b')
        for tl in ax2.get_yticklabels():
            tl.set_color('b')
        
        ax2.plot(bins_bg, dist_bg, 'b--', linewidth=1)
        #ax2.plot(bins_bg, assoc_r_bg, 'b--', linewidth=1)
        #ax2.plot(bins_bg, mindist_bg, 'y--', linewidth=1)
        #ax2.plot(bins_bg, maxdist, 'g--', linewidth=2)
        
        ax2.plot(bins_bg, dist_src, 'b-', linewidth=2)
        #ax2.plot(bins_bg, assoc_r_src, 'b-', linewidth=2)
        #ax2.plot(bins_bg, mindist_src, 'y-', linewidth=2)
        #ax2.plot(ind, maxdist, 'g-', linewidth=2)
        ax2.set_yticks([0,10,20,30,40,50,60,70,80,90])
        ax2.set_yticklabels((0,10,20,30,40,50,60,70,80,90))
        #pylab.title('Distribution of likelihood ratio and distances for \n ' + str(xsum_bg) + ' background sources and '+ str(xsum_src) + ' on-field sources as \n WENSS-NVSS candidate associations')
        #pylab.title('Distribution of likelihood ratio and distances \n for WENSS-NVSS candidate associations')
        plotfiles.append('wenss-nvss_histo_dsid' + str(dsid) + '.eps')
        pylab.savefig(plotfiles[p],dpi=600)
        
        #------------------------------------------------------------------
        


        return plotfiles
    except db.Error, e:
        logging.warn("Retrieving info for dsid %s failed: " % (str(dsid)))
        logging.warn("Failed on query %s : " % (e))
        logging.debug("Failed plotquery: %s" % (e))

def plotBarBGLR(dsid_min, dsid_max, catid, conn):
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
                       "              ,obscatsources oc1 " + \
                       "         WHERE ac1.xtrsrc = x1.id " + \
                       "           AND ac1.assoc_lr >= -100.5 " + \
                       "           AND x1.image = im1.id " + \
                       "           AND im1.dataset BETWEEN %s " + \
                       "                             AND %s " + \
                       "           AND ac1.assoc_catsrc_id = oc1.obscatsrcid " + \
                       "           AND oc1.cat_id = %s " + \
                       "       ) t " + \
                       "GROUP BY bin_nr " + \
                       "ORDER BY bin_nr ", (dsid_min, dsid_max,catid))
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
        
        #print "bins=", bins

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
        pylab.xticks((ind+width/2.)[::20],bins[::20])
        pylab.xlabel('log LR')
        pylab.ylabel('N (log LR)')
        pylab.title('Distribution of log(LR) for \n WENSS-NVSS candidate associations (' + str(xsum) + ')')
        pylab.grid(True)
        rects = pylab.bar(ind, x, width, color='r')
        plotfiles.append('wenss-nvss_bg_assocs_dsid' + str(dsid_min) + '.eps')
        pylab.savefig(plotfiles[p],dpi=600)
        
        p = p + 1
        every = 20
        fig = pylab.figure()
        ax1 = fig.add_subplot(111)
        ax1.set_xticks((ind+width/2.)[::every])
        ax1.set_xticklabels(bins[::every])
        ax1.set_xlabel('log LR')
        ax1.set_ylabel('log N (log LR)', color='r')
        for tl in ax1.get_yticklabels():
            tl.set_color('r')
        rects = ax1.bar(ind, xlog, width, color='w', linewidth='2', edgecolor='k', alpha=0.5)
        ax1.grid(True)
        
        ax2 = ax1.twinx()
        ax2.set_xticks((ind+width/2.)[::every])
        ax2.set_xticklabels(bins[::every])
        #ax2.set_yticks([0,10,20,30,40,50,60,70,80,90,100])
        #ax2.set_yticklabels((0,10,20,30,40,50,60,70,80,90,100))
        ax2.set_ylabel('distance [arcsec]', color='b')
        for tl in ax2.get_yticklabels():
            tl.set_color('b')
        ax2.plot(ind, dist, 'b--', linewidth=2)
        ax2.plot(ind, mindist, 'y--', linewidth=2)
        ax2.plot(ind, maxdist, 'g--', linewidth=2)

        pylab.title('Distribution of log(LR) and distances for \n background WENSS-NVSS candidate associations (' + str(xsum) + ')')
        plotfiles.append('wenss-nvss_bg_assocs_lrdist_dsid' + str(dsid_min) + '.eps')
        pylab.savefig(plotfiles[p],dpi=600)
        
        p = p + 1
        fig = pylab.figure()
        ax1 = fig.add_subplot(111)
        ax1.set_xticks((ind+width/2.)[::20])
        ax1.set_xticklabels(bins[::20])
        ax1.set_xlabel('log LR')
        ax1.set_ylabel('log N (log LR)', color='r')
        for tl in ax1.get_yticklabels():
            tl.set_color('r')
        rects = ax1.bar(ind, xlog, width, color='r', edgecolor='r')
        ax1.grid(True)
        
        ax2 = ax1.twinx()
        ax2.set_xticks((ind+width/2.)[::20])
        ax2.set_xticklabels(bins[::20])
        ax2.set_ylabel(r'average dimensionless distance $\rho$', color='b')
        for tl in ax2.get_yticklabels():
            tl.set_color('b')
        ax2.plot(ind, assoc_r, 'b-', linewidth=2)
        #ax2.plot(ind, minassoc_r, 'y-', linewidth=2)
        #ax2.plot(ind, maxassoc_r, 'g-', linewidth=2)

        pylab.title('Distribution of log(LR) and dim.less dist for \n WENSS-NVSS candidate associations (' + str(xsum) + ')')
        plotfiles.append('wenss-nvss_bg_assocs_lrassoc_r_dsid' + str(dsid_min) + '.eps')
        pylab.savefig(plotfiles[p],dpi=600)
        

        p = p + 1
        reduc = -80
        xreducsum = 0
        for i in range(len(x[reduc:])):
            xreducsum = xreducsum + x[reduc:][i]

        fig = pylab.figure()
        ax1 = fig.add_subplot(111)
        ax1.set_xticks((ind[reduc:] + width / 2.)[::10])
        ax1.set_xticklabels(bins[reduc:][::10])
        ax1.set_xlabel('log LR')
        ax1.set_ylabel('log N (log LR)', color='r')
        for tl in ax1.get_yticklabels():
            tl.set_color('r')
        rects = ax1.bar(ind[reduc:], xlog[reduc:], width, color='r', edgecolor='r')
        ax1.grid(True)
        
        ax2 = ax1.twinx()
        ax2.set_xticks((ind[reduc:] + width / 2.)[::10])
        ax2.set_xticklabels(bins[reduc:][::10])
        ax2.set_ylabel('distance [arcsec]', color='b')
        for tl in ax2.get_yticklabels():
            tl.set_color('b')
        ax2.plot(ind[reduc:], dist[reduc:], 'b-', linewidth=2)
        ax2.plot(ind[reduc:], mindist[reduc:], 'y-', linewidth=2)
        ax2.plot(ind[reduc:], maxdist[reduc:], 'g-', linewidth=2)
        
        pylab.title('Distribution and distances of log(LR) > -30 for \n WENSS-NVSS candidate assocs (' + str(xreducsum) + ')')
        plotfiles.append('wenss-nvss_bg_assocs_lrdistreduc_dsid' + str(dsid_min) + '.eps')
        pylab.savefig(plotfiles[p],dpi=600)
        
        p = p + 1
        pylab.figure()
        reduc = -36
        pylab.xticks((ind[reduc:] + width/2.)[::4],bins[reduc:][::4])
        pylab.xlabel('log LR')
        pylab.ylabel('N (log LR)')
        pylab.title('Distribution of log(LR) \n for WENSS-NVSS candidate assocs (log LR > -30)')
        pylab.grid(True)
        rects = pylab.bar(ind[reduc:], x[reduc:], width, color='r')
        plotfiles.append('wenss-nvss_bg_assocs_reduc_dsid' + str(dsid_min) + '.eps')
        pylab.savefig(plotfiles[p],dpi=600)
        
        return plotfiles
    except db.Error, e:
        logging.warn("Retrieving info for dsid %s failed: " % (str(dsid)))
        logging.warn("Failed on query %s : " % (e))
        logging.debug("Failed plotquery: %s" % (e))

def plotBarLR(dsid, catid, conn):
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
                       "              ,obscatsources oc1 " + \
                       "         WHERE ac1.xtrsrc = x1.id " + \
                       "           AND ac1.assoc_lr >= -100.5 " + \
                       "           AND x1.image = im1.id " + \
                       "           AND im1.dataset = %s " + \
                       "           AND ac1.assoc_catsrc_id = oc1.obscatsrcid " + \
                       "           AND oc1.cat_id = %s " + \
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
        
        print "bins=", bins
        print "x=", x

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
        pylab.xticks((ind+width/2.)[::20],bins[::20])
        pylab.xlabel('log LR')
        pylab.ylabel('N (log LR)')
        pylab.title('Distribution of log(LR) for \n WENSS-NVSS candidate associations (' + str(xsum) + ')')
        pylab.grid(True)
        rects = pylab.bar(ind, x, width, color='r')
        plotfiles.append('wenss-nvss_assocs_dsid' + str(dsid) + '.eps')
        pylab.savefig(plotfiles[p],dpi=600)
        
        p = p + 1
        every = 20
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
        ax2.plot(ind, dist, 'b-', linewidth=2)
        ax2.plot(ind, mindist, 'y-', linewidth=2)
        ax2.plot(ind, maxdist, 'g-', linewidth=2)

        pylab.title('Distribution of log(LR) and distances for \n WENSS-NVSS candidate associations (' + str(xsum) + ')')
        plotfiles.append('wenss-nvss_assocs_lrdist_dsid' + str(dsid) + '.eps')
        pylab.savefig(plotfiles[p],dpi=600)
        
        p = p + 1
        fig = pylab.figure()
        ax1 = fig.add_subplot(111)
        ax1.set_xticks((ind+width/2.)[::20])
        ax1.set_xticklabels(bins[::20])
        ax1.set_xlabel('log LR')
        ax1.set_ylabel('log N (log LR)', color='r')
        for tl in ax1.get_yticklabels():
            tl.set_color('r')
        rects = ax1.bar(ind, xlog, width, color='r', edgecolor='r')
        ax1.grid(True)
        
        ax2 = ax1.twinx()
        ax2.set_xticks((ind+width/2.)[::20])
        ax2.set_xticklabels(bins[::20])
        ax2.set_ylabel(r'average dimensionless distance $\rho$', color='b')
        for tl in ax2.get_yticklabels():
            tl.set_color('b')
        ax2.plot(ind, assoc_r, 'b-', linewidth=2)
        #ax2.plot(ind, minassoc_r, 'y-', linewidth=2)
        #ax2.plot(ind, maxassoc_r, 'g-', linewidth=2)

        pylab.title('Distribution of log(LR) and dim.less dist for \n WENSS-NVSS candidate associations (' + str(xsum) + ')')
        plotfiles.append('wenss-nvss_assocs_lrassoc_r_dsid' + str(dsid) + '.eps')
        pylab.savefig(plotfiles[p],dpi=600)
        

        p = p + 1
        reduc = -80
        xreducsum = 0
        for i in range(len(x[reduc:])):
            xreducsum = xreducsum + x[reduc:][i]

        fig = pylab.figure()
        ax1 = fig.add_subplot(111)
        ax1.set_xticks((ind[reduc:] + width / 2.)[::10])
        ax1.set_xticklabels(bins[reduc:][::10])
        ax1.set_xlabel('log LR')
        ax1.set_ylabel('log N (log LR)', color='r')
        for tl in ax1.get_yticklabels():
            tl.set_color('r')
        rects = ax1.bar(ind[reduc:], xlog[reduc:], width, color='r', edgecolor='r')
        ax1.grid(True)
        
        ax2 = ax1.twinx()
        ax2.set_xticks((ind[reduc:] + width / 2.)[::10])
        ax2.set_xticklabels(bins[reduc:][::10])
        ax2.set_ylabel('distance [arcsec]', color='b')
        for tl in ax2.get_yticklabels():
            tl.set_color('b')
        ax2.plot(ind[reduc:], dist[reduc:], 'b-', linewidth=2)
        ax2.plot(ind[reduc:], mindist[reduc:], 'y-', linewidth=2)
        ax2.plot(ind[reduc:], maxdist[reduc:], 'g-', linewidth=2)
        
        pylab.title('Distribution and distances of log(LR) > -30 for \n WENSS-NVSS candidate assocs (' + str(xreducsum) + ')')
        plotfiles.append('wenss-nvss_assocs_lrdistreduc_dsid' + str(dsid) + '.eps')
        pylab.savefig(plotfiles[p],dpi=600)
        
        p = p + 1
        pylab.figure()
        reduc = -36
        pylab.xticks((ind[reduc:] + width/2.)[::4],bins[reduc:][::4])
        pylab.xlabel('log LR')
        pylab.ylabel('N (log LR)')
        pylab.title('Distribution of log(LR) \n for WENSS-NVSS candidate assocs (log LR > -30)')
        pylab.grid(True)
        rects = pylab.bar(ind[reduc:], x[reduc:], width, color='r')
        plotfiles.append('wenss-nvss_assocs_reduc_dsid' + str(dsid) + '.eps')
        pylab.savefig(plotfiles[p],dpi=600)
        
        return plotfiles
    except db.Error, e:
        logging.warn("Retrieving info for dsid %s failed: " % (str(dsid)))
        logging.warn("Failed on query %s : " % (e))
        logging.debug("Failed plotquery: %s" % (e))

def plotLightCurveByXSource(xtrsrcid, conn):
    """
    This method plots the lightcurve for the specified extracted source.
    It also adds the averaged position and the associated catalog source.
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT xtrsrc " + \
                       "      ,image_id " + \
                       "      ,CAST(taustart_ts AS DATE) " + \
                       "      ,CAST(\'2003-03-29\' AS DATE) " + \
                       "      ,ra " + \
                       "      ,decl " + \
                       "      ,ra_err " + \
                       "      ,decl_err " + \
                       "      ,i_peak " + \
                       "      ,i_peak_err " + \
                       "      ,i_int " + \
                       "      ,i_int_err  " + \
                       "  FROM assocxtrsource " + \
                       "      ,extractedsource  " + \
                       "      ,images            " + \
                       " WHERE xtrsrcid = xtrsrc " + \
                       "   AND imageid = image_id         " + \
                       "   AND xtrsrc_id = %s ", (xtrsrcid,))
        y = cursor.fetchall()
        days=[]
        fluxpeak=[]
        fluxpeakerr=[]
        fluxint=[]
        fluxinterr=[]
        for i in range(len(y)):
            days.append((y[i][2] - y[i][3]).days)
            fluxpeak.append(y[i][8])
            fluxpeakerr.append(y[i][9])
            fluxint.append(y[i][10])
            fluxinterr.append(y[i][11])
        pylab.figure()
        pylab.errorbar(days, fluxint, yerr=fluxinterr \
                      ,fmt='o',color='red', label="Extr. flux")
        
        cursor.execute("SELECT SUM(x1.i_peak / (x1.i_peak_err * x1.i_peak_err)) " + \
                       "       / SUM(1 / (x1.i_peak_err * x1.i_peak_err)) " + \
                       "      ,SUM(x1.i_int / (x1.i_int_err * x1.i_int_err)) " + \
                       "       / SUM(1 / (x1.i_int_err * x1.i_int_err)) " + \
                       "      ,SQRT(1 / SUM(1 / (x1.i_peak_err * x1.i_peak_err))) " + \
                       "      ,SQRT(1 / SUM(1 / (x1.i_int_err * x1.i_int_err))) " + \
                       "  FROM assocxtrsource " + \
                       "      ,extractedsource x1 " + \
                       "      ,images            " + \
                       " WHERE xtrsrcid = xtrsrc " + \
                       "   AND imageid = image_id         " + \
                       "   AND xtrsrc_id = %s ", (xtrsrcid,))
        avg_y = cursor.fetchall()
        avg_fluxpeak=[]
        avg_fluxpeakerr=[]
        avg_fluxint=[]
        avg_fluxinterr=[]
        dayserr=[]
        for i in range(len(avg_y)):
            avg_fluxpeak.append(avg_y[i][0])
            avg_fluxpeakerr.append(avg_y[i][2])
            avg_fluxint.append(avg_y[i][1])
            avg_fluxinterr.append(avg_y[i][3])
            dayserr.append((max(days) - min(days))/2) 
        pylab.errorbar((max(days) + min(days))/2, avg_fluxint, yerr=avg_fluxinterr,xerr=dayserr \
                      ,fmt='s',color='blue', label="Weight. avg. flux")
        
        cursor.execute("SELECT AVG(x1.i_peak) " + \
                       #"      ,STD(x1.i_peak) " + \
                       "      ,SQRT(AVG(x1.i_peak * x1.i_peak) - AVG(x1.i_peak) * AVG(x1.i_peak)) " + \
                       "      ,AVG(x1.i_int) " + \
                       #"      ,STD(x1.i_int) " + \
                       "      ,SQRT(AVG(x1.i_int * x1.i_int) - AVG(x1.i_int) * AVG(x1.i_int)) " + \
                       "  FROM assocxtrsource " + \
                       "      ,extractedsource x1 " + \
                       "      ,images            " + \
                       " WHERE xtrsrcid = xtrsrc " + \
                       "   AND imageid = image_id         " + \
                       "   AND xtrsrc_id = %s ", (xtrsrcid,))
        avg2_y = cursor.fetchall()
        avg2_fluxpeak=[]
        avg2_fluxpeakerr=[]
        avg2_fluxint=[]
        avg2_fluxinterr=[]
        dayserr=[]
        for i in range(len(avg2_y)):
            avg2_fluxpeak.append(avg2_y[i][0])
            avg2_fluxpeakerr.append(avg2_y[i][1])
            avg2_fluxint.append(avg2_y[i][2])
            avg2_fluxinterr.append(avg2_y[i][3])
            dayserr.append((max(days) - min(days))/2) 
        pylab.errorbar((max(days) + min(days))/2, avg2_fluxint, yerr=avg2_fluxinterr,xerr=dayserr \
                      ,fmt='*',color='m', label="Arithm. mean flux")
        
        cursor.execute("SELECT catname " + \
                       "      ,i_int_avg " + \
                       "      ,i_int_avg_err  " + \
                       "  FROM catalogedsources " + \
                       "      ,catalogs  " + \
                       " WHERE catid = cat_id  " + \
                       "   AND catname = 'NVSS' " + \
                       "   AND catsrcid IN (SELECT ac.assoc_catsrc_id  " + \
                       "                      FROM assoccatsources ac " + \
                       "                          ,assocxtrsource ax  " + \
                       "                     WHERE ax.xtrsrc = ac.xtrsrc  " + \
                       "                       AND ac.assoc_lr > -10 " + \
                       "                       AND ax.xtrsrc = %s " + \
                       "                    GROUP BY ac.assoc_catsrc_id " + \
                       "                   ) ", (xtrsrcid,))
        cat_y = cursor.fetchall()
        cursor.close()
        cat_name=[]
        cat_fluxint=[]
        cat_fluxinterr=[]
        dayserr=[]
        for i in range(len(cat_y)):
            #days.append((y[i][2] - y[i][3]).days)
            cat_name.append(cat_y[i][0])
            cat_fluxint.append(cat_y[i][1])
            cat_fluxinterr.append(cat_y[i][2])
            dayserr.append((min(days) - max(days))/2)
        
        if (len(cat_fluxint) > 0):
            pylab.errorbar((max(days)+min(days))/2, cat_fluxint, yerr=cat_fluxinterr,xerr=dayserr \
                          ,fmt='D',color='black', label="Assoc. cat. flux")

        pylab.grid(True)
        pylab.title('LightCurve xtrsrcid = ' + str(xtrsrcid))
        pylab.xlabel('Time since burst [days]')
        pylab.ylabel('Integrated Flux [Jy]')
        pylab.legend(numpoints=1,loc='best')
        logtime = datetime.today().isoformat('-')
        logtime = tm.strftime("%Y%m%d-%H%M")
        plotfile = 'lightcurve_' + str(xtrsrcid) + '_' + logtime + '.eps'
        pylab.savefig(plotfile,dpi=600)
        return plotfile
    except db.Error, e:
        logging.warn("Retrieving info for xtrsrcid %s failed: " % (str(xtrsrcid)))
        logging.warn("Failed on query %s : " % (e))
        logging.debug("Failed plotquery: %s" % (e))

def plotAssocCloudByXSource(xtrsrcid, conn, outputdir):
    """
    This method plots the positions of the sources that were associated
    with each other.
    Together plotted is the associated catalog source and the average of
    the associated sources.
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT ax1.xtrsrc " + \
                       "      ,ax1.xtrsrc " + \
                       "      ,x1.ra " + \
                       "      ,x1.decl " + \
                       "      ,x1.ra_err / 3600  " + \
                       "      ,x1.decl_err / 3600  " + \
                       "  FROM (SELECT xtrsrc_id " + \
                       "          FROM assocxtrsource " + \
                       "         WHERE xtrsrc = %s " + \
                       "       ) t " + \
                       "      ,assocxtrsource ax1 " + \
                       "      ,extractedsource x1 " + \
                       "      ,images im1 " + \
                       " WHERE ax1.xtrsrc = t.xtrsrc " + \
                       "   AND ax1.xtrsrc = x1.id " + \
                       "   AND x1.image = im1.id ", (xtrsrcid,))
        y = cursor.fetchall()
        ra = []
        decl = []
        ra_err = []
        decl_err = []
        for i in range(len(y)):
            ra.append(y[i][2])
            decl.append(y[i][3])
            ra_err.append(y[i][4])
            decl_err.append(y[i][5])
        pylab.figure()
        pylab.errorbar(ra, decl, yerr=decl_err, xerr=ra_err \
                      ,fmt='o', color='red', label="Extr. Pos.")
        
        cursor.execute("SELECT SUM(x1.ra / (x1.ra_err * x1.ra_err)) " + \
                       "       / SUM(1 / (x1.ra_err * x1.ra_err)) " + \
                       "      ,SUM(x1.decl / (x1.decl_err * x1.decl_err)) " + \
                       "       / SUM(1 / (x1.decl_err * x1.decl_err)) " + \
                       "      ,SQRT(1 / SUM(1 / (x1.ra_err * x1.ra_err))) / 3600 " + \
                       "      ,SQRT(1 / SUM(1 / (x1.decl_err * x1.decl_err))) / 3600  " + \
                       "  FROM (SELECT xtrsrc_id " + \
                       "          FROM assocxtrsource " + \
                       "         WHERE xtrsrc = %s " + \
                       "       ) t " + \
                       "      ,assocxtrsource ax1 " + \
                       "      ,extractedsource x1 " + \
                       "      ,images im1 " + \
                       " WHERE ax1.xtrsrc = t.xtrsrc " + \
                       "   AND ax1.xtrsrc = x1.id " + \
                       "   AND x1.image = im1.id ", (xtrsrcid,))
        avg_y = cursor.fetchall()
        avg_ra = []
        avg_decl = []
        avg_ra_err = []
        avg_decl_err = []
        for i in range(len(avg_y)):
            avg_ra.append(avg_y[i][0])
            avg_decl.append(avg_y[i][1])
            avg_ra_err.append(avg_y[i][2])
            avg_decl_err.append(avg_y[i][3])
        #pylab.errorbar(avg_ra,avg_decl,yerr=avg_decl_err, xerr=avg_ra_err \
        #              ,fmt='s',color='blue',label="weight. avg. pos.")
        
        cursor.execute("SELECT AVG(x1.ra) " + \
                       "      ,AVG(x1.decl) " + \
                       "      ,SQRT(AVG(x1.ra * x1.ra) - AVG(x1.ra) * AVG(x1.ra)) " + \
                       "      ,SQRT(AVG(x1.decl * x1.decl) - AVG(x1.decl) * AVG(x1.decl)) " + \
                       "  FROM (SELECT xtrsrc_id " + \
                       "          FROM assocxtrsource " + \
                       "         WHERE xtrsrc = %s " + \
                       "       ) t " + \
                       "      ,assocxtrsource ax1 " + \
                       "      ,extractedsource x1 " + \
                       "      ,images im1 " + \
                       " WHERE ax1.xtrsrc = t.xtrsrc " + \
                       "   AND ax1.xtrsrc = x1.id " + \
                       "   AND x1.image = im1.id ", (xtrsrcid,))
        avg2_y = cursor.fetchall()
        avg2_ra = []
        avg2_decl = []
        avg2_ra_err = []
        avg2_decl_err = []
        for i in range(len(avg_y)):
            avg2_ra.append(avg_y[i][0])
            avg2_decl.append(avg_y[i][1])
            avg2_ra_err.append(avg_y[i][2])
            avg2_decl_err.append(avg_y[i][3])
        pylab.errorbar(avg2_ra,avg2_decl,yerr=avg2_decl_err,xerr=avg2_ra_err \
                      , fmt='*',color='m',label="Arith. mean pos.")
        
        cursor.execute("SELECT catname " + \
                       "      ,ra " + \
                       "      ,decl " + \
                       "      ,ra_err/3600 " + \
                       "      ,decl_err/3600  " + \
                       "  FROM catalogedsources " + \
                       "      ,catalogs " + \
                       " WHERE catid = cat_id " + \
                       "   AND catsrcid IN (SELECT ac.assoc_catsrc_id " + \
                       "                      FROM assoccatsources ac " + \
                       "                          ,assocxtrsource ax  " + \
                       "                     WHERE ax.xtrsrc = ac.xtrsrc " + \
                       "                       AND ac.assoc_lr > -10 " + \
                       "                       AND ax.xtrsrc = %s " + \
                       "                    GROUP BY ac.assoc_catsrc_id " + \
                       "                   ) ", (xtrsrcid,))
        cat_y = cursor.fetchall()
        cursor.close()
        cat_ra = []
        cat_decl = []
        cat_ra_err = []
        cat_decl_err = []
        for i in range(len(cat_y)):
            cat_ra.append(cat_y[i][1])
            cat_decl.append(cat_y[i][2])
            cat_ra_err.append(cat_y[i][3])
            cat_decl_err.append(cat_y[i][4])
        if (len(cat_y) > 0):
            pylab.errorbar(cat_ra,cat_decl,yerr=cat_decl_err, xerr=cat_ra_err, fmt='D',color='black',label="Cat. pos.")
        
        pylab.grid(True)
        pylab.title('Association Cloud for xtrsrcid = ' + str(xtrsrcid))
        pylab.xlabel('Right Ascension [degrees]')
        pylab.ylabel('Declination [degrees]')
        pylab.legend(numpoints=1,loc='best')
        logtime = tm.strftime("%Y%m%d-%H%M")
        plotfile = 'ac' + str(xtrsrcid) + '.eps'
        pylab.savefig(os.path.join(outputdir, plotfile),dpi=600)
        return plotfile
    except db.Error, e:
        logging.warn("Retrieving info for xtrsrcid %s failed: " % (str(xtrsrcid)))
        logging.warn("Failed on query %s : " % (e))
        logging.debug("Failed plotquery: %s" % (e))

def plotHistSpIndices(conn):
    try:
        cursor = conn.cursor()

        query="select t.cat_id,t.sp_indx from (select xtrsrc_id,assoc_catsrc_id,cat_id,log10(i_int_avg/i_int)/log10(351100000/freq_eff) as sp_indx from assoccatsources,catalogedsources,extractedsource where xtrsrc_id = xtrsrcid and assoc_catsrc_id = catsrcid and assoc_lr > -10) t order by t.cat_id,t.sp_indx "

        cursor.execute(query)
        y = cursor.fetchall()
        cursor.close()
        
        nvss=[]
        vlss=[]
        #print y
        for i in range(len(y)):
            if y[i][0] == 3:
                nvss.append(y[i][1])
                #print nvss
            else:
                vlss.append(y[i][1])
                #print vlss

        plotfiles=[]
        p = 0
        fig = pylab.figure()
        ax1 = fig.add_subplot(111)
        width = 60
        rects1 = ax1.hist(nvss, width, color='r',normed=True,edgecolor='r')
        rects2 = ax1.hist(vlss, width, color='b',normed=True,edgecolor='b')
        #rects2 = ax1.hist(vlss, width,histtype='step',edgecolor='k',log=True,hatch='/',linewidth=1, normed=True)
        #ax1.set_xticks((ind + width / 2.)[::5])
        #ax1.set_xticklabels(bins[::5])
        ax1.set_xlabel('Spectral Index')
        ax1.set_ylabel('N', color='r')
        for tl in ax1.get_yticklabels():
            tl.set_color('r')
        ax1.grid(True)
        
        pylab.title('Distribution of spectral indices')
        plotfiles.append('sp_indx_test.eps')
        pylab.savefig(plotfiles[p],dpi=600)
        
        return plotfiles
    except db.Error, e:
        logging.warn("Retrieving info for sp. idx failed: %s" % (e))
        logging.warn("Failed on query %s : " % (e))
        logging.debug("Failed plotquery: %s" % (e))

def plotLightCurveSecByXSource(xtrsrcid, conn):
    """
    This method plots the lightcurve for the specified extracted source.
    It also adds the averaged position and the associated catalog source.
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT ax1.xtrsrc " + \
                       "      ,x1.image " + \
                       "      ,CAST(im1.taustart_ts AS TIMESTAMP) " + \
                       "      ,CAST(\'2002-09-30\' AS TIMESTAMP) " + \
                       "      ,x1.ra " + \
                       "      ,x1.decl " + \
                       "      ,x1.ra_err " + \
                       "      ,x1.decl_err " + \
                       "      ,x1.i_peak " + \
                       "      ,x1.i_peak_err " + \
                       "      ,x1.i_int " + \
                       "      ,x1.i_int_err  " + \
                       "  FROM (SELECT xtrsrc_id " + \
                       "          FROM assocxtrsource " + \
                       "         WHERE xtrsrc = %s " + \
                       "       ) t " + \
                       "      ,assocxtrsource ax1 " + \
                       "      ,extractedsource x1 " + \
                       "      ,images im1 " + \
                       " WHERE ax1.xtrsrc = t.xtrsrc " + \
                       "   AND ax1.xtrsrc = x1.id " + \
                       "   AND x1.image = im1.id ", (xtrsrcid,))
        y = cursor.fetchall()
        days=[]
        fluxpeak=[]
        fluxpeakerr=[]
        fluxint=[]
        fluxinterr=[]
        for i in range(len(y)):
            #print i,'ts 1:',y[i][2],'ts 2:',y[i][3]
            #print i,'ts 1 - ts2:',(y[i][2] - y[i][3]).days + (y[i][2] - y[i][3]).seconds/86400.,'days'
            days.append((y[i][2] - y[i][3]).days + (y[i][2] - y[i][3]).seconds/86400.)
            fluxpeak.append(y[i][8])
            fluxpeakerr.append(y[i][9])
            fluxint.append(y[i][10])
            fluxinterr.append(y[i][11])
        
        #print 'days:',days

        pylab.figure()
        pylab.errorbar(days, fluxint, yerr=fluxinterr \
                      ,fmt='o',color='red', label="Extr. flux")
        
        cursor.execute("SELECT SUM(x1.i_peak / (x1.i_peak_err * x1.i_peak_err)) " + \
                       "       / SUM(1 / (x1.i_peak_err * x1.i_peak_err)) " + \
                       "      ,SUM(x1.i_int / (x1.i_int_err * x1.i_int_err)) " + \
                       "       / SUM(1 / (x1.i_int_err * x1.i_int_err)) " + \
                       "      ,SQRT(1 / SUM(1 / (x1.i_peak_err * x1.i_peak_err))) " + \
                       "      ,SQRT(1 / SUM(1 / (x1.i_int_err * x1.i_int_err))) " + \
                       "  FROM (SELECT xtrsrc_id " + \
                       "          FROM assocxtrsource " + \
                       "         WHERE xtrsrc = %s " + \
                       "       ) t " + \
                       "      ,assocxtrsource ax1 " + \
                       "      ,extractedsource x1 " + \
                       "      ,images im1 " + \
                       " WHERE ax1.xtrsrc = t.xtrsrc " + \
                       "   AND ax1.xtrsrc = x1.id " + \
                       "   AND x1.image = im1.id ", (xtrsrcid,))
        avg_y = cursor.fetchall()
        avg_fluxpeak=[]
        avg_fluxpeakerr=[]
        avg_fluxint=[]
        avg_fluxinterr=[]
        dayserr=[]
        for i in range(len(avg_y)):
            avg_fluxpeak.append(avg_y[i][0])
            avg_fluxpeakerr.append(avg_y[i][2])
            avg_fluxint.append(avg_y[i][1])
            avg_fluxinterr.append(avg_y[i][3])
            dayserr.append((max(days) - min(days))/2) 
        pylab.errorbar((max(days) + min(days))/2, avg_fluxint, yerr=avg_fluxinterr,xerr=dayserr,fmt='s',color='blue', label="Weight. avg. flux")
        
        cursor.execute("SELECT AVG(x1.i_peak) " + \
                       #"      ,STD(x1.i_peak) " + \
                       "      ,SQRT(AVG(x1.i_peak * x1.i_peak) - AVG(x1.i_peak) * AVG(x1.i_peak)) " + \
                       "      ,AVG(x1.i_int) " + \
                       #"      ,STD(x1.i_int) " + \
                       "      ,SQRT(AVG(x1.i_int * x1.i_int) - AVG(x1.i_int) * AVG(x1.i_int)) " + \
                       "  FROM (SELECT xtrsrc_id " + \
                       "          FROM assocxtrsource " + \
                       "         WHERE xtrsrc = %s " + \
                       "       ) t " + \
                       "      ,assocxtrsource ax1 " + \
                       "      ,extractedsource x1 " + \
                       "      ,images im1 " + \
                       " WHERE ax1.xtrsrc = t.xtrsrc " + \
                       "   AND ax1.xtrsrc = x1.id " + \
                       "   AND x1.image = im1.id ", (xtrsrcid,))
        avg2_y = cursor.fetchall()
        avg2_fluxpeak=[]
        avg2_fluxpeakerr=[]
        avg2_fluxint=[]
        avg2_fluxinterr=[]
        dayserr=[]
        for i in range(len(avg2_y)):
            avg2_fluxpeak.append(avg2_y[i][0])
            avg2_fluxpeakerr.append(avg2_y[i][1])
            avg2_fluxint.append(avg2_y[i][2])
            avg2_fluxinterr.append(avg2_y[i][3])
            dayserr.append((max(days) - min(days))/2) 
        pylab.errorbar((max(days) + min(days))/2, avg2_fluxint, yerr=avg2_fluxinterr,xerr=dayserr,fmt='*',color='m', label="Arithm. mean flux")
        
        cursor.execute("SELECT catname " + \
                       "      ,i_int_avg " + \
                       "      ,i_int_avg_err  " + \
                       "  FROM catalogedsources " + \
                       "      ,catalogs  " + \
                       " WHERE catid = cat_id  " + \
                       "   AND catname = 'NVSS' " + \
                       "   AND catsrcid IN (SELECT ac.assoc_catsrc_id  " + \
                       "                      FROM assoccatsources ac " + \
                       "                          ,assocxtrsource ax  " + \
                       "                     WHERE ax.xtrsrc = ac.xtrsrc  " + \
                       "                       AND ac.assoc_lr > -10 " + \
                       "                       AND ax.xtrsrc = %s " + \
                       "                    GROUP BY ac.assoc_catsrc_id " + \
                       "                   ) ", (xtrsrcid,))
        cat_y = cursor.fetchall()
        cursor.close()
        cat_name=[]
        cat_fluxint=[]
        cat_fluxinterr=[]
        dayserr=[]
        for i in range(len(cat_y)):
            #days.append((y[i][2] - y[i][3]).days)
            cat_name.append(cat_y[i][0])
            cat_fluxint.append(cat_y[i][1])
            cat_fluxinterr.append(cat_y[i][2])
            dayserr.append((min(days) - max(days))/2)
        
        if (len(cat_fluxint) > 0):
            pylab.errorbar((max(days)+min(days))/2, cat_fluxint, yerr=cat_fluxinterr,xerr=dayserr,fmt='D',color='black', label="Assoc. cat. flux")

        pylab.grid(True)
        pylab.title('LightCurve xtrsrcid = ' + str(xtrsrcid))
        #pylab.xlabel('Time since t0 [days]')
        pylab.xlabel('Time elapsed since 2002-09-30 [days]')
        pylab.ylabel('Integrated Flux [Jy]')
        #pylab.xlim(0,45)
        #pylab.ylim(0,1)
        pylab.legend(numpoints=1,loc='best')
        logtime = datetime.today().isoformat('-')
        logtime = tm.strftime("%Y%m%d-%H%M")
        plotfile = 'lc' + str(xtrsrcid) + '.eps'
        pylab.savefig(plotfile,dpi=600)
        return plotfile
    except db.Error, e:
        logging.warn("Retrieving info for xtrsrcid %s failed: " % (str(xtrsrcid)))
        logging.warn("Failed on query %s : " % (e))
        logging.debug("Failed plotquery: %s" % (e))

def plotGRB030329LightCurveSecByXSource(xtrsrcid, dsid, conn,title=None):
    """
    This method plots the multifrequency lightcurves for the specified extracted source.
    Only sources within 0.05 degrees from GRB030329 are selected, to avoid beam attenuation 
    related flux deviations.
    Its distance to GRB030329 is calculated.
    It also adds the averaged position and the associated catalog source.
    """
    try:
        cursor = conn.cursor()
        cursor.execute("select ax1.xtrsrc " + \
                       "      ,ax1.xtrsrc " + \
                       "      ,im2.band " + \
                       "      ,CAST(im2.taustart_ts AS TIMESTAMP) " + \
                       "      ,CAST(\'2003-03-29\' AS TIMESTAMP) " + \
                       #"      ,assoc_distance_arcsec " + \
                       #"      ,assoc_r " + \
                       #"      ,assoc_lr " + \
                       "      ,3600 * DEGREES(2 * ASIN(SQRT((c1.x - x2.x) * (c1.x - x2.x) " + \
                       "                                   + (c1.y - x2.y) * (c1.y - x2.y) " + \
                       "                                   + (c1.z - x2.z) * (c1.z - x2.z) " + \
                       "                                   ) / 2) ) AS grb_distance_arcsec " + \
                       "      ,1000 * x2.i_peak " + \
                       "      ,1000 * x2.i_peak_err " + \
                       "      ,1000 * x2.i_int " + \
                       "      ,1000 * x2.i_int_err " + \
                       "  from assocxtrsource ax1 " + \
                       "      ,extractedsource x1 " + \
                       "      ,extractedsource x2 " + \
                       "      ,images im1 " + \
                       "      ,images im2 " + \
                       "      ,catalogedsources c1 " + \
                       " where ax1.xtrsrc = x1.id " + \
                       "   and x1.image = im1.id " + \
                       "   AND ax1.xtrsrc = x2.id " + \
                       "   and x2.image = im2.id " + \
                       "   AND ax1.assoc_lr > -10 " + \
                       "   AND im1.band <> 17 " + \
                       "   AND im2.band <> 17 " + \
                       "   and c1.catsrcid = 2071216 " + \
                       #"   AND c1.x * x1.x + c1.y * x1.y + c1.z * x1.z > COS(RADIANS(0.05)) " + \
                       "   and ax1.xtrsrc = %s " + \
                       "   and im1.dataset = %s " + \
                       "order by ax1.xtrsrc " + \
                       "        ,im2.band " + \
                       "        ,im2.taustart_ts ", (xtrsrcid,dsid))
        y = cursor.fetchall()
        band = []
        days=[]
        grbdist = []
        fluxpeak=[]
        fluxpeakerr=[]
        fluxint=[]
        fluxinterr=[]
        for i in range(len(y)):
            #print i,'ts 1:',y[i][2],'ts 2:',y[i][3]
            #print i,'ts 1 - ts2:',(y[i][2] - y[i][3]).days + (y[i][2] - y[i][3]).seconds/86400.,'days'
            band.append(y[i][2])
            days.append((y[i][3] - y[i][4]).days + (y[i][3] - y[i][4]).seconds/86400.)
            grbdist.append(y[i][5])
            fluxpeak.append(y[i][6])
            fluxpeakerr.append(y[i][7])
            fluxint.append(y[i][8])
            fluxinterr.append(y[i][9])
        
        #print "days",days
        #print "band",band

        m = -1
        fmt = ['s','o','^','d','+','v','>','<','p','h','8','x']

        pylab.figure()
        idx_start = 0
        band0 = band[0]
        for i in range(len(days)):
            if band[i] != band0:
                if m > len(fmt):
                    m = len(fmt) - 1
                else:
                    m = m + 1
                if band[i-1] == 11:
                    leg_band = '330 MHz'
                if band[i-1] == 13:
                    leg_band = '840 MHz'
                if band[i-1] == 14:
                    leg_band = '1.4 GHz'
                if band[i-1] == 15:
                    leg_band = '2.3 GHz'
                if band[i-1] == 16:
                    leg_band = '4.8 GHz'
                pylab.errorbar(days[idx_start:i], fluxint[idx_start:i], yerr=fluxinterr[idx_start:i], \
                               fmt=fmt[m],label=leg_band)
                band0 = band[i]
                idx_start = i
        if m > len(fmt):
            m = len(fmt) - 1
        else:
            m = m + 1
        if band[i-1] == 11:
            leg_band = '330 MHz'
        if band[i-1] == 13:
            leg_band = '840 MHz'
        if band[i-1] == 14:
            leg_band = '1.4 GHz'
        if band[i-1] == 15:
            leg_band = '2.3 GHz'
        if band[i-1] == 16:
            leg_band = '4.8 GHz'
        pylab.errorbar(days[idx_start:], fluxint[idx_start:], yerr=fluxinterr[idx_start:],\
                       fmt=fmt[m],label=leg_band)
        
        """
        cursor.execute("SELECT SUM(x1.i_peak / (x1.i_peak_err * x1.i_peak_err)) " + \
                       "       / SUM(1 / (x1.i_peak_err * x1.i_peak_err)) " + \
                       "      ,SUM(x1.i_int / (x1.i_int_err * x1.i_int_err)) " + \
                       "       / SUM(1 / (x1.i_int_err * x1.i_int_err)) " + \
                       "      ,SQRT(1 / SUM(1 / (x1.i_peak_err * x1.i_peak_err))) " + \
                       "      ,SQRT(1 / SUM(1 / (x1.i_int_err * x1.i_int_err))) " + \
                       "  FROM (SELECT xtrsrc_id " + \
                       "          FROM assocxtrsource " + \
                       "         WHERE xtrsrc = %s " + \
                       "       ) t " + \
                       "      ,assocxtrsource ax1 " + \
                       "      ,extractedsource x1 " + \
                       "      ,images im1 " + \
                       " WHERE ax1.xtrsrc = t.xtrsrc " + \
                       "   AND ax1.xtrsrc = x1.id " + \
                       "   AND im1.band = 14 " + \
                       "   AND x1.image = im1.id ", (xtrsrcid,))
        avg_y = cursor.fetchall()
        avg_fluxpeak=[]
        avg_fluxpeakerr=[]
        avg_fluxint=[]
        avg_fluxinterr=[]
        dayserr=[]
        for i in range(len(avg_y)):
            avg_fluxpeak.append(avg_y[i][0])
            avg_fluxpeakerr.append(avg_y[i][2])
            avg_fluxint.append(avg_y[i][1])
            avg_fluxinterr.append(avg_y[i][3])
            dayserr.append((max(days) - min(days))/2) 
        pylab.errorbar((max(days) + min(days))/2, avg_fluxint, yerr=avg_fluxinterr,xerr=dayserr,fmt='s',color='blue', label="Weight. avg. flux")
        
        cursor.execute("SELECT AVG(x1.i_peak) " + \
                       #"      ,STD(x1.i_peak) " + \
                       "      ,SQRT(AVG(x1.i_peak * x1.i_peak) - AVG(x1.i_peak) * AVG(x1.i_peak)) " + \
                       "      ,AVG(x1.i_int) " + \
                       #"      ,STD(x1.i_int) " + \
                       "      ,SQRT(AVG(x1.i_int * x1.i_int) - AVG(x1.i_int) * AVG(x1.i_int)) " + \
                       "  FROM (SELECT xtrsrc_id " + \
                       "          FROM assocxtrsource " + \
                       "         WHERE xtrsrc = %s " + \
                       "       ) t " + \
                       "      ,assocxtrsource ax1 " + \
                       "      ,extractedsource x1 " + \
                       "      ,images im1 " + \
                       " WHERE ax1.xtrsrc = t.xtrsrc " + \
                       "   AND ax1.xtrsrc = x1.id " + \
                       "   AND im1.band = 14 " + \
                       "   AND x1.image = im1.id ", (xtrsrcid,))
        avg2_y = cursor.fetchall()
        avg2_fluxpeak=[]
        avg2_fluxpeakerr=[]
        avg2_fluxint=[]
        avg2_fluxinterr=[]
        dayserr=[]
        for i in range(len(avg2_y)):
            avg2_fluxpeak.append(avg2_y[i][0])
            avg2_fluxpeakerr.append(avg2_y[i][1])
            avg2_fluxint.append(avg2_y[i][2])
            avg2_fluxinterr.append(avg2_y[i][3])
            dayserr.append((max(days) - min(days))/2) 
        pylab.errorbar((max(days) + min(days))/2, avg2_fluxint, yerr=avg2_fluxinterr,xerr=dayserr,fmt='*',color='m', label="Arithm. mean flux")
        
        cursor.execute("SELECT catname " + \
                       "      ,i_int_avg " + \
                       "      ,i_int_avg_err  " + \
                       "  FROM catalogedsources " + \
                       "      ,catalogs  " + \
                       " WHERE catid = cat_id  " + \
                       "   AND catname = 'NVSS' " + \
                       "   AND catsrcid IN (SELECT ac.assoc_catsrc_id  " + \
                       "                      FROM assoccatsources ac " + \
                       "                          ,assocxtrsource ax  " + \
                       "                     WHERE ax.xtrsrc = ac.xtrsrc  " + \
                       "                       AND ac.assoc_lr > 0 " + \
                       "                       AND ax.xtrsrc = %s " + \
                       "                    GROUP BY ac.assoc_catsrc_id " + \
                       "                   ) ", (xtrsrcid,))
        cat_y = cursor.fetchall()
        cursor.close()
        cat_name=[]
        cat_fluxint=[]
        cat_fluxinterr=[]
        dayserr=[]
        for i in range(len(cat_y)):
            #days.append((y[i][2] - y[i][3]).days)
            cat_name.append(cat_y[i][0])
            cat_fluxint.append(cat_y[i][1])
            cat_fluxinterr.append(cat_y[i][2])
            dayserr.append((min(days) - max(days))/2)
        
        if (len(cat_fluxint) > 0):
            pylab.errorbar((max(days)+min(days))/2, cat_fluxint, yerr=cat_fluxinterr,xerr=dayserr,fmt='D',color='black', label="Assoc. cat. flux")
        """
        pylab.grid(True)
        if title:
            pylab.title('LightCurve xtrsrcid = ' + str(xtrsrcid) + ', ' + str(round(float(sum(grbdist)/len(grbdist)),3)) + '" to GRB030329')
        pylab.xlabel('Time since burst [days]')
        pylab.ylabel('Integrated Flux [mJy]')
        pylab.legend(numpoints=1,loc='best')
        #logtime = datetime.today().isoformat('-')
        #logtime = tm.strftime("%Y%m%d-%H%M")
        plotfile = 'lc' + str(xtrsrcid) + '.eps'
        pylab.savefig(plotfile,dpi=600)
        return plotfile
    except db.Error, e:
        logging.warn("Retrieving info for xtrsrcid %s failed: " % (str(xtrsrcid)))
        logging.warn("Failed on query %s : " % (e))
        logging.debug("Failed plotquery: %s" % (e))
