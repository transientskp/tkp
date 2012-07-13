--DROP FUNCTION neighborsInCats;

CREATE FUNCTION neighborsInCats(ira DOUBLE
                               ,idecl DOUBLE
                               ) RETURNS TABLE (id INT
                                               ,name VARCHAR(50)
                                               ,catsrcname VARCHAR(120)
                                               ,band SMALLINT
                                               ,freq_eff DOUBLE
                                               ,ra DOUBLE
                                               ,decl DOUBLE
                                               ,ra_err DOUBLE
                                               ,decl_err DOUBLE
                                               ,avg_f_peak DOUBLE
                                               ,avg_f_peak_err DOUBLE
                                               ,avg_f_int DOUBLE
                                               ,avg_f_int_err DOUBLE
                                               ,distance_arcsec DOUBLE
                                               )
BEGIN
  
  DECLARE izoneheight, itheta, ix, iy, iz DOUBLE;
  
  SET ix = COS(RADIANS(idecl)) * COS(RADIANS(ira));
  SET iy = COS(RADIANS(idecl)) * SIN(RADIANS(ira));
  SET iz = SIN(RADIANS(idecl));

  SET itheta = 1;

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
          ,3600 * DEGREES(2 * ASIN(SQRT(  (ix - c1.x) * (ix - c1.x)
                                        + (iy - c1.y) * (iy - c1.y)
                                        + (iz - c1.z) * (iz - c1.z)
                                       ) / 2) 
                     ) AS distance_arcsec
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

