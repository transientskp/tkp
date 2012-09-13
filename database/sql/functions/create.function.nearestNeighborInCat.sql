--DROP FUNCTION nearestNeighborInCat;

CREATE FUNCTION nearestNeighborInCat(ira DOUBLE
                                    ,idecl DOUBLE
                                    ,iname VARCHAR(50)
                                    ) RETURNS TABLE (catsrcid INT
                                                    ,catsrcname VARCHAR(120)
                                                    ,avg_f_int DOUBLE
                                                    ,distance_arcsec DOUBLE
                                                    )
BEGIN
  
  DECLARE itheta, ix, iy, iz DOUBLE;
  
  SET ix = COS(RADIANS(idecl)) * COS(RADIANS(ira));
  SET iy = COS(RADIANS(idecl)) * SIN(RADIANS(ira));
  SET iz = SIN(RADIANS(idecl));

  SET itheta = 1.0;

  /* We adopt a zoneheight of 1 degree */
  RETURN TABLE 
  (
    SELECT c1.id
          ,catsrcname
          ,avg_f_int
          ,3600 * DEGREES(2 * ASIN(SQRT( (ix - c1.x) * (ix - c1.x)
                                       + (iy - c1.y) * (iy - c1.y)
                                       + (iz - c1.z) * (iz - c1.z)
                                       ) / 2) 
                         ) AS distance_arcsec
      FROM catalogedsource c1
          ,catalog c0
     WHERE c1.catalog = c0.id
       AND c0.name = iname
       AND c1.x * ix + c1.y * iy + c1.z * iz > COS(RADIANS(itheta))
       AND c1.zone BETWEEN CAST(FLOOR(idecl - itheta) AS INTEGER)
                       AND CAST(FLOOR(idecl + itheta) AS INTEGER)
       AND c1.ra BETWEEN ira - alpha(itheta, idecl)
                     AND ira + alpha(itheta, idecl)
       AND c1.decl BETWEEN idecl - itheta
                       AND idecl + itheta
    ORDER BY distance_arcsec ASC
    LIMIT 1
  )
  ;

END
;

