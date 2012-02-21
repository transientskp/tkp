#!/usr/bin/python

import os, errno, time, sys, pylab
from scipy import *
from scipy import optimize
import numpy as np
import matplotlib.cm as cm
from datetime import datetime
import logging

import monetdb.sql as db
from monetdb.sql import Error as Error

#host = sys.argv[1] # number of sources per image
#ns = int(sys.argv[2]) # number of sources per image
#iter = int(sys.argv[3]) # number of images to process

#db_type = "MonetDB"
#db_host = host
#db_port = 50000
#db_dbase = "simdat"
#db_user = "simdat" 
#db_passwd = "simdat"

path = os.getenv('HOME') + '/plots'

logtime = time.strftime("%Y%m%d-%H%M")
logfile = path + '/log/plot.assoc_r.' + str(logtime) + '.log'
logf = open(logfile, 'w')
row = 'Plot assoc_r \n'
logf.write(row)
row = '+========================================================================================+\n'
logf.write(row)
row = '| iter | imageid | query5_time | query8_time | query9_time | query10_time | query12_time |\n'
logf.write(row)
row = '+========================================================================================+\n'
logf.write(row)

#conn = db.connect(hostname=db_host,database=db_dbase,username=db_user,password=db_passwd)

def plotHist_assoc_r(conn):
    """Initialize the temporary storage table
    
    Initialize the temporary table temprunningcatalog which contains
    the current observed sources.
    """
    
    try:
        cursor = conn.cursor()
        query = """
        select r.xtrsrc_id
              ,x.xtrsrcid
              ,a.assoc_distance_arcsec
              ,3600 * deg(2 * ASIN(SQRT((r.x - x.x) * (r.x - x.x)
                                        + (r.y - x.y) * (r.y - x.y)
                                        + (r.z - x.z) * (r.z - x.z)
                                       ) / 2) 
                         ) AS distance_arcsec
              ,a.assoc_r
              ,3600 * sqrt(
                            ((r.wm_ra * cos(rad(r.wm_decl)) - x.ra * cos(rad(x.decl))) 
                           * (r.wm_ra * cos(rad(r.wm_decl)) - x.ra * cos(rad(x.decl)))) 
                           / (r.wm_ra_err * r.wm_ra_err + x.ra_err * x.ra_err)
                          +
                           ((r.wm_decl - x.decl) * (r.wm_decl - x.decl)) 
                           / (r.wm_decl_err * r.wm_decl_err + x.decl_err * x.decl_err)
                          ) as r
              ,3600*(x.ra - r.wm_ra)/r.wm_ra_err as z_ra
              ,x.decl
              /*,3600*(x.ra*cos(rad(x.decl)) - r.wm_ra *cos(rad(r.wm_decl)))/r.wm_ra_err as z_ra_cos*/
          from assocxtrsources a
              ,runningcatalog r
              ,extractedsources x
         where r.xtrsrc_id = 232683
           and r.xtrsrc_id = a.xtrsrc_id
           and a.assoc_xtrsrc_id = x.xtrsrcid
        order by a.assoc_r
        """
        plotfiles = []
        lar = []
        for j in range(1,2):
            print "j=",j
            #cursor.execute(query,(j,))
            cursor.execute(query)
            results = zip(*cursor.fetchall())
            conn.commit()

            xtrsrc_id = results[0]
            assoc_xtrsrcid = results[1]
            current_assoc_dist = results[2]
            last_assoc_dist = results[3]
            current_assoc_r = results[4]
            last_assoc_r = results[5]
            ra = results[6]
            decl = results[7]
            
            #print "last_assoc_r =", last_assoc_r
            #print "len(last_assoc_r) =", len(last_assoc_r)
            # alpha_s Histogram
            bins = pylab.arange(-0.1, 10.1, 0.1)
            #sigma = 5.1568e-04
            #sigma = 2.
            #z=pylab.arange(-0.05,0.05,0.001)
            #f_ray=pylab.exp(-z**2/2)/pylab.sqrt(2*pylab.pi)
            x=[]
            #Rayleigh=[]
            #z_ra = [] 
            #distr = []
            #z_ra = (ra - 266.799791971)/0.00632258036237
            #print "z_ra=",z_ra
            #distr = pylab.exp(z_ra**2/2) / pylab.sqrt(2*pylab.pi)
            #for i in range(len(ra)):
            #    z_ra.append((ra[i] - 266.799791971)*pylab.cos(pylab.radians(decl[i]))/1.7562723228805555e-06)
            #    distr.append( pylab.exp(-z_ra[i]**2/2) / pylab.sqrt(2*pylab.pi) )
            for i in range(len(bins)-1):
                x.append((bins[i]+bins[i+1])/2.)
            #    Rayleigh.append(5280.53*(x[i]/sigma**2)*pylab.exp(-x[i]**2/(2*sigma**2)))
            #print "z_ra=",z_ra
            #print "Rayleigh=",Rayleigh
            fig = pylab.figure()
            ax = fig.add_subplot(111)
            counts_cur, bins_cur, patches_cur = ax.hist(current_assoc_r, bins, histtype='bar', color='r')
            counts_lst, bins_lst, patches_lst = ax.hist(last_assoc_r, bins, histtype='bar', color='b')
            #counts_ra, bins_ra, patches_ra = ax.hist(ra, 50, normed=1, color='m')
            #counts_zra, bins_zra, patches_zra = ax.hist(z_ra, 50, normed=1,color='m')
            #print "bins_zra=",bins_zra
            #print "counts_zra=",counts_zra
            #for i in range(len(bins_zra)):
            #    #distr.append(pylab.exp(-bins_zra[i]**2/2)/pylab.sqrt(2*pylab.pi))
            #    distr.append(pylab.exp(-bins_zra[i]**2/2)/pylab.sqrt(2*pylab.pi))
            #counts_decl, bins_decl, patches_decl = ax.hist(decl, 50, histtype='bar', color='g')
            fig=pylab.figure()
            ax = fig.add_subplot(111)
            ax.step(x,counts_cur, where='mid', linewidth=2, color='r', label=str(j)+',cur')
            ax.step(x,counts_lst, where='mid', linewidth=2, color='b', label=str(j)+',lst')
            #ax.step(x,counts_ra, where='mid', linewidth=2, color='m', label=str(j)+',ra')
            #ax.step(x,counts_decl, where='mid', linewidth=2, color='g', label=str(j)+',decl')
            #ax.plot(x, Rayleigh, linewidth=2, color='k', label=str(j)+',R')
            #ax.plot(bins_zra, distr, linewidth=2, color='k', label=str(j)+',R')
            #ax.plot(z, f_ray, linewidth=2, color='k', label=str(j)+',R')
            #ax.plot(z_ra, distr, linewidth=2, color='k', label=str(j)+',R')
            #ax.set_xlim(xmin=-100,xmax=150)
            ax.set_ylim(ymin=0)
            for i in range(len(ax.get_xticklabels())):
                ax.get_xticklabels()[i].set_size('x-large')
            for i in range(len(ax.get_yticklabels())):
                ax.get_yticklabels()[i].set_size('x-large')
            ax.set_xlabel(r'Dimensionless distance, $r$', size='x-large')
            ax.set_ylabel(r'Counts', size='x-large')
            pylab.grid(True)
            pylab.legend()
            fname = 'simdat_dimless_r_' + str(j) + '.eps'
            #fname = 'simdat_dimless_r_all.eps'
            plotfiles.append(fname)
            pylab.savefig(plotfiles[-1],dpi=600)
            print plotfiles[-1]
        
        logf.close()
        print "Results stored in log file:\n", logfile
        return plotfiles
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()

def plot_i_assoc_r(conn):
    """Initialize the temporary storage table
    
    Initialize the temporary table temprunningcatalog which contains
    the current observed sources.
    """
    
    try:
        cursor = conn.cursor()
        query = """
        select row_number() over()
              ,r.xtrsrc_id
              ,x.xtrsrcid
              ,a.assoc_distance_arcsec
              ,3600 * deg(2 * ASIN(SQRT((r.x - x.x) * (r.x - x.x)
                                        + (r.y - x.y) * (r.y - x.y)
                                        + (r.z - x.z) * (r.z - x.z)
                                       ) / 2) 
                         ) AS distance_arcsec
              ,a.assoc_r
              ,3600 * sqrt(
                            ((r.wm_ra * cos(rad(r.wm_decl)) - x.ra * cos(rad(x.decl))) 
                           * (r.wm_ra * cos(rad(r.wm_decl)) - x.ra * cos(rad(x.decl)))) 
                           / (r.wm_ra_err * r.wm_ra_err + x.ra_err * x.ra_err)
                          +
                           ((r.wm_decl - x.decl) * (r.wm_decl - x.decl)) 
                           / (r.wm_decl_err * r.wm_decl_err + x.decl_err * x.decl_err)
                          ) as r
          from assocxtrsources a
              ,runningcatalog r
              ,extractedsources x
         where r.xtrsrc_id = %s
           and a.xtrsrc_id = r.xtrsrc_id
           and a.assoc_xtrsrc_id = x.xtrsrcid
        order by a.assoc_xtrsrc_id
        """
        plotfiles = []
        lar = []
        for j in range(1,2):
            print "j=",j
            cursor.execute(query,(j,))
            results = zip(*cursor.fetchall())
            conn.commit()

            row = results[0]
            xtrsrc_id = results[1]
            assoc_xtrsrcid = results[2]
            current_assoc_dist = results[3]
            last_assoc_dist = results[4]
            current_assoc_r = results[5]
            last_assoc_r = results[6]
            
            #print "current_assoc_r =", current_assoc_r
            print "len(current_assoc_r) =", len(current_assoc_r)
            fig=pylab.figure()
            ax = fig.add_subplot(111)
            #ax.plot(row, current_assoc_r, linewidth=2, color='r', label='cur')
            #ax.plot(row, last_assoc_r, linewidth=2, color='b', label='last')
            ax.scatter(row, current_assoc_r, marker='o', color='r', label='cur')
            #ax.scatter(row, last_assoc_r, marker='s', color='b', label='last')
            ax.set_xlim(xmin=0,xmax=1000)
            ax.set_ylim(ymin=0)
            for i in range(len(ax.get_xticklabels())):
                ax.get_xticklabels()[i].set_size('x-large')
            for i in range(len(ax.get_yticklabels())):
                ax.get_yticklabels()[i].set_size('x-large')
            ax.set_xlabel(r'Sequential Source Number', size='x-large')
            ax.set_ylabel(r'Association radius, $r$', size='x-large')
            pylab.grid(True)
            pylab.legend(numpoints=1)
            fname = 'simdat_i_assoc_r_' + str(j) + '.eps'
            plotfiles.append(fname)
            pylab.savefig(plotfiles[-1],dpi=600)
            print plotfiles[-1]
        
        logf.close()
        print "Results stored in log file:\n", logfile
        return plotfiles
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()



