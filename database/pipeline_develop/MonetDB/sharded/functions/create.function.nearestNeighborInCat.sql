--DROP FUNCTION nearestNeighborInCat;

CREATE FUNCTION nearestNeighborInCat(ira DOUBLE
                                     ,idecl DOUBLE
                                     ,icatname VARCHAR(50)
                                     ) RETURNS TABLE (catsrcid INT
                                                     ,catsrcname VARCHAR(120)
                                                     ,i_int DOUBLE
                                                     ,distance_arcsec DOUBLE
                                                     )
BEGIN
  
  DECLARE izoneheight, itheta, ix, iy, iz DOUBLE;
  
  SET ix = COS(RADIANS(idecl)) * COS(RADIANS(ira));
  SET iy = COS(RADIANS(idecl)) * SIN(RADIANS(ira));
  SET iz = SIN(RADIANS(idecl));

  /* TODO: 
   * retrieve zoneheight from table ->
   * meaning add a columns to the table
  SELECT zoneheight
    INTO izoneheight
    FROM zoneheight
  ;*/
  SET izoneheight = 1.0;
  SET itheta = 1.0;

  RETURN TABLE 
  (
    SELECT catsrcid
          ,catsrcname
          ,i_int_avg
          ,3600 * DEGREES(2 * ASIN(SQRT((ix - c1.x) * (ix - c1.x)
                                       + (iy - c1.y) * (iy - c1.y)
                                       + (iz - c1.z) * (iz - c1.z)
                                       ) / 2) 
                         ) AS distance_arcsec
      FROM catalogedsources c1
          ,catalogs c0
     WHERE c1.cat_id = c0.catid
       AND c0.catname = icatname
       AND c1.x * ix + c1.y * iy + c1.z * iz > COS(RADIANS(itheta))
       AND c1.zone BETWEEN CAST(FLOOR((idecl - itheta) / izoneheight) AS INTEGER)
                       AND CAST(FLOOR((idecl + itheta) / izoneheight) AS INTEGER)
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

