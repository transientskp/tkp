--DROP FUNCTION neighborsInCatsParams;

CREATE FUNCTION neighborsInCatsParams(ira DOUBLE
                                     ,idecl DOUBLE
                                     ,ira_err DOUBLE
                                     ,idecl_err DOUBLE
                                     ) RETURNS TABLE (id INT
                                                     ,name VARCHAR(50)
                                                     ,catsrcname VARCHAR(120)
                                                     ,band INT
                                                     ,freq_eff DOUBLE
                                                     ,ra DOUBLE
                                                     ,decl DOUBLE
                                                     ,ra_err DOUBLE
                                                     ,decl_err DOUBLE
                                                     ,avg_f_peak DOUBLE
                                                     ,avg_f_peak_err DOUBLE
                                                     ,avg_f_int DOUBLE
                                                     ,avg_f_int_err DOUBLE
                                                     ,assoc_distance_arcsec DOUBLE
                                                     ,assoc_r DOUBLE
                                                     ,assoc_logLR DOUBLE
                                                     )
BEGIN
  
  DECLARE itheta, ix, iy, iz DOUBLE;
  
  SET ix = COS(RADIANS(idecl)) * COS(RADIANS(ira));
  SET iy = COS(RADIANS(idecl)) * SIN(RADIANS(ira));
  SET iz = SIN(RADIANS(idecl));

  SET itheta = 1;

  /* The NVSS source density is 4.02439375E-06 */
  RETURN TABLE 
  (
    SELECT c1.id
          ,name
          ,catsrcname
          ,band
          ,freq_eff
          ,ra
          ,decl
          ,ra_err
          ,decl_err
          ,avg_f_peak
          ,avg_f_peak_err
          ,avg_f_int
          ,avg_f_int_err
          ,3600 * DEGREES(2 * ASIN(SQRT( (ix - c1.x) * (ix - c1.x)
                                       + (iy - c1.y) * (iy - c1.y)
                                       + (iz - c1.z) * (iz - c1.z)
                                       ) / 2) 
                         ) AS assoc_distance_arcsec
          ,3600 * SQRT(  (ira * COS(RADIANS(idecl)) - c1.ra * COS(RADIANS(c1.decl))) 
                       * (ira * COS(RADIANS(idecl)) - c1.ra * COS(RADIANS(c1.decl))) 
                         / (ira_err * ira_err + c1.ra_err * c1.ra_err)
                      + (idecl - c1.decl) * (idecl - c1.decl)  
                        / (idecl_err * idecl_err + c1.decl_err * c1.decl_err)
                      ) AS assoc_r
          ,LOG10(EXP(6480000 * (( (ira * COS(RADIANS(idecl)) - c1.ra * COS(RADIANS(c1.decl))) 
                      * (ira * COS(RADIANS(idecl)) - c1.ra * COS(RADIANS(c1.decl))) 
                        / (ira_err * ira_err + c1.ra_err * c1.ra_err)
                      + (idecl - c1.decl) * (idecl - c1.decl)  
                        / (idecl_err * idecl_err + c1.decl_err * c1.decl_err)
                      )
                     ) 
                    )
                /
                (2 * PI() * SQRT(ira_err * ira_err + c1.ra_err * c1.ra_err) 
                          * SQRT(idecl_err * idecl_err + c1.decl_err * c1.decl_err) 
                          * 4.02439375E-06)
                ) AS assoc_loglr
      FROM catalogedsource c1
          ,catalog c0
     WHERE c1.catalog = c0.id
       AND c1.zone BETWEEN CAST(FLOOR(idecl - itheta) AS INTEGER)
                       AND CAST(FLOOR(idecl + itheta) AS INTEGER)
       AND c1.ra BETWEEN ira - alpha(itheta, idecl)
                     AND ira + alpha(itheta, idecl)
       AND c1.decl BETWEEN idecl - itheta
                       AND idecl + itheta
       AND c1.x * ix + c1.y * iy + c1.z * iz > COS(RADIANS(itheta))
  )
  ;

END
;

