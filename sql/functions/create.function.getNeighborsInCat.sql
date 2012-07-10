--DROP FUNCTION getNeighborsInCat;

CREATE FUNCTION getNeighborsInCat(iname VARCHAR(50)
                                 ,itheta DOUBLE
                                 ,ixtrsrcid INT
                                 ) RETURNS TABLE (catsrcid INT
                                                 ,distance_arcsec DOUBLE
                                                 )
BEGIN
  
  RETURN TABLE 
  (
    SELECT c1.id
          ,3600 * DEGREES(2 * ASIN(SQRT((x1.x - c1.x) * (x1.x - c1.x)
                                       + (x1.y - c1.y) * (x1.y - c1.y)
                                       + (x1.z - c1.z) * (x1.z - c1.z)
                                       ) / 2) 
                         ) AS distance_arcsec
      FROM catalog c0
          ,catalogedsource c1
          ,extractedsource x1
     WHERE c0.name = iname
       AND c1.catalog = c0.id
       AND x1.id = ixtrsrcid
       AND c1.x * x1.x + c1.y * x1.y + c1.z * x1.z > COS(RADIANS(itheta))
       AND c1.zone BETWEEN CAST(FLOOR(x1.decl - itheta) AS INTEGER)
                       AND CAST(FLOOR(x1.decl + itheta) AS INTEGER)
       AND c1.ra BETWEEN x1.ra - alpha(itheta, x1.decl)
                     AND x1.ra + alpha(itheta, x1.decl)
       AND c1.decl BETWEEN x1.decl - itheta
                       AND x1.decl + itheta
    ORDER BY distance_arcsec
  )
  ;

END
;

