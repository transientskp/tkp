--DROP FUNCTION spectralIndex;

/* For a given input position, the nearest vlss,wenss,and nvss
 * sources are checked. If no found nulls are returned,
 * otherwise the corresponding fluxes and spectral indices
 */
CREATE FUNCTION spectralIndex(ira double precision
                             ,idecl double precision
                             ) RETURNS TABLE (vlss_catsrcname VARCHAR(120)
                                             ,wenss_catsrcname VARCHAR(120)
                                             ,nvss_catsrcname VARCHAR(120)
                                             ,vlss_dist_arcsec double precision
                                             ,wenss_dist_arcsec double precision
                                             ,nvss_dist_arcsec double precision
                                             ,vlss_flux double precision
                                             ,wenss_flux double precision
                                             ,nvss_flux double precision
                                             ,alpha_vw double precision
                                             ,alpha_vn double precision
                                             ,alpha_wn double precision
                                             ) as $$

  DECLARE izoneheight double precision;
  declare itheta double precision;
  declare ix double precision;
  declare iy double precision;
  declare iz double precision;
  DECLARE ivlss_catsrcid int;
  declare iwenss_catsrcid int;
  declare invss_catsrcid INT;
  DECLARE ivlss_catsrcname varchar(120);
  declare iwenss_catsrcname, invss_catsrcname VARCHAR(120);
  DECLARE ivlss_freq double precision;
  declare iwenss_freq double precision;
  declare invss_freq double precision;
  DECLARE ivlss_flux double precision;
  declare iwenss_flux double precision;
  declare invss_flux double precision;
  DECLARE ivlss_dist_arcsec double precision;
  declare iwenss_dist_arcsec double precision;
  declare invss_dist_arcsec double precision;
  DECLARE ialpha_vw double precision;
  declare ialpha_vn double precision;
  declare ialpha_wn double precision;
  
BEGIN
  
  ix := COS(RADIANS(idecl)) * COS(RADIANS(ira));
  iy := COS(RADIANS(idecl)) * SIN(RADIANS(ira));
  iz := SIN(RADIANS(idecl));

  izoneheight := 1;
  itheta := 1;

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

  ialpha_vw := LOG10(ivlss_flux / iwenss_flux) / LOG10(iwenss_freq / ivlss_freq);
  ialpha_vn := LOG10(ivlss_flux / invss_flux) / LOG10(invss_freq / ivlss_freq);
  ialpha_wn := LOG10(iwenss_flux / invss_flux) / LOG10(invss_freq / iwenss_freq);
   
  RETURN query 
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
  ;
  
END
;
$$ language plpgsql;
