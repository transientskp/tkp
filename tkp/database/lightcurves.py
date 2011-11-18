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
import monetdb.sql as db

def lightcurveByXSource(conn, xtrsrcid, dirname, freqband=None, Stokes=None):
    """
    This method plots the lightcurve at a sspecified frequencyband 
    for the specified extracted source.
    It also adds the averaged position and the associated catalog source.
    """
    
    try:
        cursor = conn.cursor()
        query = """\
        SELECT assoc_xtrsrc_id 
              ,image_id 
              ,taustart_ts 
              ,ra 
              ,decl 
              ,ra_err 
              ,decl_err 
              ,i_peak 
              ,i_peak_err 
              ,i_int 
              ,i_int_err  
              ,cast(now() as timestamp) 
          FROM assocxtrsources 
              ,extractedsources  
              ,images            
         WHERE xtrsrcid = assoc_xtrsrc_id 
           AND imageid = image_id         
           AND xtrsrc_id = %s 
        ORDER BY taustart_ts
        """
        cursor.execute(query, (xtrsrcid,))
        results = zip(*cursor.fetchall())
        cursor.close()
        if len(results) != 0:
            assoc_xtrsrc_id = results[0]
            image_id = results[1]
            taustart_ts = results[2]
            ra = results[3]
            decl = results[4]
            ra_err = results[5]
            decl_err = results[6]
            i_peak = results[7]
            i_peak_err = results[8]
            i_int = results[9]
            i_int_err = results[10]
            now = results[11]
        
        pylab.figure()
        pylab.errorbar(taustart_ts, i_peak, yerr=i_peak_err \
                      ,fmt='o',color='red', label="Extr. flux")
        
        """
        cursor.execute("SELECT SUM(x1.i_peak / (x1.i_peak_err * x1.i_peak_err)) " + \
                       "       / SUM(1 / (x1.i_peak_err * x1.i_peak_err)) " + \
                       "      ,SUM(x1.i_int / (x1.i_int_err * x1.i_int_err)) " + \
                       "       / SUM(1 / (x1.i_int_err * x1.i_int_err)) " + \
                       "      ,SQRT(1 / SUM(1 / (x1.i_peak_err * x1.i_peak_err))) " + \
                       "      ,SQRT(1 / SUM(1 / (x1.i_int_err * x1.i_int_err))) " + \
                       "  FROM assocxtrsources " + \
                       "      ,extractedsources x1 " + \
                       "      ,images            " + \
                       " WHERE xtrsrcid = assoc_xtrsrc_id " + \
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
                       "  FROM assocxtrsources " + \
                       "      ,extractedsources x1 " + \
                       "      ,images            " + \
                       " WHERE xtrsrcid = assoc_xtrsrc_id " + \
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
                       "                          ,assocxtrsources ax  " + \
                       "                     WHERE ax.assoc_xtrsrc_id = ac.xtrsrc_id  " + \
                       "                       AND ac.assoc_lr > -10 " + \
                       "                       AND ax.xtrsrc_id = %s " + \
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
        """
        pylab.grid(True)
        pylab.title('LightCurve xtrsrcid = ' + str(xtrsrcid))
        pylab.xlabel('Date [timestamp]')
        pylab.ylabel('Peak Flux [Jy]')
        pylab.legend(numpoints=1,loc='best')
        plotfile = dirname + '/lightcurve_' + str(xtrsrcid) + '.eps'
        pylab.savefig(plotfile,dpi=600)
        return plotfile
    except db.Error, e:
        logging.warn("Retrieving info for xtrsrcid %s failed: " % (str(xtrsrcid)))
        logging.warn("Failed on query %s : " % (query))
        raise

def plotAssocCloudByXSource(xtrsrcid, conn, outputdir):
    """
    This method plots the positions of the sources that were associated
    with each other.
    Together plotted is the associated catalog source and the average of
    the associated sources.
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT ax1.xtrsrc_id " + \
                       "      ,ax1.assoc_xtrsrc_id " + \
                       "      ,x1.ra " + \
                       "      ,x1.decl " + \
                       "      ,x1.ra_err / 3600  " + \
                       "      ,x1.decl_err / 3600  " + \
                       "  FROM (SELECT xtrsrc_id " + \
                       "          FROM assocxtrsources " + \
                       "         WHERE assoc_xtrsrc_id = %s " + \
                       "       ) t " + \
                       "      ,assocxtrsources ax1 " + \
                       "      ,extractedsources x1 " + \
                       "      ,images im1 " + \
                       " WHERE ax1.xtrsrc_id = t.xtrsrc_id " + \
                       "   AND ax1.assoc_xtrsrc_id = x1.xtrsrcid " + \
                       "   AND x1.image_id = im1.imageid ", (xtrsrcid,))
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
                       "          FROM assocxtrsources " + \
                       "         WHERE assoc_xtrsrc_id = %s " + \
                       "       ) t " + \
                       "      ,assocxtrsources ax1 " + \
                       "      ,extractedsources x1 " + \
                       "      ,images im1 " + \
                       " WHERE ax1.xtrsrc_id = t.xtrsrc_id " + \
                       "   AND ax1.assoc_xtrsrc_id = x1.xtrsrcid " + \
                       "   AND x1.image_id = im1.imageid ", (xtrsrcid,))
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
                       "          FROM assocxtrsources " + \
                       "         WHERE assoc_xtrsrc_id = %s " + \
                       "       ) t " + \
                       "      ,assocxtrsources ax1 " + \
                       "      ,extractedsources x1 " + \
                       "      ,images im1 " + \
                       " WHERE ax1.xtrsrc_id = t.xtrsrc_id " + \
                       "   AND ax1.assoc_xtrsrc_id = x1.xtrsrcid " + \
                       "   AND x1.image_id = im1.imageid ", (xtrsrcid,))
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
                       "                          ,assocxtrsources ax  " + \
                       "                     WHERE ax.assoc_xtrsrc_id = ac.xtrsrc_id " + \
                       "                       AND ac.assoc_lr > -10 " + \
                       "                       AND ax.xtrsrc_id = %s " + \
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

        query="select t.cat_id,t.sp_indx from (select xtrsrc_id,assoc_catsrc_id,cat_id,log10(i_int_avg/i_int)/log10(351100000/freq_eff) as sp_indx from assoccatsources,catalogedsources,extractedsources where xtrsrc_id = xtrsrcid and assoc_catsrc_id = catsrcid and assoc_lr > -10) t order by t.cat_id,t.sp_indx "

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
        cursor.execute("SELECT ax1.assoc_xtrsrc_id " + \
                       "      ,x1.image_id " + \
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
                       "          FROM assocxtrsources " + \
                       "         WHERE assoc_xtrsrc_id = %s " + \
                       "       ) t " + \
                       "      ,assocxtrsources ax1 " + \
                       "      ,extractedsources x1 " + \
                       "      ,images im1 " + \
                       " WHERE ax1.xtrsrc_id = t.xtrsrc_id " + \
                       "   AND ax1.assoc_xtrsrc_id = x1.xtrsrcid " + \
                       "   AND x1.image_id = im1.imageid ", (xtrsrcid,))
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
                       "          FROM assocxtrsources " + \
                       "         WHERE assoc_xtrsrc_id = %s " + \
                       "       ) t " + \
                       "      ,assocxtrsources ax1 " + \
                       "      ,extractedsources x1 " + \
                       "      ,images im1 " + \
                       " WHERE ax1.xtrsrc_id = t.xtrsrc_id " + \
                       "   AND ax1.assoc_xtrsrc_id = x1.xtrsrcid " + \
                       "   AND x1.image_id = im1.imageid ", (xtrsrcid,))
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
                       "          FROM assocxtrsources " + \
                       "         WHERE assoc_xtrsrc_id = %s " + \
                       "       ) t " + \
                       "      ,assocxtrsources ax1 " + \
                       "      ,extractedsources x1 " + \
                       "      ,images im1 " + \
                       " WHERE ax1.xtrsrc_id = t.xtrsrc_id " + \
                       "   AND ax1.assoc_xtrsrc_id = x1.xtrsrcid " + \
                       "   AND x1.image_id = im1.imageid ", (xtrsrcid,))
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
                       "                          ,assocxtrsources ax  " + \
                       "                     WHERE ax.assoc_xtrsrc_id = ac.xtrsrc_id  " + \
                       "                       AND ac.assoc_lr > -10 " + \
                       "                       AND ax.xtrsrc_id = %s " + \
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
        cursor.execute("select ax1.xtrsrc_id " + \
                       "      ,ax1.assoc_xtrsrc_id " + \
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
                       "  from assocxtrsources ax1 " + \
                       "      ,extractedsources x1 " + \
                       "      ,extractedsources x2 " + \
                       "      ,images im1 " + \
                       "      ,images im2 " + \
                       "      ,catalogedsources c1 " + \
                       " where ax1.xtrsrc_id = x1.xtrsrcid " + \
                       "   and x1.image_id = im1.imageid " + \
                       "   AND ax1.assoc_xtrsrc_id = x2.xtrsrcid " + \
                       "   and x2.image_id = im2.imageid " + \
                       "   AND ax1.assoc_lr > -10 " + \
                       "   AND im1.band <> 17 " + \
                       "   AND im2.band <> 17 " + \
                       "   and c1.catsrcid = 2071216 " + \
                       #"   AND c1.x * x1.x + c1.y * x1.y + c1.z * x1.z > COS(RADIANS(0.05)) " + \
                       "   and ax1.xtrsrc_id = %s " + \
                       "   and im1.ds_id = %s " + \
                       "order by ax1.xtrsrc_id " + \
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
                       "          FROM assocxtrsources " + \
                       "         WHERE assoc_xtrsrc_id = %s " + \
                       "       ) t " + \
                       "      ,assocxtrsources ax1 " + \
                       "      ,extractedsources x1 " + \
                       "      ,images im1 " + \
                       " WHERE ax1.xtrsrc_id = t.xtrsrc_id " + \
                       "   AND ax1.assoc_xtrsrc_id = x1.xtrsrcid " + \
                       "   AND im1.band = 14 " + \
                       "   AND x1.image_id = im1.imageid ", (xtrsrcid,))
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
                       "          FROM assocxtrsources " + \
                       "         WHERE assoc_xtrsrc_id = %s " + \
                       "       ) t " + \
                       "      ,assocxtrsources ax1 " + \
                       "      ,extractedsources x1 " + \
                       "      ,images im1 " + \
                       " WHERE ax1.xtrsrc_id = t.xtrsrc_id " + \
                       "   AND ax1.assoc_xtrsrc_id = x1.xtrsrcid " + \
                       "   AND im1.band = 14 " + \
                       "   AND x1.image_id = im1.imageid ", (xtrsrcid,))
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
                       "                          ,assocxtrsources ax  " + \
                       "                     WHERE ax.assoc_xtrsrc_id = ac.xtrsrc_id  " + \
                       "                       AND ac.assoc_lr > 0 " + \
                       "                       AND ax.xtrsrc_id = %s " + \
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
