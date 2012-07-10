#!/usr/bin/python

import os, errno, time, sys, pylab
from scipy import *
from scipy import optimize
from scipy import special
from scipy import stats
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
          from assocxtrsources a
              ,runningcatalog r
              ,extractedsource x
         where r.xtrsrc_id = 1
           and a.xtrsrc_id = r.xtrsrc_id
           and a.assoc_xtrsrc_id = x.xtrsrcid
        order by a.assoc_xtrsrc_id
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
          from (select r.xtrsrc_id
                      ,r.wm_ra
                      ,r.wm_decl
                      ,x.xtrsrcid
                      ,cos(rad(wm_decl))*cos(rad(wm_ra))*x.x
                       + cos(rad(wm_decl))*sin(rad(wm_ra))*x.y
                       + sin(rad(wm_decl))*x.z as z_prime
                  from assocxtrsources a
                      ,runningcatalog r
                      ,extractedsource x
                 where r.xtrsrc_id = a.xtrsrc_id
                   and a.assoc_xtrsrc_id = x.xtrsrcid
                   and r.xtrsrc_id = 1
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
            c = 1./n - 2. * (i+1.) / (n*n*(n+1.))
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
        chisqfit_hat2 = 0.0
        for i in range(n):
            D_n_plus.append((i+1)/float(n) - 1. + pylab.exp(-kappa_hat * colat[i]))
            #print "D_n_plus[",i,"] =",D_n_plus[-1],\
            #      " = (i+1)/n ", (i+1.)/n, \
            #      " pylab.exp(-kappa_hat * colat[i]) = ", pylab.exp(-kappa_hat * colat[i]), \
            #      " (i+1)/n -1 + pylab.exp(-kappa_hat * colat[i]) = ", (i+1)/float(n) -1. + pylab.exp(-kappa_hat * colat[i]) 
            D_n_min.append(1.-pylab.exp(-kappa_hat*colat[i]) - i/float(n))
            chisqfit1.append(m_hat1*E[i])
            chisqfit2.append(m_hat2*E[i])
            chisqfit_robust.append(kappa_robust*E[i])
            chisqfit_hat.append(E[i]/kappa_hat)
            chisqfit_hat2 = chisqfit_hat2 + (colat[i]-E[i]/kappa_hat)**2/(E[i]/kappa_hat)
        
        print "chisqfit_hat2 =", chisqfit_hat2
        #print "D_n_plus = ", D_n_plus
        D_n_plus_max = max(D_n_plus)
        print "D_n_plus_max = ", D_n_plus_max
        D_n_min_max = max(D_n_min)
        print "D_n_min_max = ", D_n_min_max
        D_n = max(D_n_plus_max, D_n_min_max)
        print "D_n = ", D_n
        M_E = (D_n - 0.2/n) * (pylab.sqrt(n) + 0.26 + 0.5/pylab.sqrt(n))
        print "M_E = ", M_E
        
        plotfiles = []
        #fig=pylab.figure(figsize=(8,8))
        fig=pylab.figure()
        ax = fig.add_subplot(111)
        ax.scatter(E, colat, c='r', s=20, edgecolor='r', label=r'Colatitude')
        #ax.plot(E, chisqfit1, 'b-', linewidth=2,label=r'$\chi^2_1$ fit')
        #ax.plot(E, chisqfit2, 'g:', linewidth=2,label=r'$\chi^2_2$ fit')
        #ax.plot(E, chisqfit_robust, 'k--', linewidth=2,label=r'$\kappa_r$ fit')
        ax.plot(E, chisqfit_hat, 'b--', linewidth=3, label=r'$\hat{\kappa}$ fit')
        ax.set_xlabel(r'Exponential Quantile, $E_i$', size='x-large')
        ax.set_ylabel(r'Sample Quantile, $X_{(i)}$', size='x-large')
        ax.set_xlim(xmin=0)
        ax.set_ylim(ymin=0)
        
        pylab.legend(numpoints=1, loc='upper left')
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
                  from (select r.xtrsrc_id
                              ,r.wm_ra
                              ,r.wm_decl
                              ,x.xtrsrcid
                              ,sin(rad(wm_decl))*cos(rad(wm_ra))*x.x 
                               + sin(rad(wm_decl))*sin(rad(wm_ra))*x.y 
                               - cos(rad(wm_decl))*x.z as x_prime
                              ,-sin(rad(wm_ra))*x.x 
                               + cos(rad(wm_ra))*x.y as y_prime
                          from assocxtrsources a
                              ,runningcatalog r
                              ,extractedsource x
                         where r.xtrsrc_id = a.xtrsrc_id
                           and a.assoc_xtrsrc_id = x.xtrsrcid
                           and r.xtrsrc_id = 1
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
        fig=pylab.figure(figsize=(6,6))
        ax = fig.add_subplot(111)
        ax.scatter(U, longitude, c='r', s=20, edgecolor='r', label=r'Longitude')
        ax.plot(U, U, 'b--', linewidth=3, label=r'$U(x)=x$')
        ax.set_xlabel(r'Uniform Quantile, $U_i$', size='x-large')
        ax.set_ylabel(r'Sample Quantile, $X_{(i)}$', size='x-large')
        ax.set_xlim(xmin=0, xmax=1)
        ax.set_ylim(ymin=0, ymax=1)
        
        pylab.legend(numpoints=1, loc='upper left')
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
        SELECT xtrsrc_id
              ,xtrsrcid
              ,ra_rad_dblprime * sqrt(sin(decl_rad_dblprime)) AS twovar
          FROM (
                SELECT xtrsrc_id
                      ,xtrsrcid
                      ,ACOS(z_dblprime) AS decl_rad_dblprime
                      ,ATAN(y_dblprime/x_dblprime) AS ra_rad_dblprime
                      ,x_dblprime
                      ,y_dblprime
                      ,z_dblprime
                  FROM (
                        SELECT r.xtrsrc_id
                              ,r.wm_ra
                              ,r.wm_decl
                              ,x.xtrsrcid
                              ,COS(rad(wm_decl)) * COS(rad(wm_ra)) * x.x 
                               + COS(rad(wm_decl)) * SIN(rad(wm_ra)) * x.y 
                               + SIN(rad(wm_decl)) * x.z 
                               AS x_dblprime
                              ,SIN(rad(wm_ra)) * x.x 
                               - COS(rad(wm_ra)) * x.y 
                               AS y_dblprime
                              ,SIN(rad(wm_decl)) * COS(rad(wm_ra)) * x.x 
                               + SIN(rad(wm_decl)) * SIN(rad(wm_ra)) * x.y 
                               - COS(rad(wm_decl)) * x.z 
                               AS z_dblprime  
                          FROM assocxtrsources a
                              ,runningcatalog r
                              ,extractedsource x
                         WHERE r.xtrsrc_id = a.xtrsrc_id
                           AND a.assoc_xtrsrc_id = x.xtrsrcid
                           AND r.xtrsrc_id = 1 
                       ) t1
               ) t2
        ORDER BY twovar
        """
        cursor.execute(query)
        results = zip(*cursor.fetchall())
        conn.commit()

        xtrsrc_id = results[0]
        xtrsrcid = results[1]
        twovar = results[2]
        
        print "len(twovar) =", len(twovar)
        n = len(twovar)
        Nsamp = []
        Qsamp=[]
        iksij = []
        ikssq = []
        for i in range(n):
            p = ((i+1)-0.5)/n # here i starts at 0
            Nsamp.append(pylab.sqrt(2)*special.erfinv(2*p-1))
            iksij.append(Nsamp[i]*twovar[i])
            ikssq.append(Nsamp[i]*Nsamp[i])
            Qsamp.append(1000000*twovar[i])

        m_hat = sum(iksij)/sum(ikssq)
        print "1/sqrt(m_hat) = ", m_hat
        print "m_hat = ", 1./m_hat**2
        m = []
        kappa_hat = 1.286e12
        print "kappa_hat = ", kappa_hat
        kappa = []
        for i in range(n):
            kappa.append(1000000*Nsamp[i]/pylab.sqrt(kappa_hat))
            m.append(1000000*m_hat*Nsamp[i])
        
        plotfiles = []
        fig=pylab.figure(figsize=(8,8))
        #fig=pylab.figure()
        ax = fig.add_subplot(111)
        #ax.scatter(Norm, normquant, c='r', s=20, edgecolor='r', label=r'Two-variable')
        #ax.scatter(Norm, twovar, c='r', s=20, edgecolor='r', label=r'Two-variable')
        ax.scatter(Nsamp, Qsamp, c='r', s=20, edgecolor='r', label=r'Two-variable')
        ax.plot(Nsamp, kappa, 'b--', linewidth=3, label=r'$\hat{\kappa}$')
        ax.plot(Nsamp, m, 'k-.', linewidth=3, label=r'$1/\sqrt{\kappa_{\mathrm{fit}}}$')
        #ax.semilogy(Norm, twovar, 'r-', label=r'Two-variable')
        ax.set_xlabel(r'Normal Quantile, $N_i$', size='x-large')
        ax.set_ylabel(r'Sample Quantile [$\times 10^{-6}$], $X_{(i)}$', size='x-large')
        #ax.set_xlim(xmin=0)
        #ax.set_ylim(ymin=0)
        
        pylab.legend(numpoints=1, loc='upper left')
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

def fisher_distr_plot(conn):
    """
    Plot the Fisher distribution
    """
    
    try:
        cursor = conn.cursor()
        query = """
        select x.xtrsrcid
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
              ,r.xtrsrc_id
          from assocxtrsources a
              ,runningcatalog r
              ,extractedsource x
         where r.xtrsrc_id = 1
           and r.xtrsrc_id = a.xtrsrc_id
           and a.assoc_xtrsrc_id = x.xtrsrcid
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
        
        print "len(distance_arcsec) =", len(distance_arcsec)
        n = len(distance_arcsec)
    
        plotfiles = []
        binwidth = 0.02
        theta_arcsec = pylab.arange(0.0, 1.0, binwidth) # arcsecs
        print "theta_arcsec = ", theta_arcsec
        #g = kappa * pylab.exp(kappa*(cos(theta_rad)-1.)) 
        
        fig = pylab.figure(figsize=(8,8))
        ax = fig.add_subplot(111)
        
        #cnt,bins,patches = ax.hist(distance_arcsec, theta_arcsec, fc='r', normed=1, alpha=0.75, label=r'Sample')
        cnt,bins,patches = ax.hist(distance_arcsec, theta_arcsec, color='r', label=r'Sample')
        print "cnt =", cnt
        print "bins =", bins
        
        kappa = 2.18643758617e+12
        theta_rad = []
        fisher_arcsec = []
        fisher = []
        f_approx = []
        fisher_ideal = []
        f_a_ideal=[]
        for i in range(len(bins)-1):
            theta_rad.append(((bins[i]+bins[i+1])/2) * pylab.pi / 648000.) # theta_rad is at the mid bin
            fisher_arcsec.append((bins[i]+bins[i+1])/2)
            fisher.append(kappa * sin(theta_rad[i]) * pylab.exp(kappa*(cos(theta_rad[i]) - 1.)))
            f_approx.append(kappa*theta_rad[i]*pylab.exp(-kappa*theta_rad[i]**2/2))
            fisher_ideal.append(n * fisher[i] * (binwidth * pylab.pi / 648000.))
            f_a_ideal.append(n * f_approx[i] * (binwidth * pylab.pi / 648000.))
        print "fisher_arcsec =", fisher_arcsec
        print "theta_rad =", theta_rad
        print "fisher =", fisher
        print "fisher_ideal =", fisher_ideal
        print "sum(cnt) =", sum(cnt)
        print "sum(fisher) =", sum(fisher)
        print "sum(fisher_ideal) =", sum(fisher_ideal)

        # f = kappa * sin(theta_rad) * pylab.exp(kappa*(cos(theta_rad) - 1.)) 
        
        int_f = 0.0
        for i in range(len(theta_rad)):
            int_f = int_f + (binwidth * pylab.pi / 648000.) * fisher[i] / n
        print "int_f=",int_f

        f_obs = pylab.array(cnt)
        f_exp = pylab.array(fisher_ideal)
        print "###########################################################################"
        print "stats.chisquare(f_obs, f_exp=f_exp) = ", stats.chisquare(f_obs, f_exp=f_exp)
        print "###########################################################################"

        ax.plot(fisher_arcsec, fisher_ideal, 'b--', linewidth=3, label=r'Fisher')
        #ax.plot(fisher_arcsec, f_a_ideal, 'k:', linewidth=3, label=r'Approx Fisher')
        
        ax.set_xlabel(r'$\theta$ [arcsec]', size='x-large')
        ax.set_ylabel(r'Number', size='x-large')
        for i in range(len(ax.get_xticklabels())):
            ax.get_xticklabels()[i].set_size('x-large')
        for i in range(len(ax.get_yticklabels())):
            ax.get_yticklabels()[i].set_size('x-large')
        pylab.legend(numpoints=1)
        pylab.grid(True)
        fname = 'simdat_distr_fisher_' +str(xtrsrc_id[0]) + '.eps'
        plotfiles.append(fname)
        pylab.savefig(plotfiles[-1],dpi=600)
        print plotfiles[-1]

        ###############

        fig = pylab.figure(figsize=(8,8))
        ax = fig.add_subplot(111)
        
        binwidth = 0.2
        r_bin = pylab.arange(0.0, 6.0, binwidth) # arcsecs
        print "r_bin = ", r_bin
        #cnt,bins,patches = ax.hist(distance_arcsec, theta_arcsec, fc='r', normed=1, alpha=0.75, label=r'Sample')
        cnt,bins,patches = ax.hist(r, r_bin, color='r', label=r'r Sample')
        print "cnt =", cnt
        print "bins =", bins
        
        r_midbin = []
        rayleigh = []
        rayleigh_ideal = []
        for i in range(len(bins)-1):
            r_midbin.append((bins[i]+bins[i+1])/2)
            rayleigh.append(r_midbin[i] * pylab.exp(-r_midbin[i]*r_midbin[i]/2))
            rayleigh_ideal.append(n * rayleigh[i] * binwidth)
        print "r_midbin = ", r_midbin
        print "rayleigh = ", rayleigh
        print "rayleigh_ideal = ", rayleigh_ideal
        print "sum(rayleigh) = ", sum(rayleigh)
        print "sum(rayleigh_ideal) = ", sum(rayleigh_ideal)
        
        int_rayleigh = 0.0
        for i in range(len(rayleigh)):
            int_rayleigh = int_rayleigh + n * binwidth * rayleigh[i] 
        print "int_rayleigh =", int_rayleigh

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
        ax.set_ylim(ymin=0, ymax=150)
        pylab.legend(numpoints=1)
        pylab.grid(True)
        fname = 'simdat_distr_r_' +str(xtrsrc_id[0]) + '.eps'
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


