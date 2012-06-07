--DROP FUNCTION spectralIndex;

/* For a given input position, the nearest vlss,wenss,and nvss
 * sources are checked. If no found nulls are returned,
 * otherwise the corresponding fluxes and spectral indices
 */
CREATE FUNCTION spectralIndex(ira DOUBLE
                             ,idecl DOUBLE
                             ) RETURNS TABLE (vlss_catsrcname VARCHAR(120)
                                             ,wenss_catsrcname VARCHAR(120)
                                             ,nvss_catsrcname VARCHAR(120)
                                             ,vlss_dist_arcsec DOUBLE
                                             ,wenss_dist_arcsec DOUBLE
                                             ,nvss_dist_arcsec DOUBLE
                                             ,vlss_flux DOUBLE
                                             ,wenss_flux DOUBLE
                                             ,nvss_flux DOUBLE
                                             ,alpha_vw DOUBLE
                                             ,alpha_vn DOUBLE
                                             ,alpha_wn DOUBLE
                                             )
BEGIN
  
  DECLARE izoneheight, itheta, ix, iy, iz DOUBLE;
  DECLARE ivlss_catsrcid, iwenss_catsrcid, invss_catsrcid INT;
  DECLARE ivlss_catsrcname, iwenss_catsrcname, invss_catsrcname VARCHAR(120);
  DECLARE ivlss_freq, iwenss_freq, invss_freq DOUBLE;
  DECLARE ivlss_flux, iwenss_flux, invss_flux DOUBLE;
  DECLARE ivlss_dist_arcsec, iwenss_dist_arcsec, invss_dist_arcsec DOUBLE;
  DECLARE ialpha_vw, ialpha_vn, ialpha_wn DOUBLE;
  
  SET ix = COS(RADIANS(idecl)) * COS(RADIANS(ira));
  SET iy = COS(RADIANS(idecl)) * SIN(RADIANS(ira));
  SET iz = SIN(RADIANS(idecl));

  SET izoneheight = 1;
  SET itheta = 1;

  SELECT catsrcid
        ,catsrcname
        ,freq_eff
        ,i_int_avg
        ,distance_arcsec
    INTO ivlss_catsrcid
        ,ivlss_catsrcname
        ,ivlss_freq
        ,ivlss_flux
        ,ivlss_dist_arcsec
    FROM (SELECT catsrcid
                ,catsrcname
                ,freq_eff
                ,i_int_avg
                ,3600 * DEGREES(2 * ASIN(SQRT((ix - x) * (ix - x)
                                             + (iy - y) * (iy - y)
                                             + (iz - z) * (iz - z)
                                             ) / 2) 
                               ) AS distance_arcsec
            FROM catalogedsources 
           WHERE cat_id = 4
             AND x * ix + y * iy + z * iz > COS(RADIANS(itheta))
             AND zone BETWEEN CAST(FLOOR((idecl - itheta) / izoneheight) AS INTEGER)
                          AND CAST(FLOOR((idecl + itheta) / izoneheight) AS INTEGER)
             AND ra BETWEEN ira - alpha(itheta, idecl)
                        AND ira + alpha(itheta, idecl)
             AND decl BETWEEN idecl - itheta
                          AND idecl + itheta
             AND 3600 * DEGREES(2 * ASIN(SQRT((ix - x) * (ix - x)
                                             + (iy - y) * (iy - y)
                                             + (iz - z) * (iz - z)
                                             ) / 2) 
                               ) = (SELECT MIN(3600 * DEGREES(2 * ASIN(SQRT((ix - x) * (ix - x)
                                                                   + (iy - y) * (iy - y)
                                                                   + (iz - z) * (iz - z)
                                                                   ) / 2) 
                                                     )
                                      )
                              FROM catalogedsources 
                             WHERE cat_id = 4
                               AND x * ix + y * iy + z * iz > COS(RADIANS(itheta))
                               AND zone BETWEEN CAST(FLOOR((idecl - itheta) / izoneheight) AS INTEGER)
                                            AND CAST(FLOOR((idecl + itheta) / izoneheight) AS INTEGER)
                               AND ra BETWEEN ira - alpha(itheta, idecl)
                                          AND ira + alpha(itheta, idecl)
                               AND decl BETWEEN idecl - itheta
                                            AND idecl + itheta
                                   ) 
        ) t0
  ;
  
  SELECT catsrcid
        ,catsrcname
        ,freq_eff
        ,i_int_avg
        ,distance_arcsec
    INTO iwenss_catsrcid
        ,iwenss_catsrcname
        ,iwenss_freq
        ,iwenss_flux
        ,iwenss_dist_arcsec
    FROM (SELECT catsrcid
                ,catsrcname
                ,freq_eff
                ,i_int_avg
                ,3600 * DEGREES(2 * ASIN(SQRT((ix - x) * (ix - x)
                                             + (iy - y) * (iy - y)
                                             + (iz - z) * (iz - z)
                                             ) / 2) 
                               ) AS distance_arcsec
            FROM catalogedsources 
           WHERE cat_id = 5
             AND x * ix + y * iy + z * iz > COS(RADIANS(itheta))
             AND zone BETWEEN CAST(FLOOR((idecl - itheta) / izoneheight) AS INTEGER)
                          AND CAST(FLOOR((idecl + itheta) / izoneheight) AS INTEGER)
             AND ra BETWEEN ira - alpha(itheta, idecl)
                        AND ira + alpha(itheta, idecl)
             AND decl BETWEEN idecl - itheta
                          AND idecl + itheta
             AND 3600 * DEGREES(2 * ASIN(SQRT((ix - x) * (ix - x)
                                             + (iy - y) * (iy - y)
                                             + (iz - z) * (iz - z)
                                             ) / 2) 
                               ) = (SELECT MIN(3600 * DEGREES(2 * ASIN(SQRT((ix - x) * (ix - x)
                                                                   + (iy - y) * (iy - y)
                                                                   + (iz - z) * (iz - z)
                                                                   ) / 2) 
                                                     )
                                      )
                              FROM catalogedsources 
                             WHERE cat_id = 5
                               AND x * ix + y * iy + z * iz > COS(RADIANS(itheta))
                               AND zone BETWEEN CAST(FLOOR((idecl - itheta) / izoneheight) AS INTEGER)
                                            AND CAST(FLOOR((idecl + itheta) / izoneheight) AS INTEGER)
                               AND ra BETWEEN ira - alpha(itheta, idecl)
                                          AND ira + alpha(itheta, idecl)
                               AND decl BETWEEN idecl - itheta
                                            AND idecl + itheta
                                   ) 
        ) t0
  ;
  
  SELECT catsrcid
        ,catsrcname
        ,freq_eff
        ,i_int_avg
        ,distance_arcsec
    INTO invss_catsrcid
        ,invss_catsrcname
        ,invss_freq
        ,invss_flux
        ,invss_dist_arcsec
    FROM (SELECT catsrcid
                ,catsrcname
                ,freq_eff
                ,i_int_avg
                ,3600 * DEGREES(2 * ASIN(SQRT((ix - x) * (ix - x)
                                             + (iy - y) * (iy - y)
                                             + (iz - z) * (iz - z)
                                             ) / 2) 
                               ) AS distance_arcsec
            FROM catalogedsources 
           WHERE cat_id = 3
             AND x * ix + y * iy + z * iz > COS(RADIANS(itheta))
             AND zone BETWEEN CAST(FLOOR((idecl - itheta) / izoneheight) AS INTEGER)
                          AND CAST(FLOOR((idecl + itheta) / izoneheight) AS INTEGER)
             AND ra BETWEEN ira - alpha(itheta, idecl)
                        AND ira + alpha(itheta, idecl)
             AND decl BETWEEN idecl - itheta
                          AND idecl + itheta
             AND 3600 * DEGREES(2 * ASIN(SQRT((ix - x) * (ix - x)
                                             + (iy - y) * (iy - y)
                                             + (iz - z) * (iz - z)
                                             ) / 2) 
                               ) = (SELECT MIN(3600 * DEGREES(2 * ASIN(SQRT((ix - x) * (ix - x)
                                                                   + (iy - y) * (iy - y)
                                                                   + (iz - z) * (iz - z)
                                                                   ) / 2) 
                                                     )
                                      )
                              FROM catalogedsources 
                             WHERE cat_id = 3
                               AND x * ix + y * iy + z * iz > COS(RADIANS(itheta))
                               AND zone BETWEEN CAST(FLOOR((idecl - itheta) / izoneheight) AS INTEGER)
                                            AND CAST(FLOOR((idecl + itheta) / izoneheight) AS INTEGER)
                               AND ra BETWEEN ira - alpha(itheta, idecl)
                                          AND ira + alpha(itheta, idecl)
                               AND decl BETWEEN idecl - itheta
                                            AND idecl + itheta
                                   ) 
        ) t0
  ;

  SET ialpha_vw = LOG10(ivlss_flux / iwenss_flux) / LOG10(iwenss_freq / ivlss_freq);
  SET ialpha_vn = LOG10(ivlss_flux / invss_flux) / LOG10(invss_freq / ivlss_freq);
  SET ialpha_wn = LOG10(iwenss_flux / invss_flux) / LOG10(invss_freq / iwenss_freq);
   
  RETURN TABLE 
  (
    SELECT ivlss_catsrcname 
          ,iwenss_catsrcname 
          ,invss_catsrcname 
          ,ivlss_dist_arcsec 
          ,iwenss_dist_arcsec 
          ,invss_dist_arcsec
          ,ivlss_flux 
          ,iwenss_flux 
          ,invss_flux 
          ,ialpha_vw 
          ,ialpha_vn 
          ,ialpha_wn 
  )
  ;
  
END
;

