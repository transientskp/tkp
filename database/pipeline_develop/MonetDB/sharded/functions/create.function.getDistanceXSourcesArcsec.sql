--DROP FUNCTION getDistanceXSourcesArcsec;

/**
 * This function calculates the distance between two point sources.
 * Input ra and decl are in degrees
 * Output distance is in arcsec.
 */
CREATE FUNCTION getDistanceXSourcesArcsec(ixtrsrcid1 INT
                                         ,ixtrsrcid2 INT
                                         ) RETURNS DOUBLE
BEGIN

  DECLARE dist DOUBLE;

  SELECT 3600 * DEGREES(2 * ASIN(SQRT((x1.x - x2.x) * (x1.x - x2.x)  
                                     + (x1.y - x2.y) * (x1.y - x2.y)  
                                     + (x1.z - x2.z) * (x1.z - x2.z)  
                                     ) / 2) ) AS distance_arcsec
    INTO dist
    FROM extractedsources x1
        ,extractedsources x2
   WHERE x1.xtrsrcid = ixtrsrcid1     
     AND x2.xtrsrcid = ixtrsrcid2 
  ;

  RETURN dist;
  
END;
