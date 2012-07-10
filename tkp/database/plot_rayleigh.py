#!/usr/bin/python

import os, errno, time, sys, pylab
from scipy import *
from scipy import optimize
from scipy import special
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

def plot_fisher():
    """
    Plot the Fisher distribution
    """
    
    plotfiles = []
    #theta = pylab.arange(0.0, pylab.pi, 0.1)
    #theta_deg = pylab.arange(0.0, 180.0, 0.01) # degrees
    theta_arcsec = pylab.arange(0.0, 90.0, 0.1) # arcsecs
    theta_rad = theta_arcsec * pylab.pi / 648000.
    #theta = pylab.arange(0.0, (0.0 + 1./7200.)*pylab.pi, pylab.pi/(180*3600))
    print "theta_arcsec=",theta_arcsec
    print "theta_rad=",theta_rad
    #kappa = 5.
    kappa = 10000000.
    #kappa = 5.
    #C_F = kappa / (2. * pylab.pi * pylab.exp(kappa))
    #f = C_F * pylab.exp(kappa*cos(theta*pylab.pi/180.)) * cos(theta*pylab.pi/180.)
    #f = kappa * sin(theta*pylab.pi/180.) * pylab.exp(kappa*(cos(theta*pylab.pi/180.)-1.)) 
    #g = kappa * pylab.exp(kappa*(cos(theta*pylab.pi/180.)-1.)) 
    f = kappa * sin(theta_rad) * pylab.exp(kappa*(cos(theta_rad)-1.)) 
    g = kappa * pylab.exp(kappa*(cos(theta_rad)-1.)) 
    print "f=",f
    print "g=",g
    #ln_f = pylab.log(kappa * pylab.cos(theta)) + kappa * (pylab.cos(theta) - 1.)
    #ln_f = pylab.log(kappa * pylab.cos(theta) / (2 * pylab.pi)) + kappa * (pylab.sin(theta) - 1)
    #f_approx = (kappa * (1 - theta**2/2)) * pylab.exp(kappa * theta) / (4. * pylab.pi * pylab.sinh(kappa))
    int_f=0.0
    for i in range(len(theta_arcsec)):
        int_f = int_f + 0.01 * f[i] * pylab.pi/648000.
    print "int_f=",int_f
    fig = pylab.figure(figsize=(8,8))
    ax = fig.add_subplot(111)
    #ax = fig.add_axes([0.1, 0.1, 0.8, 0.8], polar=True)
    for i in range(len(ax.get_xticklabels())):
        ax.get_xticklabels()[i].set_size('x-large')
    for i in range(len(ax.get_yticklabels())):
        ax.get_yticklabels()[i].set_size('x-large')
    #ax.set_xlabel(r'Sequential Source Number', size='x-large')
    #ax.set_ylabel(r'Association radius, $r$', size='x-large')
    pylab.grid(True)
    #pylab.legend(numpoints=1)
    #ax.plot(180*(pylab.pi/2 - theta)/pylab.pi, f, linewidth=2, color='r', linestyle='-')
    #ax.plot(180*(pylab.pi/2 - theta)/pylab.pi, pylab.exp(ln_f), linewidth=2, color='b', linestyle='--')
    #ax.plot(theta, f/(2.*pylab.pi), linewidth=2, color='b', linestyle='--')
    #ax.plot(theta, g/(2.*pylab.pi), linewidth=2, color='r', linestyle='--')
    #ax.plot(theta_arcsec, f, linewidth=2, color='b', linestyle='--')
    ax.plot(theta_arcsec, g, linewidth=2, color='r', linestyle='--')
    #ax.plot(206264.806*(pylab.pi/2 - theta), pylab.exp(ln_f), linewidth=2, color='b', linestyle='--')
    #ax.plot(180*(pylab.pi/2 - theta)/pylab.pi, pylab.log(f), linewidth=2, color='r', linestyle='-')
    #ax.plot(180*(pylab.pi/2 - theta)/pylab.pi, ln_f, linewidth=2, color='b', linestyle='--')
    #ax.semilogy(pylab.pi/2 - theta, f, linewidth=2, color='r', linestyle='-')
    #ax.semilogy(180*(pylab.pi/2 - theta)/pylab.pi, pylab.exp(ln_f), linewidth=2, color='b', linestyle='--')
    #ax.plot(pylab.pi/2 - theta, f_approx, linewidth=2, color='b')
    fname = 'simdat_fisher.eps'
    plotfiles.append(fname)
    pylab.savefig(plotfiles[-1],dpi=600)
    print plotfiles[-1]
    
    logf.close()
    print "Results stored in log file:\n", logfile
    return plotfiles

def polarplot_distr(conn):
    """
    Plot the distribution
    """
    
    #ax = fig.add_axes([0.1, 0.1, 0.8, 0.8], polar=True)
    #for i in range(len(ax.get_xticklabels())):
    #    ax.get_xticklabels()[i].set_size('x-large')
    #for i in range(len(ax.get_yticklabels())):
    #    ax.get_yticklabels()[i].set_size('x-large')
    #ax.set_xlabel(r'Sequential Source Number', size='x-large')
    #ax.set_ylabel(r'Association radius, $r$', size='x-large')
    #pylab.grid(True)
    #pylab.legend(numpoints=1)
    #ax.plot(theta, f, linewidth=2, color='r')

    try:
        cursor = conn.cursor()
        query = """
        select r.xtrsrc
              ,x.id
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
          from assocxtrsource a
              ,runningcatalog r
              ,extractedsource x
         where r.xtrsrc = 1
           and a.xtrsrc = r.xtrsrc
           and a.xtrsrc = x.id
        order by a.xtrsrc
        """
        cursor.execute(query)
        results = zip(*cursor.fetchall())
        conn.commit()

        xtrsrc_id = results[0]
        assoc_xtrsrcid = results[1]
        current_assoc_dist = results[2]
        last_assoc_dist = results[3]
        current_assoc_r = results[4]
        last_assoc_r = results[5]
        
        #print "last_assoc_r =", last_assoc_r
        print "len(last_assoc_r) =", len(last_assoc_r)
        plotfiles = []
        N = 150
        #r = 2 * pylab.rand(N)
        theta = pylab.arange(0,2*pylab.pi,2*pylab.pi/len(current_assoc_r))
        #area = 200 * r**2 * pylab.rand(N)
        #area=1.
        #colors = theta
        fig=pylab.figure(figsize=(8,8))
        ax = fig.add_subplot(111, polar=True)
        c = ax.scatter(theta, current_assoc_dist, c='r', s=20, edgecolor='r')
        #c = ax.scatter(theta, last_assoc_dist, c='b', s=10, edgecolor='b')
        c.set_alpha(0.75)
        
        pylab.grid(True)
        pylab.legend()
        
        fname = 'simdat_polar_distr.eps'
        plotfiles.append(fname)
        pylab.savefig(plotfiles[-1],dpi=600)
        print plotfiles[-1]
        
        print "Results stored in log file:\n", logfile
        return plotfiles
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()
        logf.close()

def colatitude_plot(conn):
    """
    Plot the distribution
    """
    
    try:
        cursor = conn.cursor()
        query = """
        select xtrsrc_id
              ,xtrsrcid
              ,1-z_prime as colat
          from (select r.xtrsrc
                      ,r.wm_ra
                      ,r.wm_decl
                      ,x.id
                      ,cos(rad(wm_decl))*cos(rad(wm_ra))*x.x
                       + cos(rad(wm_decl))*sin(rad(wm_ra))*x.y
                       + sin(rad(wm_decl))*x.z as z_prime
                  from assocxtrsource a
                      ,runningcatalog r
                      ,extractedsource x
                 where r.xtrsrc = a.xtrsrc
                   and a.xtrsrc = x.id
                   and r.xtrsrc = 1
               ) t1
        order by colat
        """
        cursor.execute(query)
        results = zip(*cursor.fetchall())
        conn.commit()

        xtrsrc_id = results[0]
        xtrsrcid = results[1]
        colat = results[2]
        
        print "len(colat) =", len(colat)
        n = len(colat)
        E = []
        for i in range(n):
            E.append(pylab.log(n/(n-(i+1)+0.5))) # here i starts at 0 -> (i+1)
        
        # least squares fitting
        iksij = []
        ikssq = []
        for i in range(n):
            iksij.append(E[i]*colat[i])
            ikssq.append(E[i]*E[i])
        
        m_hat1 = (sum(iksij) - sum(E) * sum(colat)/n)/(sum(ikssq) - sum(E)*sum(E)/n)
        print "m_hat (1) = ", m_hat1
        m_hat2 = sum(iksij) / sum(ikssq)
        print "m_hat (2) = ", m_hat2
        #m_hat = 2e-12/4.

        # robust estimate of kappa (FLE, Eq. 5.28)
        kappa_est = []
        for i in range(n):
            c = 1./n - 2. * (i+1) / (n*n*(n+1))
            kappa_est.append(c*colat[i])
        kappa_robust = sum(kappa_est)
        print "robust estimate of 1/kappa : ", kappa_robust
        
        # Kolmogorov-Smirnov statistics
        D_n_plus = []
        D_n_min = []
        kappa_hat = (n-1)/sum(colat)
        print "kappa_hat = ", kappa_hat
        chisqfit1 = []
        chisqfit2 = []
        chisqfit_robust = []
        chisqfit_hat = []
        for i in range(n):
            D_n_plus.append((i+1)/n - (1.-pylab.exp(-kappa_hat*colat[i])))
            D_n_min.append(1.-pylab.exp(-kappa_hat*colat[i]) - i/n)
            chisqfit1.append(m_hat1*E[i])
            chisqfit2.append(m_hat2*E[i])
            chisqfit_robust.append(kappa_robust*E[i])
            chisqfit_hat.append(E[i]/kappa_hat)

        D_n_plus_max = max(D_n_plus)
        print "D_n_plus_max = ", D_n_plus_max
        D_n_min_max = max(D_n_min)
        print "D_n_min_max = ", D_n_min_max
        D_n = max(D_n_plus_max, D_n_min_max)
        print "D_n = ", D_n
        M_E = (D_n - 0.2/n) * (pylab.sqrt(n) + 0.26 + 0.5/pylab.sqrt(n))
        print "M_E = ", M_E
        
        plotfiles = []
        fig=pylab.figure(figsize=(8,8))
        ax = fig.add_subplot(111)
        ax.scatter(E, colat, c='r', s=20, edgecolor='r', label=r'Colatitude')
        ax.plot(E, chisqfit1, 'b-', linewidth=2,label=r'$\chi^2_1$ fit')
        ax.plot(E, chisqfit2, 'g:', linewidth=2,label=r'$\chi^2_2$ fit')
        ax.plot(E, chisqfit_robust, 'k--', linewidth=2,label=r'$\kappa_r$ fit')
        ax.plot(E, chisqfit_hat, 'm-.', linewidth=2, label=r'$\hat{\kappa}$ fit')
        ax.set_xlabel(r'Exponential Quantile', size='x-large')
        ax.set_ylabel(r'Sample Quantile', size='x-large')
        ax.set_xlim(xmin=0)
        ax.set_ylim(ymin=0)
        
        pylab.legend(numpoints=1, loc='best')
        pylab.grid(True)
        
        fname = 'simdat_colat_plot_' + str(xtrsrc_id[0]) + '.eps'
        plotfiles.append(fname)
        pylab.savefig(plotfiles[-1],dpi=600)
        print plotfiles[-1]
        
        print "Results stored in log file:\n", logfile
        return plotfiles
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()
        logf.close()

def longitude_plot(conn):
    """
    Plot the distribution
    """
    
    try:
        cursor = conn.cursor()
        query = """
        select xtrsrc_id
              ,xtrsrcid
              ,ra_prime/360 as longitude
          from (select xtrsrc_id
                      ,xtrsrcid
                      ,case when y_prime > 0 
                            then case when x_prime > 0 
                                      then 180*atan(y_prime/x_prime)/pi()
                                      else 180+180*atan(y_prime/x_prime)/pi()
                                 end
                            else case when x_prime < 0 
                                      then 180+180*atan(y_prime/x_prime)/pi()
                                      else 360+180*atan(y_prime/x_prime)/pi()
                                 end
                       end as ra_prime
                  from (select r.xtrsrc
                              ,r.wm_ra
                              ,r.wm_decl
                              ,x.id
                              ,sin(rad(wm_decl))*cos(rad(wm_ra))*x.x 
                               + sin(rad(wm_decl))*sin(rad(wm_ra))*x.y 
                               - cos(rad(wm_decl))*x.z as x_prime
                              ,-sin(rad(wm_ra))*x.x 
                               + cos(rad(wm_ra))*x.y as y_prime
                          from assocxtrsource a
                              ,runningcatalog r
                              ,extractedsource x
                         where r.xtrsrc = a.xtrsrc
                           and a.xtrsrc = x.id
                           and r.xtrsrc = 1
                       ) t1
               ) t2
        order by longitude
        """
        cursor.execute(query)
        results = zip(*cursor.fetchall())
        conn.commit()

        xtrsrc_id = results[0]
        xtrsrcid = results[1]
        longitude = results[2]
        
        print "len(longitude) =", len(longitude)
        n = len(longitude)
        U = []
        for i in range(n):
            U.append(((i+1)-0.5)/n) # here i starts at 0, not 100% sure, but Fisher,Lewis&Embleton: i=1,...,n
        
        plotfiles = []
        fig=pylab.figure(figsize=(8,8))
        ax = fig.add_subplot(111)
        ax.scatter(U, longitude, c='r', s=20, edgecolor='r', label=r'Longitude')
        ax.set_xlabel(r'Uniform Quantile', size='x-large')
        ax.set_ylabel(r'Sample Quantile', size='x-large')
        ax.set_xlim(xmin=0)
        ax.set_ylim(ymin=0)
        
        pylab.legend(numpoints=1, loc='best')
        pylab.grid(True)
        
        fname = 'simdat_longitude_plot_' + str(xtrsrc_id[0]) + '.eps'
        plotfiles.append(fname)
        pylab.savefig(plotfiles[-1],dpi=600)
        print plotfiles[-1]
        
        print "Results stored in log file:\n", logfile
        return plotfiles
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()
        logf.close()

def two_variable_plot(conn):
    """
    Plot the distribution
    """
    
    try:
        cursor = conn.cursor()
        # we rotate the mean vector A(pi+decl,ra-pi,0), where A is the rotation matrix
        # for the ra,dec coordinate system
        query = """
        select xtrsrc_id
              ,xtrsrcid
              ,(rad(ra_dblprime)-pi()) * sqrt(sin(rad(decl_dblprime))) as twovar
          from (
                select xtrsrc_id
                      ,xtrsrcid
                      ,acos(z_dblprime) as decl_dblprime
                      ,case when y_dblprime > 0 
                            then case when x_dblprime > 0
                                      then 180*atan(y_dblprime/x_dblprime)/pi()
                                      else 180+180*atan(y_dblprime/x_dblprime)/pi()
                                 end
                            else case when x_dblprime < 0
                                      then 180+180*atan(y_dblprime/x_dblprime)/pi()
                                      else 360+180*atan(y_dblprime/x_dblprime)/pi()
                                 end 
                       end as ra_dblprime
                      ,x_dblprime
                      ,y_dblprime
                      ,z_dblprime
                  from (
                        select r.xtrsrc
                              ,r.wm_ra
                              ,r.wm_decl
                              ,x.id
                              ,sin(3*pi()+rad(wm_decl))*cos(rad(wm_ra)-pi())*x.x 
                               + sin(3*pi()+rad(wm_decl))*sin(rad(wm_ra)-pi())*x.y 
                               - cos(3*pi()+rad(wm_decl))*x.z as x_dblprime
                              ,-sin(rad(wm_ra)-pi())*x.x 
                               + cos(rad(wm_ra)-pi())*x.y as y_dblprime
                              ,cos(3*pi()+rad(wm_decl))*cos(rad(wm_ra)-pi())*x.x 
                               + cos(3*pi()+rad(wm_decl))*sin(rad(wm_ra)-pi())*x.y 
                               + sin(3*pi()+rad(wm_decl))*x.z as z_dblprime  
                          from assocxtrsource a
                              ,runningcatalog r
                              ,extractedsource x
                         where r.xtrsrc = a.xtrsrc
                           and a.xtrsrc = x.id
                           and r.xtrsrc = 1
                       ) t1
               ) t2
        order by twovar
        """
        cursor.execute(query)
        results = zip(*cursor.fetchall())
        conn.commit()

        xtrsrc_id = results[0]
        xtrsrcid = results[1]
        twovar = results[2]
        
        print "len(twovar) =", len(twovar)
        n = len(twovar)
        Norm = []
        for i in range(n):
            p = ((i+1)-0.5)/n # here i starts at 0
            Norm.append(pylab.sqrt(2)*special.erfinv(2*p-1))
        
        plotfiles = []
        fig=pylab.figure(figsize=(8,8))
        ax = fig.add_subplot(111)
        #ax.scatter(Norm, normquant, c='r', s=20, edgecolor='r', label=r'Two-variable')
        ax.scatter(Norm, twovar, c='r', s=20, edgecolor='r', label=r'Two-variable')
        #ax.semilogy(Norm, twovar, 'r-', label=r'Two-variable')
        ax.set_xlabel(r'Normal Quantile', size='x-large')
        ax.set_ylabel(r'Sample Quantile', size='x-large')
        #ax.set_xlim(xmin=0)
        #ax.set_ylim(ymin=0)
        
        pylab.legend(numpoints=1, loc='best')
        pylab.grid(True)
        
        fname = 'simdat_two-variable_plot_' + str(xtrsrc_id[0]) + '.eps'
        plotfiles.append(fname)
        pylab.savefig(plotfiles[-1],dpi=600)
        print plotfiles[-1]
        
        print "Results stored in log file:\n", logfile
        return plotfiles
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()
        logf.close()

def rayleigh_distr_plot(conn):
    """
    Plot the Fisher distribution
    """
    
    try:
        cursor = conn.cursor()
        query = """
        select x.id
              ,a.assoc_distance_arcsec
              ,3600 * deg(2 * ASIN(SQRT((r.x - x.x) * (r.x - x.x)
                                        + (r.y - x.y) * (r.y - x.y)
                                        + (r.z - x.z) * (r.z - x.z)
                                       ) / 2) ) AS distance_arcsec
              ,a.assoc_r
              ,3600 * sqrt(
                           ((r.wm_ra * cos(rad(r.wm_decl)) - x.ra * cos(rad(x.decl))) 
                           * (r.wm_ra * cos(rad(r.wm_decl)) - x.ra * cos(rad(x.decl)))) 
                           / (r.wm_ra_err * r.wm_ra_err + x.ra_err*x.ra_err)
                          +
                           ((r.wm_decl - x.decl) * (r.wm_decl - x.decl)) 
                           / (r.wm_decl_err * r.wm_decl_err + x.decl_err*x.decl_err)
                          ) as r
              ,r.xtrsrc
              ,x.ra * cos(rad(x.decl))
              ,x.decl
              ,x.ra_err
              ,3600 * sqrt(
                           ((r.wm_ra * cos(rad(r.wm_decl)) - x.ra * cos(rad(x.decl))) 
                           * (r.wm_ra * cos(rad(r.wm_decl)) - x.ra * cos(rad(x.decl)))) 
                           / 0.309937661034
                          +
                           ((r.wm_decl - x.decl) * (r.wm_decl - x.decl)) 
                           / 0.126006356623 
                          ) as r2
              ,x.decl_err
              ,3600 * (x.ra * cos(rad(x.decl)) - r.wm_ra * cos(rad(r.wm_decl))) as z_ra
              ,3600 * (x.decl - r.wm_decl) as z_decl
          from assocxtrsource a
              ,runningcatalog r
              ,extractedsource x
         where r.xtrsrc = 1
           and r.xtrsrc = a.xtrsrc
           and a.xtrsrc = x.id
        order by distance_arcsec
        """
        cursor.execute(query)
        results = zip(*cursor.fetchall())
        conn.commit()

        xtrsrcid = results[0]
        assoc_distance_arcsec = results[1]
        distance_arcsec = results[2]
        assoc_r= results[3]
        r = results[4]
        xtrsrc_id = results[5]
        ra = results[6]
        decl = results[7]
        ra_err = results[8]
        r2 = results[9]
        decl_err = results[10]
        z_ra = results[11]
        z_decl = results[12]
        
        #############################################
        print "#############################################\n"

        print "len(distance_arcsec) =", len(distance_arcsec)
        n = len(distance_arcsec)
    
        ra_avg = sum(ra) / n
        ra_min = min(ra)
        ra_max = max(ra)
        ra0 = (ra - ra_avg) * 3600
        #print "ra = ", ra
        std_ra = 0.0
        for i in range(len(ra0)):
            std_ra = std_ra + ra0[i]*ra0[i]
        std_ra = pylab.sqrt(std_ra/n)
        print "std_ra = ", std_ra

        plotfiles = []
        binwidth = 0.1
        ra_bin = pylab.arange(-1.5, 1.5, binwidth) # arcsecs
        #print "ra_bin = ", ra_bin
        
        fig = pylab.figure()
        ax = fig.add_subplot(111)
        cnt,bins,patches = ax.hist(ra0, ra_bin, color='r', label=r'Sample')
        #print "cnt =", cnt
        #print "bins =", bins
        
        g_midbin = []
        gauss = []
        gauss_ideal = []
        for i in range(len(bins)-1):
            g_midbin.append((bins[i]+bins[i+1])/2)
            gauss.append(pylab.exp(-g_midbin[i]*g_midbin[i]/(2*std_ra**2))/(pylab.sqrt(2*pylab.pi)*std_ra))
            gauss_ideal.append(n * gauss[i] * binwidth)

        chisq_ra = 0.0
        print "len(cnt) =", len(cnt)
        print "len(gauss_ideal) =", len(gauss_ideal)
        for i in range(len(gauss_ideal)):
            chisq_ra = chisq_ra + (cnt[i] - gauss_ideal[i])**2/gauss_ideal[i]
        print "chisq_ra = ", chisq_ra
        
        ax.plot(g_midbin, gauss_ideal, 'b--', linewidth=3, label=r'Gaussian')
        
        ax.set_xlabel(r'$z_\alpha$', size='x-large')
        ax.set_ylabel(r'Number', size='x-large')
        for i in range(len(ax.get_xticklabels())):
            ax.get_xticklabels()[i].set_size('x-large')
        for i in range(len(ax.get_yticklabels())):
            ax.get_yticklabels()[i].set_size('x-large')
        pylab.legend(numpoints=1)
        pylab.grid(True)
        fname = 'simdat_ra_distr_' +str(xtrsrc_id[0]) + '.eps'
        plotfiles.append(fname)
        pylab.savefig(plotfiles[-1],dpi=600)
        print plotfiles[-1]

        #############################################
        print "#############################################\n"

        binwidth = 0.2
        z_ra_bin = pylab.arange(-6, 6, binwidth) # arcsecs
        std_z_ra = 0.0
        for i in range(len(z_ra)):
            std_z_ra = std_z_ra + z_ra[i]*z_ra[i]
        std_z_ra = pylab.sqrt(std_z_ra/len(z_ra))
        print "std_z_ra = ", std_z_ra
        fig = pylab.figure()
        ax = fig.add_subplot(111)
        #cnt, bins, patches = ax.hist(z_ra, z_ra_bin, color='r', label=r'Sample')
        cnt, bins, patches = ax.hist(z_ra/std_z_ra, z_ra_bin, color='r', label=r'Sample')
        g_midbin = []
        g = []
        #g = pylab.exp(-z_ra*z_ra/2)/pylab.sqrt(2*pylab.pi)
        g_ideal = []
        for i in range(len(bins)-1):
            g_midbin.append((bins[i] + bins[i+1])/2)
            g.append(pylab.exp(-g_midbin[i]**2/2)/pylab.sqrt(2*pylab.pi))
            g_ideal.append(n * g[i] * binwidth)
        chisq = 0
        #print "len(bins) =", len(bins)
        #print "bins =", bins
        #print "len(g_midbin) =", len(g_midbin)
        #print "g_midbin =", g_midbin
        print "len(cnt) =", len(cnt)
        print "cnt =", cnt
        for i in range(len(g_midbin)):
            chisq = chisq + (cnt[i] - g_ideal[i])**2 / g_ideal[i]
        
        print "g_ideal =", g_ideal
        print "chisq rho = ", chisq
        #ax.plot(g_midbin, g, 'b--', linewidth=2, label=r'Unit Gaussian')
        ax.plot(g_midbin, g_ideal, 'b--', linewidth=3, label=r'Gaussian')
        ax.set_xlabel(r'$z_x$', size='x-large')
        ax.set_ylabel(r'Number', size='x-large')
        for i in range(len(ax.get_xticklabels())):
            ax.get_xticklabels()[i].set_size('x-large')
        for i in range(len(ax.get_yticklabels())):
            ax.get_yticklabels()[i].set_size('x-large')
        pylab.legend(numpoints=1)
        pylab.grid(True)
        fname = 'simdat_z_ra_distr_' +str(xtrsrc_id[0]) + '.eps'
        plotfiles.append(fname)
        pylab.savefig(plotfiles[-1],dpi=600)
        print plotfiles[-1]

        #############################################
        print "#############################################\n"

        binwidth = 0.2
        z_decl_bin = pylab.arange(-6, 6, binwidth) # arcsecs
        std_z_decl = 0.0
        for i in range(len(z_decl)):
            std_z_decl = std_z_decl + z_decl[i]*z_decl[i]
        std_z_decl = pylab.sqrt(std_z_decl/len(z_decl))
        print "std_z_decl = ", std_z_decl
        fig = pylab.figure()
        ax = fig.add_subplot(111)
        #cnt, bins, patches = ax.hist(z_ra, z_ra_bin, color='r', label=r'Sample')
        cnt, bins, patches = ax.hist(z_decl/std_z_decl, z_decl_bin, color='r', label=r'Sample')
        g_midbin = []
        g = []
        #g = pylab.exp(-z_ra*z_ra/2)/pylab.sqrt(2*pylab.pi)
        g_ideal = []
        for i in range(len(bins)-1):
            g_midbin.append((bins[i] + bins[i+1])/2)
            g.append(pylab.exp(-g_midbin[i]**2/2)/pylab.sqrt(2*pylab.pi))
            g_ideal.append(n * g[i] * binwidth)
        #ax.plot(g_midbin, g, 'b--', linewidth=2, label=r'Unit Gaussian')
        ax.plot(g_midbin, g_ideal, 'b--', linewidth=3, label=r'Gaussian')
        ax.set_xlabel(r'$z_y$', size='x-large')
        ax.set_ylabel(r'Number', size='x-large')
        for i in range(len(ax.get_xticklabels())):
            ax.get_xticklabels()[i].set_size('x-large')
        for i in range(len(ax.get_yticklabels())):
            ax.get_yticklabels()[i].set_size('x-large')
        pylab.legend(numpoints=1)
        pylab.grid(True)
        fname = 'simdat_z_decl_distr_' +str(xtrsrc_id[0]) + '.eps'
        plotfiles.append(fname)
        pylab.savefig(plotfiles[-1],dpi=600)
        print plotfiles[-1]

        #############################################
        print "#############################################\n"
        
        #TODO: Use g_midbin values...

        #############################################
        print "#############################################\n"
        
        z = pylab.sqrt((z_ra/std_z_ra)**2 + (z_decl/std_z_decl)**2)
        fig = pylab.figure()
        ax = fig.add_subplot(111)
        binwidth = 0.1
        r_z_bin = pylab.arange(0, 5, binwidth) # arcsecs
        cnt, bins, patches = ax.hist(z, r_z_bin, color='r', label=r'Sample')
        r_z_midbin = []
        r_z = []
        r_z_ideal = []
        for i in range(len(bins)-1):
            r_z_midbin.append((bins[i] + bins[i+1])/2)
            r_z.append(r_z_midbin[i] * pylab.exp(-r_z_midbin[i]**2/2))
            r_z_ideal.append(n * r_z[i] * binwidth)
        chisq = 0.0
        for i in range(len(cnt)):
            chisq = chisq + (cnt[i] - r_z_ideal[i])**2/r_z_ideal[i]
        print "chisq = ", chisq
        ax.plot(r_z_midbin, r_z_ideal, 'b--', linewidth=3, label=r'Rayleigh')
        ax.set_xlabel(r'$\rho$', size='x-large')
        ax.set_ylabel(r'Number', size='x-large')
        for i in range(len(ax.get_xticklabels())):
            ax.get_xticklabels()[i].set_size('x-large')
        for i in range(len(ax.get_yticklabels())):
            ax.get_yticklabels()[i].set_size('x-large')
        pylab.legend(numpoints=1)
        pylab.grid(True)
        fname = 'simdat_r_z_distr_' +str(xtrsrc_id[0]) + '.eps'
        plotfiles.append(fname)
        pylab.savefig(plotfiles[-1],dpi=600)
        print plotfiles[-1]

        #############################################
        print "#############################################\n"

        print "len(decl) = ", len(decl)
        decl_avg = sum(decl) / n
        decl_min = min(decl)
        decl_max = max(decl)
        decl = (decl - decl_avg) * 3600
        #print "decl = ", decl
        std_decl = 0.0
        for i in range(len(decl)):
            std_decl = std_decl + decl[i]*decl[i]
        std_decl = pylab.sqrt(std_decl/n)
        print "std_decl = ", std_decl

        binwidth = 0.05
        decl_bin = pylab.arange(-0.5, 0.5, binwidth) # arcsecs
        fig = pylab.figure()
        ax = fig.add_subplot(111)
        cnt,bins,patches = ax.hist(decl, decl_bin, color='r', label=r'Sample')
        #print "cnt =", cnt
        #print "bins =", bins
        
        g_midbin = []
        gauss = []
        gauss_ideal = []
        for i in range(len(bins)-1):
            g_midbin.append((bins[i]+bins[i+1])/2)
            gauss.append(pylab.exp(-g_midbin[i]*g_midbin[i]/(2*std_decl**2))/(pylab.sqrt(2*pylab.pi)*std_decl))
            gauss_ideal.append(n * gauss[i] * binwidth)
        
        chisq_decl = 0.0
        print "len(cnt) =", len(cnt)
        print "len(gauss_ideal) =", len(gauss_ideal)
        for i in range(len(gauss_ideal)):
            chisq_decl = chisq_decl + (cnt[i] - gauss_ideal[i])**2/gauss_ideal[i]
        print "chisq_decl = ", chisq_decl
        
        ax.plot(g_midbin, gauss_ideal, 'b--', linewidth=3, label=r'Gaussian')
        ax.set_xlabel(r'$z_\delta$', size='x-large')
        ax.set_ylabel(r'Number', size='x-large')
        for i in range(len(ax.get_xticklabels())):
            ax.get_xticklabels()[i].set_size('x-large')
        for i in range(len(ax.get_yticklabels())):
            ax.get_yticklabels()[i].set_size('x-large')
        pylab.legend(numpoints=1)
        pylab.grid(True)
        fname = 'simdat_decl_distr_' +str(xtrsrc_id[0]) + '.eps'
        plotfiles.append(fname)
        pylab.savefig(plotfiles[-1],dpi=600)
        print plotfiles[-1]
        
        #############################################
        print "#############################################\n"

        #r = r2
        print "len(r) = ", len(r)
        #print "r = ", r
        std_r = 0.0
        for i in range(len(r)):
            std_r = std_r + r[i]*r[i]
        std_r = pylab.sqrt(std_r/(2*n))
        print "std_r = ", std_r

        binwidth = 0.1
        r_bin = pylab.arange(0.0, 6.0, binwidth) # arcsecs
        fig = pylab.figure()
        ax = fig.add_subplot(111)
        cnt,bins,patches = ax.hist(r, r_bin, color='r', label=r'Sample')
        #print "cnt =", cnt
        #print "bins =", bins
        
        r_midbin = []
        rayleigh = []
        rayleigh_ideal = []
        for i in range(len(bins)-1):
            r_midbin.append((bins[i]+bins[i+1])/2)
            rayleigh.append(r_midbin[i] * pylab.exp(-r_midbin[i]*r_midbin[i]/(2*std_r**2))/std_r**2)
            rayleigh_ideal.append(n * rayleigh[i] * binwidth)
        #print "r_midbin = ", r_midbin
        #print "rayleigh = ", rayleigh
        #print "rayleigh_ideal = ", rayleigh_ideal
        #print "sum(rayleigh) = ", sum(rayleigh)
        #print "sum(rayleigh_ideal) = ", sum(rayleigh_ideal)
        
        chisq_r = 0.0
        print "len(cnt) =", len(cnt)
        print "len(rayleigh_ideal) =", len(rayleigh_ideal)
        for i in range(len(rayleigh_ideal)):
            chisq_r = chisq_r + (cnt[i] - rayleigh_ideal[i])**2/rayleigh_ideal[i]
        print "chisq_r = ", chisq_r
        
        ax.plot(r_midbin, rayleigh_ideal, 'b--', linewidth=2, label=r'Rayleigh')
        ax.set_xlabel(r'$r$ [dimensionless]', size='x-large')
        ax.set_ylabel(r'Number', size='x-large')
        for i in range(len(ax.get_xticklabels())):
            ax.get_xticklabels()[i].set_size('x-large')
        for i in range(len(ax.get_yticklabels())):
            ax.get_yticklabels()[i].set_size('x-large')
        #ax.set_ylim(ymin=0,ymax=150)
        pylab.legend(numpoints=1)
        pylab.grid(True)
        fname = 'simdat_rayleigh_distr_' +str(xtrsrc_id[0]) + '.eps'
        plotfiles.append(fname)
        pylab.savefig(plotfiles[-1],dpi=600)
        print plotfiles[-1]
        
        #############################################
        print "#############################################\n"

        print "len(r) = ", len(r)
        #print "r = ", r
        std_r = 0.0
        for i in range(len(r)):
            std_r = std_r + r[i]*r[i]
        std_r = pylab.sqrt(std_r/(2*n))
        print "std_r = ", std_r
        
        r2 = []
        for i in range(len(r)):
            r2.append(pylab.exp(-r[i]*r[i]/2)/(2*pylab.pi*ra_err[i]*decl_err[i]))

        binwidth = 0.1
        r_bin = pylab.arange(0.0, 6.0, binwidth) # arcsecs
        fig = pylab.figure()
        ax = fig.add_subplot(111)
        #cnt,bins,patches = ax.hist(r, r_bin, color='r', label=r'Sample')
        cnt,bins,patches = ax.hist(r2, r_bin, color='r', label=r'Sample')
        #print "cnt =", cnt
        #print "bins =", bins
        
        r_midbin = []
        rayleigh = []
        rayleigh_ideal = []
        for i in range(len(bins)-1):
            r_midbin.append((bins[i]+bins[i+1])/2)
            rayleigh.append(pylab.exp(-r_midbin[i]*r_midbin[i]/2)/(2*pylab.pi*0.03371694))
            rayleigh_ideal.append(n * rayleigh[i] * binwidth)
        #print "r_midbin = ", r_midbin
        #print "rayleigh = ", rayleigh
        #print "rayleigh_ideal = ", rayleigh_ideal
        #print "sum(rayleigh) = ", sum(rayleigh)
        #print "sum(rayleigh_ideal) = ", sum(rayleigh_ideal)
        
        chisq_r = 0.0
        print "len(cnt) =", len(cnt)
        print "len(rayleigh_ideal) =", len(rayleigh_ideal)
        for i in range(len(rayleigh_ideal)):
            chisq_r = chisq_r + (cnt[i] - rayleigh_ideal[i])**2/rayleigh_ideal[i]
        print "chisq_r = ", chisq_r
        
        #ax.plot(r_midbin, rayleigh_ideal, 'b--', linewidth=2, label=r'Rayleigh')
        ax.set_xlabel(r'$r$ [dimensionless]', size='x-large')
        ax.set_ylabel(r'Number', size='x-large')
        for i in range(len(ax.get_xticklabels())):
            ax.get_xticklabels()[i].set_size('x-large')
        for i in range(len(ax.get_yticklabels())):
            ax.get_yticklabels()[i].set_size('x-large')
        #ax.set_ylim(ymin=0,ymax=150)
        pylab.legend(numpoints=1)
        pylab.grid(True)
        fname = 'simdat_rayleigh2_distr_' +str(xtrsrc_id[0]) + '.eps'
        plotfiles.append(fname)
        pylab.savefig(plotfiles[-1],dpi=600)
        print plotfiles[-1]
        
        #############################################
        print "#############################################\n"

        print "Results stored in log file:\n", logfile
        return plotfiles
    
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()
        logf.close()

def rayleigh_distr_r_plot(conn):
    """
    Plot the Fisher distribution
    """
    
    try:
        cursor = conn.cursor()
        query = """
        select r.xtrsrc
              ,x.id
              ,a.assoc_distance_arcsec
              ,3600 * deg(2 * ASIN(SQRT((r.x - x.x) * (r.x - x.x)
                                        + (r.y - x.y) * (r.y - x.y)
                                        + (r.z - x.z) * (r.z - x.z)
                                       ) / 2) ) AS distance_arcsec
              ,a.assoc_r
              ,3600 * sqrt(
                           ((r.wm_ra * cos(rad(r.wm_decl)) - x.ra * cos(rad(x.decl))) 
                           * (r.wm_ra * cos(rad(r.wm_decl)) - x.ra * cos(rad(x.decl)))) 
                           / (r.wm_ra_err * r.wm_ra_err + x.ra_err*x.ra_err)
                          +
                           ((r.wm_decl - x.decl) * (r.wm_decl - x.decl)) 
                           / (r.wm_decl_err * r.wm_decl_err + x.decl_err*x.decl_err)
                          ) as r
              ,x.ra * cos(rad(x.decl))
              ,x.decl
              ,x.ra_err
              ,x.decl_err
          from assocxtrsource a
              ,runningcatalog r
              ,extractedsource x
         where r.xtrsrc = 20
           and r.xtrsrc = a.xtrsrc
           and a.xtrsrc = x.id
        order by r.xtrsrc
                ,a.xtrsrc
        """
        cursor.execute(query)
        results = zip(*cursor.fetchall())
        conn.commit()

        xtrsrcid = results[0]
        xtrsrc = results[1]
        assoc_distance_arcsec = results[2]
        distance_arcsec = results[3]
        assoc_r = results[4]
        r = results[5]
        ra = results[6]
        decl = results[7]
        ra_err = results[8]
        decl_err = results[9]
        
        n = len(r)
        ra_avg = sum(ra) / n
        ra = (ra - ra_avg) * 3600
        decl_avg = sum(decl) / n
        decl = (decl - decl_avg) * 3600
            
        #############################################
        print "#############################################\n"

        tot = len(r)
        print "tot=",tot
        
        rayl = []
        for i in range(len(ra)):
            rayl.append(pylab.sqrt(ra[i]**2/ra_err[i]**2+decl[i]**2/decl_err[i]**2))
        
        plotfiles = []
        binwidth = 0.1
        r_bin = pylab.arange(0.0, 6.0, binwidth) # arcsecs
        #print "ra_bin = ", ra_bin
        
        fig = pylab.figure(figsize=(4,4))
        #fig = pylab.figure()
        ax = fig.add_subplot(111)
        #cnt,bins,patches = ax.hist(ra, ra_bin, color='r', label=r'Sample')
        cnt,bins,patches = ax.hist(rayl, r_bin, color='r', label=r'Sample $r$')
        #print "cnt =", cnt
        #print "bins =", bins
        
        r_midbin = []
        rayleigh = []
        rayleigh_ideal = []
        for i in range(len(bins)-1):
            r_midbin.append((bins[i]+bins[i+1])/2)
            rayleigh.append(r_midbin[i]*pylab.exp(-r_midbin[i]*r_midbin[i]/2))
            #rayleigh.append(pylab.exp(-r_midbin[i]*r_midbin[i]/2)/(2*pylab.pi*ra_err[i]*decl_err[i]))
            rayleigh_ideal.append(n * rayleigh[i] * binwidth)

        ax.plot(r_midbin, rayleigh_ideal, 'b--', linewidth=2, label=r'Rayleigh')
        
        ax.set_xlabel(r'$r$ [dimensionless]', size='x-large')
        ax.set_ylabel(r'Number', size='x-large')
        for i in range(len(ax.get_xticklabels())):
            ax.get_xticklabels()[i].set_size('x-large')
        for i in range(len(ax.get_yticklabels())):
            ax.get_yticklabels()[i].set_size('x-large')
        #ax.set_ylim(ymin=0,ymax=150)
        pylab.legend(numpoints=1)
        pylab.grid(True)
        fname = 'simdat_sqrt_rsq_distr_' +str(xtrsrcid[0]) + '.eps'
        plotfiles.append(fname)
        pylab.savefig(plotfiles[-1],dpi=600)
        print plotfiles[-1]
        
        print "Results stored in log file:\n", logfile
        return plotfiles
    
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()
        logf.close()

def z_alpha_decl_plot(conn, id):
    """
    Plot the alpha/decl distribution
    """
    
    try:
        cursor = conn.cursor()
        query = """
        SELECT r.xtrsrc
              ,3600 * (x.ra * cos(rad(x.decl))  - r.wm_ra * cos(rad(r.wm_decl))) AS z_alpha
              ,3600 * (x.decl - r.wm_decl) AS z_delta
          FROM assocxtrsource a
              ,runningcatalog r
              ,extractedsource x
         WHERE r.xtrsrc = %s
           AND r.xtrsrc = a.xtrsrc
           AND a.xtrsrc = x.id
        ORDER BY z_alpha
        """
        cursor.execute(query, (id,))
        results = zip(*cursor.fetchall())
        conn.commit()

        xtrsrc_id = results[0]
        z_alpha = results[1]
        z_delta = results[2]
        
        #############################################
        print "############### z_alpha ##############################\n"

        n = len(z_alpha)
        print "len(z_alpha) =", n
    
        sigma_alpha_sq = 0
        for i in range(n):
            sigma_alpha_sq = sigma_alpha_sq + z_alpha[i]*z_alpha[i]
        sigma_alpha_sq = sigma_alpha_sq / n
        print "sigma_alpha_sq =", sigma_alpha_sq

        plotfiles = []
        
        binwidth = 0.1
        ra_bin = pylab.arange(-1.5, 1.5, binwidth) # arcsecs
        #print "ra_bin = ", ra_bin
        
        fig = pylab.figure(figsize=(12,6))
        ax1 = fig.add_subplot(121)
        cnt, bins, patches = ax1.hist(z_alpha, ra_bin, color='r', label=r'Sample')
        #print "len(cnt) =", len(cnt), "; cnt =", cnt
        print "len(cnt) =", len(cnt)
        #print "len(bins) =", len(bins), "; bins =", bins
        
        midbins = []
        gauss = []
        gauss_ideal = []
        chisq = 0
        for i in range(len(bins)-1):
            midbins.append((bins[i] + bins[i+1]) / 2)
            gauss.append(pylab.exp(-midbins[i]*midbins[i]/(2*sigma_alpha_sq))/(pylab.sqrt(2*pylab.pi*sigma_alpha_sq)))
            gauss_ideal.append(n * gauss[i] * binwidth)
            chisq = chisq + (cnt[i] - gauss_ideal[i])**2 / gauss_ideal[i]

        #print "len(gauss_ideal) =", len(gauss_ideal), "; gauss_ideal =", gauss_ideal
        print "chisq =", chisq
        
        ax1.plot(midbins, gauss_ideal, 'b--', linewidth=3, label=r'Gaussian')
        ax1.set_xlabel(r'$z_\alpha$', size='x-large')
        ax1.set_ylabel(r'Number', size='x-large')
        for i in range(len(ax1.get_xticklabels())):
            ax1.get_xticklabels()[i].set_size('x-large')
        for i in range(len(ax1.get_yticklabels())):
            ax1.get_yticklabels()[i].set_size('x-large')
        ax1.set_ylim(ymax=160)
        ax1.legend(numpoints=1)
        ax1.grid(True)

        ##########################################
        print "############### z_delta ##############################\n"

        sigma_delta_sq = 0
        for i in range(n):
            sigma_delta_sq = sigma_delta_sq + z_delta[i]*z_delta[i]
        sigma_delta_sq = sigma_delta_sq / n
        print "sigma_delta_sq =", sigma_delta_sq

        binwidth = 0.05
        delta_bin = pylab.arange(-0.6, 0.6, binwidth) # arcsecs
        #print "delta_bin = ", delta_bin
        
        ax2 = fig.add_subplot(122)
        cnt, bins, patches = ax2.hist(z_delta, delta_bin, color='r', label=r'Sample')
        #print "len(cnt) =", len(cnt), "; cnt =", cnt
        print "len(cnt) =", len(cnt)
        #print "len(bins) =", len(bins), "; bins =", bins
        
        midbins = []
        gauss = []
        gauss_ideal = []
        chisq = 0
        for i in range(len(bins) - 1):
            midbins.append((bins[i] + bins[i+1]) / 2)
            gauss.append(pylab.exp(-midbins[i]*midbins[i]/(2*sigma_delta_sq))/(pylab.sqrt(2*pylab.pi*sigma_delta_sq)))
            gauss_ideal.append(n * gauss[i] * binwidth)
            chisq = chisq + (cnt[i] - gauss_ideal[i])**2 / gauss_ideal[i]

        #print "len(gauss_ideal) =", len(gauss_ideal), "; gauss_ideal =", gauss_ideal
        print "chisq =", chisq
        
        ax2.plot(midbins, gauss_ideal, 'b--', linewidth=3, label=r'Gaussian')
        ax2.set_xlabel(r'$z_\delta$', size='x-large')
        #ax2.set_ylabel(r'Number', size='x-large')
        for i in range(len(ax2.get_xticklabels())):
            ax2.get_xticklabels()[i].set_size('x-large')
        for i in range(len(ax2.get_yticklabels())):
            ax2.get_yticklabels()[i].set_size('x-large')
        ax2.set_ylim(ymax=ax1.get_ylim()[1])
        ax2.legend(numpoints=1)
        ax2.grid(True)

        fname = 'simdat_z_alpha_delta_distr_' +str(xtrsrc_id[0]) + '.eps'
        plotfiles.append(fname)
        pylab.savefig(plotfiles[-1],dpi=600)
        print plotfiles[-1]

        #############################################
        print "############### z_x ##################################\n"

        z_x = []
        for i in range(n):
            z_x.append(z_alpha[i] / pylab.sqrt(sigma_alpha_sq))

        binwidth = 0.2
        z_x_bin = pylab.arange(-6, 6, binwidth)
        
        fig = pylab.figure(figsize=(12,6))
        ax1 = fig.add_subplot(121)
        cnt, bins, patches = ax1.hist(z_x, z_x_bin, color='r', label=r'Sample')
        
        #print "len(cnt) =", len(cnt), "; cnt =", cnt
        print "len(cnt) =", len(cnt)
        #print "len(bins) =", len(bins), "; bins =", bins
        
        midbins = []
        gauss = []
        gauss_ideal = []
        chisq = 0
        for i in range(len(bins)-1):
            midbins.append((bins[i] + bins[i+1]) / 2)
            gauss.append(pylab.exp(-midbins[i]*midbins[i]/2)/pylab.sqrt(2*pylab.pi))
            gauss_ideal.append(n * gauss[i] * binwidth)
            chisq = chisq + (cnt[i] - gauss_ideal[i])**2 / gauss_ideal[i]

        #print "len(gauss_ideal) =", len(gauss_ideal), "; gauss_ideal =", gauss_ideal
        print "chisq =", chisq
        
        ax1.plot(midbins, gauss_ideal, 'b--', linewidth=3, label=r'Gaussian')
        ax1.set_xlabel(r'$z_x$', size='x-large')
        ax1.set_ylabel(r'Number', size='x-large')
        for i in range(len(ax1.get_xticklabels())):
            ax1.get_xticklabels()[i].set_size('x-large')
        for i in range(len(ax1.get_yticklabels())):
            ax1.get_yticklabels()[i].set_size('x-large')
        ax1.set_ylim(ymax=100)
        ax1.legend(numpoints=1)
        ax1.grid(True)

        #############################################
        print "############### z_y ##################################\n"

        z_y = []
        for i in range(n):
            z_y.append(z_delta[i] / pylab.sqrt(sigma_delta_sq))

        binwidth = 0.2
        z_y_bin = pylab.arange(-6, 6, binwidth)
        
        ax2 = fig.add_subplot(122)
        cnt, bins, patches = ax2.hist(z_y, z_y_bin, color='r', label=r'Sample')
        
        #print "len(cnt) =", len(cnt), "; cnt =", cnt
        print "len(cnt) =", len(cnt)
        #print "len(bins) =", len(bins), "; bins =", bins
        
        midbins = []
        gauss = []
        gauss_ideal = []
        chisq = 0
        for i in range(len(bins)-1):
            midbins.append((bins[i] + bins[i+1]) / 2)
            gauss.append(pylab.exp(-midbins[i]*midbins[i]/2)/pylab.sqrt(2*pylab.pi))
            gauss_ideal.append(n * gauss[i] * binwidth)
            chisq = chisq + (cnt[i] - gauss_ideal[i])**2 / gauss_ideal[i]

        #print "len(gauss_ideal) =", len(gauss_ideal), "; gauss_ideal =", gauss_ideal
        print "chisq =", chisq
        
        ax2.plot(midbins, gauss_ideal, 'b--', linewidth=3, label=r'Gaussian')
        ax2.set_xlabel(r'$z_y$', size='x-large')
        #ax2.set_ylabel(r'Number', size='x-large')
        for i in range(len(ax2.get_xticklabels())):
            ax2.get_xticklabels()[i].set_size('x-large')
        for i in range(len(ax2.get_yticklabels())):
            ax2.get_yticklabels()[i].set_size('x-large')
        ax2.set_ylim(ymax=100)
        ax2.legend(numpoints=1)
        ax2.grid(True)

        fname = 'simdat_z_x_y_distr_' +str(xtrsrc_id[0]) + '.eps'
        plotfiles.append(fname)
        pylab.savefig(plotfiles[-1],dpi=600)
        print plotfiles[-1]

        #############################################
        print "############### rho ##################################\n"

        rho = []
        for i in range(n):
            rho.append(pylab.sqrt(z_x[i]**2 + z_y[i]**2))

        binwidth = 0.1
        rho_bin = pylab.arange(0, 5, binwidth)
        
        fig = pylab.figure()
        ax1 = fig.add_subplot(111)
        cnt, bins, patches = ax1.hist(rho, rho_bin, color='r', label=r'Sample')
        
        #print "len(cnt) =", len(cnt), "; cnt =", cnt
        print "len(cnt) =", len(cnt)
        #print "len(bins) =", len(bins), "; bins =", bins
        
        midbins = []
        rayleigh = []
        rayleigh_ideal = []
        chisq = 0
        for i in range(len(bins)-1):
            midbins.append((bins[i] + bins[i+1]) / 2)
            rayleigh.append(midbins[i] * pylab.exp(-midbins[i]**2/2))
            rayleigh_ideal.append(n * rayleigh[i] * binwidth)
            chisq = chisq + (cnt[i] - rayleigh_ideal[i])**2 / rayleigh_ideal[i]
            #chisq = chisq + (cnt[i] - rayleigh[i])**2 / rayleigh[i]

        #print "len(rayleigh_ideal) =", len(rayleigh_ideal), "; rayleigh_ideal =", rayleigh_ideal
        #print "len(rayleigh) =", len(rayleigh), "; rayleigh =", rayleigh
        print "chisq =", chisq
        
        ax1.plot(midbins, rayleigh_ideal, 'b--', linewidth=3, label=r'Rayleigh')
        #ax1.plot(midbins, rayleigh, 'b--', linewidth=3, label=r'Rayleigh')
        ax1.set_xlabel(r'$\rho$', size='x-large')
        ax1.set_ylabel(r'Number', size='x-large')
        for i in range(len(ax1.get_xticklabels())):
            ax1.get_xticklabels()[i].set_size('x-large')
        for i in range(len(ax1.get_yticklabels())):
            ax1.get_yticklabels()[i].set_size('x-large')
        ax1.set_ylim(ymax=80)
        ax1.legend(numpoints=1)
        ax1.grid(True)

        fname = 'simdat_rho_distr_' +str(xtrsrc_id[0]) + '.eps'
        plotfiles.append(fname)
        pylab.savefig(plotfiles[-1],dpi=600)
        print plotfiles[-1]

        #############################################
        print "######################################################\n"

        #print "Results stored in log file:\n", logfile
        return plotfiles
    
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()
        logf.close()

def z_alpha_decl_errors_plot(conn):
    """
    Plot the alpha/decl distribution
    """
    
    try:
        cursor = conn.cursor()
        query = """
        SELECT r.xtrsrc
              ,3600 * (x.ra * cos(rad(x.decl))  - r.wm_ra * cos(rad(r.wm_decl))) / ra_err
               AS z_x
              ,3600 * (x.decl - r.wm_decl) / decl_err AS z_y
          FROM assocxtrsource a
              ,runningcatalog r
              ,extractedsource x
         WHERE r.xtrsrc = 1
           AND r.xtrsrc = a.xtrsrc
           AND a.xtrsrc = x.id
        ORDER BY z_x
        """
        cursor.execute(query)
        results = zip(*cursor.fetchall())
        conn.commit()

        xtrsrc_id = results[0]
        z_x = results[1]
        z_y = results[2]
        
        n = len(z_x)

        #############################################
        print "############### z_x ##################################\n"

        binwidth = 0.2
        z_x_bin = pylab.arange(-6, 6, binwidth)
        
        plotfiles = []
        fig = pylab.figure(figsize=(12,6))
        ax1 = fig.add_subplot(121)
        cnt, bins, patches = ax1.hist(z_x, z_x_bin, color='r', label=r'Sample')
        
        print "len(cnt) =", len(cnt), "; cnt =", cnt
        #print "len(bins) =", len(bins), "; bins =", bins
        
        midbins = []
        gauss = []
        gauss_ideal = []
        chisq = 0
        for i in range(len(bins)-1):
            midbins.append((bins[i] + bins[i+1]) / 2)
            gauss.append(pylab.exp(-midbins[i]*midbins[i]/2)/pylab.sqrt(2*pylab.pi))
            gauss_ideal.append(n * gauss[i] * binwidth)
            chisq = chisq + (cnt[i] - gauss_ideal[i])**2 / gauss_ideal[i]

        print "len(gauss_ideal) =", len(gauss_ideal), "; gauss_ideal =", gauss_ideal
        print "chisq =", chisq
        
        ax1.plot(midbins, gauss_ideal, 'b--', linewidth=3, label=r'Gaussian')
        ax1.set_xlabel(r'$z_x$', size='x-large')
        ax1.set_ylabel(r'Number', size='x-large')
        for i in range(len(ax1.get_xticklabels())):
            ax1.get_xticklabels()[i].set_size('x-large')
        for i in range(len(ax1.get_yticklabels())):
            ax1.get_yticklabels()[i].set_size('x-large')
        ax1.set_ylim(ymax=100)
        ax1.legend(numpoints=1)
        ax1.grid(True)

        #############################################
        print "############### z_y ##################################\n"

        binwidth = 0.2
        z_y_bin = pylab.arange(-6, 6, binwidth)
        
        ax2 = fig.add_subplot(122)
        cnt, bins, patches = ax2.hist(z_y, z_y_bin, color='r', label=r'Sample')
        
        print "len(cnt) =", len(cnt), "; cnt =", cnt
        #print "len(bins) =", len(bins), "; bins =", bins
        
        midbins = []
        gauss = []
        gauss_ideal = []
        chisq = 0
        for i in range(len(bins)-1):
            midbins.append((bins[i] + bins[i+1]) / 2)
            gauss.append(pylab.exp(-midbins[i]*midbins[i]/2)/pylab.sqrt(2*pylab.pi))
            gauss_ideal.append(n * gauss[i] * binwidth)
            chisq = chisq + (cnt[i] - gauss_ideal[i])**2 / gauss_ideal[i]

        print "len(gauss_ideal) =", len(gauss_ideal), "; gauss_ideal =", gauss_ideal
        print "chisq =", chisq
        
        ax2.plot(midbins, gauss_ideal, 'b--', linewidth=3, label=r'Gaussian')
        ax2.set_xlabel(r'$z_y$', size='x-large')
        #ax2.set_ylabel(r'Number', size='x-large')
        for i in range(len(ax2.get_xticklabels())):
            ax2.get_xticklabels()[i].set_size('x-large')
        for i in range(len(ax2.get_yticklabels())):
            ax2.get_yticklabels()[i].set_size('x-large')
        ax2.set_ylim(ymax=100)
        ax2.legend(numpoints=1)
        ax2.grid(True)

        fname = 'simdat_z_x_y_errors_distr_' +str(xtrsrc_id[0]) + '.eps'
        plotfiles.append(fname)
        pylab.savefig(plotfiles[-1],dpi=600)
        print plotfiles[-1]

        #############################################
        print "############### rho ##################################\n"

        rho = []
        for i in range(n):
            rho.append(pylab.sqrt(z_x[i]**2 + z_y[i]**2))

        binwidth = 0.1
        rho_bin = pylab.arange(0, 5, binwidth)
        
        fig = pylab.figure()
        ax1 = fig.add_subplot(111)
        cnt, bins, patches = ax1.hist(rho, rho_bin, color='r', label=r'Sample')
        
        print "len(cnt) =", len(cnt), "; cnt =", cnt
        #print "len(bins) =", len(bins), "; bins =", bins
        
        midbins = []
        rayleigh = []
        rayleigh_ideal = []
        chisq = 0
        for i in range(len(bins)-1):
            midbins.append((bins[i] + bins[i+1]) / 2)
            rayleigh.append(midbins[i] * pylab.exp(-midbins[i]**2/2))
            rayleigh_ideal.append(n * rayleigh[i] * binwidth)
            chisq = chisq + (cnt[i] - rayleigh_ideal[i])**2 / rayleigh_ideal[i]

        print "len(rayleigh_ideal) =", len(rayleigh_ideal), "; rayleigh_ideal =", rayleigh_ideal
        print "chisq =", chisq
        
        ax1.plot(midbins, rayleigh_ideal, 'b--', linewidth=3, label=r'Rayleigh')
        ax1.set_xlabel(r'$\rho$', size='x-large')
        ax1.set_ylabel(r'Number', size='x-large')
        for i in range(len(ax1.get_xticklabels())):
            ax1.get_xticklabels()[i].set_size('x-large')
        for i in range(len(ax1.get_yticklabels())):
            ax1.get_yticklabels()[i].set_size('x-large')
        ax1.set_ylim(ymax=80)
        ax1.legend(numpoints=1)
        ax1.grid(True)

        fname = 'simdat_rho_errors_distr_' +str(xtrsrc_id[0]) + '.eps'
        plotfiles.append(fname)
        pylab.savefig(plotfiles[-1],dpi=600)
        print plotfiles[-1]

        #############################################
        print "######################################################\n"

        print "Results stored in log file:\n", logfile
        return plotfiles
    
    except db.Error, e:
        logging.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()
        logf.close()

