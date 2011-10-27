# -*- coding: utf-8 -*-

#
# LOFAR Transients Key Project
#
import sys, pylab, string
import numpy as np
# Local tkp_lib functionality
import monetdb.sql as db
import logging
from tkp.config import config

DERUITER_R = config['source_association']['deruiter_radius']
print "DERUITER_R =",DERUITER_R

def expected_flux_in_fov(conn, ra_central, decl_central, fov_radius, assoc_theta, bbsfile, storespectraplots=False):
    """Search for VLSS, WENSS and NVSS sources that
    are in the given FoV. The FoV is set by its central position
    (ra_central, decl_central) out to a radius of fov_radius.
    The query looks for cross-matches around the sources, out
    to a radius of assoc_theta.

    All units are in degrees.

    The query returns all vlss sources (id) that are in the FoV.
    If so, the counterparts from other catalogues are returned as well 
    (also their ids).
    """
    
    skymodel = open(bbsfile, 'w')
    header = "# (Name, Type, Ra, Dec, I, Q, U, V, ReferenceFrequency='60e6',  SpectralIndex='[0.0]', MajorAxis, MinorAxis, Orientation) = format\n\n"
    skymodel.write(header)

    # This is dimensionless search radius that takes into account 
    # the ra and decl difference between two sources weighted by 
    # their positional errors.
    deRuiter_reduced = 3.717/3600.
    try:
        cursor = conn.cursor()
        query = """\
SELECT t0.v_catsrcid
      ,t0.catsrcname
      ,t1.wm_catsrcid
      ,t2.wp_catsrcid
      ,t3.n_catsrcid
      ,t0.v_flux
      ,t1.wm_flux
      ,t2.wp_flux
      ,t3.n_flux
      ,t0.v_flux_err
      ,t1.wm_flux_err
      ,t2.wp_flux_err
      ,t3.n_flux_err
      ,t1.wm_assoc_distance_arcsec
      ,t1.wm_assoc_r
      ,t2.wp_assoc_distance_arcsec
      ,t2.wp_assoc_r
      ,t3.n_assoc_distance_arcsec
      ,t3.n_assoc_r
      ,t0.pa
      ,t0.major
      ,t0.minor
      ,t0.ra
      ,t0.decl
  FROM (SELECT c1.catsrcid AS v_catsrcid
              ,c1.catsrcname
              ,c1.ra
              ,c1.decl
              ,c1.i_int_avg AS v_flux
              ,c1.i_int_avg_err AS v_flux_err
              ,c1.pa
              ,c1.major
              ,c1.minor
          FROM (SELECT catsrcid
                      ,catsrcname
                      ,ra
                      ,decl
                      ,pa
                      ,major
                      ,minor
                      ,i_int_avg
                      ,i_int_avg_err
                  FROM catalogedsources 
                 WHERE cat_id = 4
                   AND zone BETWEEN CAST(FLOOR(CAST(%s AS DOUBLE) - %s) AS INTEGER)
                                AND CAST(FLOOR(CAST(%s AS DOUBLE) + %s) AS INTEGER)
                   AND decl BETWEEN CAST(%s AS DOUBLE) - %s
                                AND CAST(%s AS DOUBLE) + %s
                   AND ra BETWEEN CAST(%s AS DOUBLE) - alpha(%s, %s)
                              AND CAST(%s AS DOUBLE) + alpha(%s, %s)
                   AND x * COS(RADIANS(%s)) * COS(RADIANS(%s))
                      + y * COS(RADIANS(%s)) * SIN(RADIANS(%s))
                      + z * SIN(RADIANS(%s)) > COS(RADIANS(%s))
               ) c1
       ) t0
       FULL OUTER JOIN 
       (SELECT c1.catsrcid AS v_catsrcid
              ,c2.catsrcid AS wm_catsrcid
              ,c2.i_int_avg AS wm_flux
              ,c2.i_int_avg_err AS wm_flux_err
              ,3600 * DEGREES(2 * ASIN(SQRT( (c1.x - c2.x) * (c1.x - c2.x)
                                           + (c1.y - c2.y) * (c1.y - c2.y)
                                           + (c1.z - c2.z) * (c1.z - c2.z)
                                           ) / 2)
                             ) AS wm_assoc_distance_arcsec
              ,SQRT(((c1.ra * COS(RADIANS(c1.decl)) - c2.ra * COS(RADIANS(c2.decl)))
                    * (c1.ra * COS(RADIANS(c1.decl)) - c2.ra * COS(RADIANS(c2.decl)))
                    / (c1.ra_err * c1.ra_err + c2.ra_err * c2.ra_err))
                    + ((c1.decl - c2.decl) * (c1.decl - c2.decl)
                    / (c1.decl_err * c1.decl_err + c2.decl_err * c2.decl_err))
                    ) AS wm_assoc_r
          FROM (SELECT catsrcid
                      ,ra
                      ,decl
                      ,ra_err
                      ,decl_err
                      ,x
                      ,y
                      ,z
                  FROM catalogedsources 
                 WHERE cat_id = 4
                   AND zone BETWEEN CAST(FLOOR(CAST(%s AS DOUBLE) - %s) AS INTEGER)
                                AND CAST(FLOOR(CAST(%s AS DOUBLE) + %s) AS INTEGER)
                   AND decl BETWEEN CAST(%s AS DOUBLE) - %s
                                AND CAST(%s AS DOUBLE) + %s
                   AND ra BETWEEN CAST(%s AS DOUBLE) - alpha(%s, %s)
                              AND CAST(%s AS DOUBLE) + alpha(%s, %s)
                   AND x * COS(RADIANS(%s)) * COS(RADIANS(%s))
                      + y * COS(RADIANS(%s)) * SIN(RADIANS(%s))
                      + z * SIN(RADIANS(%s)) > COS(RADIANS(%s))
               ) c1
              ,(SELECT catsrcid
                      ,ra
                      ,decl
                      ,ra_err
                      ,decl_err
                      ,x
                      ,y
                      ,z
                      ,i_int_avg
                      ,i_int_avg_err
                  FROM catalogedsources 
                 WHERE cat_id = 5
                   AND zone BETWEEN CAST(FLOOR(CAST(%s AS DOUBLE) - %s) AS INTEGER)
                                AND CAST(FLOOR(CAST(%s AS DOUBLE) + %s) AS INTEGER)
                   AND decl BETWEEN CAST(%s AS DOUBLE) - %s
                                AND CAST(%s AS DOUBLE) + %s
                   AND ra BETWEEN CAST(%s AS DOUBLE) - alpha(%s, %s)
                              AND CAST(%s AS DOUBLE) + alpha(%s, %s)
                   AND x * COS(RADIANS(%s)) * COS(RADIANS(%s))
                      + y * COS(RADIANS(%s)) * SIN(RADIANS(%s))
                      + z * SIN(RADIANS(%s)) > COS(RADIANS(%s))
               ) c2
         WHERE c1.x * c2.x + c1.y * c2.y + c1.z * c2.z > COS(RADIANS(%s))
           AND SQRT(((c1.ra * COS(RADIANS(c1.decl)) - c2.ra * COS(RADIANS(c2.decl)))
                    * (c1.ra * COS(RADIANS(c1.decl)) - c2.ra * COS(RADIANS(c2.decl)))
                    / (c1.ra_err * c1.ra_err + c2.ra_err * c2.ra_err))
                    + ((c1.decl - c2.decl) * (c1.decl - c2.decl)
                    / (c1.decl_err * c1.decl_err + c2.decl_err * c2.decl_err))) < %s
       ) t1
    ON t0.v_catsrcid = t1.v_catsrcid
       FULL OUTER JOIN 
       (SELECT c1.catsrcid AS v_catsrcid
              ,c2.catsrcid AS wp_catsrcid
              ,c2.i_int_avg AS wp_flux
              ,c2.i_int_avg_err AS wp_flux_err
              ,3600 * DEGREES(2 * ASIN(SQRT( (c1.x - c2.x) * (c1.x - c2.x)
                                           + (c1.y - c2.y) * (c1.y - c2.y)
                                           + (c1.z - c2.z) * (c1.z - c2.z)
                                           ) / 2)
                             ) AS wp_assoc_distance_arcsec
              ,SQRT(((c1.ra * COS(RADIANS(c1.decl)) - c2.ra * COS(RADIANS(c2.decl)))
                    * (c1.ra * COS(RADIANS(c1.decl)) - c2.ra * COS(RADIANS(c2.decl)))
                    / (c1.ra_err * c1.ra_err + c2.ra_err * c2.ra_err))
                    + ((c1.decl - c2.decl) * (c1.decl - c2.decl)
                    / (c1.decl_err * c1.decl_err + c2.decl_err * c2.decl_err))
                    ) AS wp_assoc_r
          FROM (SELECT catsrcid
                      ,ra
                      ,decl
                      ,ra_err
                      ,decl_err
                      ,x
                      ,y
                      ,z
                  FROM catalogedsources 
                 WHERE cat_id = 4
                   AND zone BETWEEN CAST(FLOOR(CAST(%s AS DOUBLE) - %s) AS INTEGER)
                                AND CAST(FLOOR(CAST(%s AS DOUBLE) + %s) AS INTEGER)
                   AND decl BETWEEN CAST(%s AS DOUBLE) - %s
                                AND CAST(%s AS DOUBLE) + %s
                   AND ra BETWEEN CAST(%s AS DOUBLE) - alpha(%s, %s)
                              AND CAST(%s AS DOUBLE) + alpha(%s, %s)
                   AND x * COS(RADIANS(%s)) * COS(RADIANS(%s))
                      + y * COS(RADIANS(%s)) * SIN(RADIANS(%s))
                      + z * SIN(RADIANS(%s)) > COS(RADIANS(%s))
               ) c1
              ,(SELECT catsrcid
                      ,ra
                      ,decl
                      ,ra_err
                      ,decl_err
                      ,x
                      ,y
                      ,z
                      ,i_int_avg
                      ,i_int_avg_err
                  FROM catalogedsources 
                 WHERE cat_id = 6
                   AND zone BETWEEN CAST(FLOOR(CAST(%s AS DOUBLE) - %s) AS INTEGER)
                                AND CAST(FLOOR(CAST(%s AS DOUBLE) + %s) AS INTEGER)
                   AND decl BETWEEN CAST(%s AS DOUBLE) - %s
                                AND CAST(%s AS DOUBLE) + %s
                   AND ra BETWEEN CAST(%s AS DOUBLE) - alpha(%s, %s)
                              AND CAST(%s AS DOUBLE) + alpha(%s, %s)
                   AND x * COS(RADIANS(%s)) * COS(RADIANS(%s))
                      + y * COS(RADIANS(%s)) * SIN(RADIANS(%s))
                      + z * SIN(RADIANS(%s)) > COS(RADIANS(%s))
               ) c2
         WHERE c1.x * c2.x + c1.y * c2.y + c1.z * c2.z > COS(RADIANS(%s))
           AND SQRT(((c1.ra * COS(RADIANS(c1.decl)) - c2.ra * COS(RADIANS(c2.decl)))
                    * (c1.ra * COS(RADIANS(c1.decl)) - c2.ra * COS(RADIANS(c2.decl)))
                    / (c1.ra_err * c1.ra_err + c2.ra_err * c2.ra_err))
                    + ((c1.decl - c2.decl) * (c1.decl - c2.decl)
                    / (c1.decl_err * c1.decl_err + c2.decl_err * c2.decl_err))) < %s
       ) t2
    ON t0.v_catsrcid = t2.v_catsrcid
       FULL OUTER JOIN 
       (SELECT c1.catsrcid AS v_catsrcid
              ,c2.catsrcid AS n_catsrcid
              ,c2.i_int_avg AS n_flux
              ,c2.i_int_avg_err AS n_flux_err
              ,3600 * DEGREES(2 * ASIN(SQRT( (c1.x - c2.x) * (c1.x - c2.x)
                                           + (c1.y - c2.y) * (c1.y - c2.y)
                                           + (c1.z - c2.z) * (c1.z - c2.z)
                                           ) / 2)
                             ) AS n_assoc_distance_arcsec
              ,SQRT(((c1.ra * COS(RADIANS(c1.decl)) - c2.ra * COS(RADIANS(c2.decl)))
                    * (c1.ra * COS(RADIANS(c1.decl)) - c2.ra * COS(RADIANS(c2.decl)))
                    / (c1.ra_err * c1.ra_err + c2.ra_err * c2.ra_err))
                    + ((c1.decl - c2.decl) * (c1.decl - c2.decl)
                    / (c1.decl_err * c1.decl_err + c2.decl_err * c2.decl_err))
                    ) AS n_assoc_r
          FROM (SELECT catsrcid
                      ,ra
                      ,decl
                      ,ra_err
                      ,decl_err
                      ,x
                      ,y
                      ,z
                  FROM catalogedsources 
                 WHERE cat_id = 4
                   AND zone BETWEEN CAST(FLOOR(CAST(%s AS DOUBLE) - %s) AS INTEGER)
                                AND CAST(FLOOR(CAST(%s AS DOUBLE) + %s) AS INTEGER)
                   AND decl BETWEEN CAST(%s AS DOUBLE) - %s
                                AND CAST(%s AS DOUBLE) + %s
                   AND ra BETWEEN CAST(%s AS DOUBLE) - alpha(%s, %s)
                              AND CAST(%s AS DOUBLE) + alpha(%s, %s)
                   AND x * COS(RADIANS(%s)) * COS(RADIANS(%s))
                      + y * COS(RADIANS(%s)) * SIN(RADIANS(%s))
                      + z * SIN(RADIANS(%s)) > COS(RADIANS(%s))
               ) c1
              ,(SELECT catsrcid
                      ,ra
                      ,decl
                      ,ra_err
                      ,decl_err
                      ,x
                      ,y
                      ,z
                      ,i_int_avg
                      ,i_int_avg_err
                  FROM catalogedsources 
                 WHERE cat_id = 3
                   AND zone BETWEEN CAST(FLOOR(CAST(%s AS DOUBLE) - %s) AS INTEGER)
                                AND CAST(FLOOR(CAST(%s AS DOUBLE) + %s) AS INTEGER)
                   AND decl BETWEEN CAST(%s AS DOUBLE) - %s
                                AND CAST(%s AS DOUBLE) + %s
                   AND ra BETWEEN CAST(%s AS DOUBLE) - alpha(%s, %s)
                              AND CAST(%s AS DOUBLE) + alpha(%s, %s)
                   AND x * COS(RADIANS(%s)) * COS(RADIANS(%s))
                      + y * COS(RADIANS(%s)) * SIN(RADIANS(%s))
                      + z * SIN(RADIANS(%s)) > COS(RADIANS(%s))
               ) c2
         WHERE c1.x * c2.x + c1.y * c2.y + c1.z * c2.z > COS(RADIANS(%s))
           AND SQRT(((c1.ra * COS(RADIANS(c1.decl)) - c2.ra * COS(RADIANS(c2.decl)))
                    * (c1.ra * COS(RADIANS(c1.decl)) - c2.ra * COS(RADIANS(c2.decl)))
                    / (c1.ra_err * c1.ra_err + c2.ra_err * c2.ra_err))
                    + ((c1.decl - c2.decl) * (c1.decl - c2.decl)
                    / (c1.decl_err * c1.decl_err + c2.decl_err * c2.decl_err))) < %s
       ) t3
    ON t0.v_catsrcid = t3.v_catsrcid
        """
        cursor.execute(query, (
                     decl_central, fov_radius, decl_central, fov_radius, decl_central, fov_radius, decl_central, fov_radius,
                     ra_central, fov_radius, decl_central, ra_central, fov_radius, decl_central, 
                     decl_central, ra_central, decl_central, ra_central, decl_central, fov_radius,
                     decl_central, fov_radius, decl_central, fov_radius, decl_central, fov_radius, decl_central, fov_radius,
                     ra_central, fov_radius, decl_central,ra_central, fov_radius, decl_central, 
                     decl_central, ra_central, decl_central, ra_central, decl_central, fov_radius,
                     decl_central, fov_radius, decl_central, fov_radius, decl_central, fov_radius, decl_central, fov_radius,
                     ra_central, fov_radius, decl_central,ra_central, fov_radius, decl_central, 
                     decl_central, ra_central, decl_central, ra_central, decl_central, fov_radius,
                     assoc_theta, deRuiter_reduced,
                     decl_central, fov_radius, decl_central, fov_radius, decl_central, fov_radius, decl_central, fov_radius,
                     ra_central, fov_radius, decl_central,ra_central, fov_radius, decl_central, 
                     decl_central, ra_central, decl_central, ra_central, decl_central, fov_radius,
                     decl_central, fov_radius, decl_central, fov_radius, decl_central, fov_radius, decl_central, fov_radius,
                     ra_central, fov_radius, decl_central,ra_central, fov_radius, decl_central, 
                     decl_central, ra_central, decl_central, ra_central, decl_central, fov_radius,
                     assoc_theta, deRuiter_reduced,
                     decl_central, fov_radius, decl_central, fov_radius, decl_central, fov_radius, decl_central, fov_radius,
                     ra_central, fov_radius, decl_central,ra_central, fov_radius, decl_central, 
                     decl_central, ra_central, decl_central, ra_central, decl_central, fov_radius,
                     decl_central, fov_radius, decl_central, fov_radius, decl_central, fov_radius, decl_central, fov_radius,
                     ra_central, fov_radius, decl_central,ra_central, fov_radius, decl_central, 
                     decl_central, ra_central, decl_central, ra_central, decl_central, fov_radius,
                     assoc_theta, deRuiter_reduced
                              ))
        results = zip(*cursor.fetchall())
        if len(results) != 0:
            vlss_catsrcid = results[0]
            vlss_name = results[1]
            wenssm_catsrcid = results[2]
            wenssp_catsrcid = results[3]
            nvss_catsrcid = results[4]
            v_flux = results[5]
            wm_flux = results[6]
            wp_flux = results[7]
            n_flux = results[8]
            v_flux_err = results[9]
            wm_flux_err = results[10]
            wp_flux_err = results[11]
            n_flux_err = results[12]
            wm_assoc_distance_arcsec = results[13]
            wm_assoc_r = results[14]
            wp_assoc_distance_arcsec = results[15]
            wp_assoc_r = results[16]
            n_assoc_distance_arcsec = results[17]
            n_assoc_r = results[18]
            pa = results[19]
            major = results[20]
            minor = results[21]
            ra = results[22]
            decl = results[23]
        spectrumfiles = []
        for i in range(len(vlss_catsrcid)):
            print "\ni = ", i
            bbsrow = ""
            # Here we check the cases for the degree of the polynomial spectral index fit
            print vlss_catsrcid[i], wenssm_catsrcid[i], wenssp_catsrcid[i], nvss_catsrcid[i]
            #print "VLSS",vlss_name[i]
            bbsrow += vlss_name[i] + ", "
            # According to Jess, only sources that have values for all
            # three are considered as GAUSSIAN
            if pa[i] is not None and major[i] is not None and minor[i] is not None:
                #print "Gaussian:", pa[i], major[i], minor[i]
                bbsrow += "GAUSSIAN, "
            else:
                #print "POINT"
                bbsrow += "POINT, "
            #print "ra = ", ra[i], "; decl = ", decl[i]
            #print "BBS ra = ", ra2bbshms(ra[i]), "; BBS decl = ", decl2bbsdms(decl[i])
            bbsrow += ra2bbshms(ra[i]) + ", " + decl2bbsdms(decl[i]) + ", "
            # Stokes I id default, so filed is empty
            bbsrow += ", "
            lognu = []
            logflux = []
            lognu.append(np.log10(74.0/60.0))
            logflux.append(np.log10(v_flux[i]))
            if wenssm_catsrcid[i] is not None:
                lognu.append(np.log10(325.0/60.0))
                logflux.append(np.log10(wm_flux[i]))
            if wenssp_catsrcid[i] is not None:
                lognu.append(np.log10(352.0/60.0))
                logflux.append(np.log10(wp_flux[i]))
            if nvss_catsrcid[i] is not None:
                lognu.append(np.log10(1400.0/60.0))
                logflux.append(np.log10(n_flux[i]))
            f = ""
            for j in range(len(logflux)):
                f += str(10**logflux[j]) + "; "
            print f
            #print "len(lognu) = ",len(lognu), "nvss_catsrcid[",i,"] =", nvss_catsrcid[i]
            # Here we write the expected flux values at 60 MHz, and the fitted spectral index and
            # and curvature term
            if len(lognu) == 1:
                #print "Exp. flux:", 10**(np.log10(v_flux[i]) + 0.7 * np.log10(74.0/60.0))
                #print "Default -0.7"
                bbsrow += str(round(10**(np.log10(v_flux[i]) + 0.7 * np.log10(74.0/60.0)), 2)) + ", , , , , "
                bbsrow += "[-0.7]"
            elif len(lognu) == 2 or (len(lognu) == 3 and nvss_catsrcid[i] is None):
                #print "Do a 1-degree polynomial fit"
                # p has form : p(x) = p[0] + p[1]*x
                p = np.poly1d(np.polyfit(np.array(lognu), np.array(logflux), 1))
                #print p
                if storespectraplots:
                    spectrumfile = plotSpectrum(np.array(lognu), np.array(logflux), p, "spectrum_%s.eps" % vlss_name[i])
                    spectrumfiles.append(spectrumfile)
                # Default reference frequency is reported, so we leave it empty here;
                # Catalogues just report on Stokes I, so others are empty.
                bbsrow += str(round(10**p[0], 4)) + ", , , , , "
                bbsrow += "[" + str(round(p[1], 4)) + "]"
            elif (len(lognu) == 3 and nvss_catsrcid[i] is not None) or len(lognu) == 4:
                #print "Do a 2-degree polynomial fit"
                # p has form : p(x) = p[0] + p[1]*x + p[2]*x**2
                p = np.poly1d(np.polyfit(np.array(lognu), np.array(logflux), 2))
                #print p
                if storespectraplots:
                    spectrumfile = plotSpectrum(np.array(lognu), np.array(logflux), p, "spectrum_%s.eps" % vlss_name[i])
                    spectrumfiles.append(spectrumfile)
                # Default reference frequency is reported, so we leave it empty here
                bbsrow += str(round(10**p[0], 4)) + ", , , , , "
                bbsrow += "[" + str(round(p[1],4)) + ", " + str(round(p[2],4)) + "]"
            if pa[i] is not None and major[i] is not None and minor[i] is not None:
                # Gaussian source:
                bbsrow += ", " + str(round(major[i], 2)) + ", " + str(round(minor[i], 2)) + ", " + str(round(pa[i], 2))
            #print bbsrow
            skymodel.write(bbsrow + '\n')
        
        if storespectraplots:
            print "Spectra available in:", spectrumfiles

        skymodel.close()
        print "Sky model stored in source table:", bbsfile
    
    except db.Error, e:
        logging.warn("Failed on query nr %s; for reason %s" % (query, e))
        raise
    finally:
        cursor.close()

def plotSpectrum(x, y, p, f):
    expflux = "Exp. flux: " + str(round(10**p(0),3)) + " Jy"
    fig = pylab.figure()
    ax = fig.add_subplot(111)
    for i in range(len(ax.get_xticklabels())):
        ax.get_xticklabels()[i].set_size('x-large')
    for i in range(len(ax.get_yticklabels())):
        ax.get_yticklabels()[i].set_size('x-large')
    ax.set_xlabel(r'$\log \nu/\nu_0$', size='x-large')
    ax.set_ylabel('$\log S$', size='x-large')
    # Roughly between log10(30/60) and log10(1500/60)
    xp = np.linspace(-0.3, 1.5, 100)
    ax.plot(x, y, 'o', label='cat fluxes')
    ax.plot(0.0, p(0), 'o', color='k', label=expflux )
    ax.plot(xp, p(xp), linestyle='--', linewidth=2, label='fit')
    pylab.legend(numpoints=1, loc='best')
    pylab.grid(True)
    pylab.savefig(f, dpi=600)
    return f


def decl2bbsdms(d):
    """Based on function deg2dec Written by Enno Middelberg 2001
    http://www.atnf.csiro.au/people/Enno.Middelberg/python/python.html
    """
    deg = float(d)
    sign = "+"
    
    # test whether the input numbers are sane:
    
    # if negative, store "-" in sign and continue calulation
    # with positive value
    
    if deg < 0:
        sign = "-"
        deg = deg * (-1)
    
    #if deg > 180:
    #    logging.warn("%s: inputs may not exceed 180!" % deg)
    #    raise
    
    #if deg > 90:
    #    print `deg`+" exceeds 90, will convert it to negative dec\n"
    #    deg=deg-90
    #    sign="-"
    
    if deg < -90 or deg > 90:
        logging.warn("%s: inputs may not exceed 90 degrees!" % deg)
    
    hh = int(deg)
    mm = int((deg - int(deg)) * 60)
    ss = '%10.8f' % (((deg - int(deg)) * 60 - mm) * 60)
    
    #print '\t'+sign+string.zfill(`hh`,2)+':'+string.zfill(`mm`,2)+':'+'%10.8f' % ss
    #print '\t'+sign+string.zfill(`hh`,2)+' '+string.zfill(`mm`,2)+' '+'%10.8f' % ss
    #print '\t'+sign+string.zfill(`hh`,2)+'h'+string.zfill(`mm`,2)+'m'+'%10.8fs\n' % ss
    return sign + string.zfill(`hh`, 2) + '.' + string.zfill(`mm`, 2) + '.' + string.zfill(ss, 11)

def ra2bbshms(a):
    deg=float(a)
    
    # test whether the input numbers are sane:
    
    if deg < 0 or deg > 360:
        logging.warn("%s: inputs may not exceed 90 degrees!" % deg)
    
    hh = int(deg / 15)
    mm = int((deg - 15 * hh) * 4)
    ss = '%10.8f' % ((4 * deg - 60 * hh - mm) * 60)
    
    #print '\t'+string.zfill(`hh`,2)+':'+string.zfill(`mm`,2)+':'+'%10.8f' % ss
    #print '\t'+string.zfill(`hh`,2)+' '+string.zfill(`mm`,2)+' '+'%10.8f' % ss
    #print '\t'+string.zfill(`hh`,2)+'h'+string.zfill(`mm`,2)+'m'+'%10.8fs\n' % ss
    return string.zfill(`hh`, 2) + ':' + string.zfill(`mm`, 2) + ':' + string.zfill(ss, 11)

