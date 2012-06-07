--DROP FUNCTION getNearestNeighborInCat;

CREATE FUNCTION getNearestNeighborInCat(icatname VARCHAR(50)
                                       ,ixtrsrcid INT
                                       ) RETURNS TABLE (catsrcid INT
                                                       ,distance_arcsec DOUBLE
                                                       )
BEGIN
  
  RETURN TABLE 
  (
    SELECT catsrcid
          ,distance_arcsec
      FROM getNeighborsInCat(icatname, 1, ixtrsrcid)
    LIMIT 1
  )
  ;

END
;

