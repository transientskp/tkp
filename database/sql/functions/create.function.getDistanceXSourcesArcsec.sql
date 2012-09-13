--DROP FUNCTION getDistanceXSourcesArcsec;

/**
 * This function calculates the distance between two point sources.
 * Input ra and decl are in degrees
 * Output distance is in arcsec.
 */
CREATE FUNCTION getDistanceXSourcesArcsec(id1 INT
                                         ,id2 INT
                                         ) RETURNS DOUBLE
BEGIN

  DECLARE dist DOUBLE;

  SELECT 3600 * DEGREES(2 * ASIN(SQRT( (x1.x - x2.x) * (x1.x - x2.x)  
                                     + (x1.y - x2.y) * (x1.y - x2.y)  
                                     + (x1.z - x2.z) * (x1.z - x2.z)  
                                     ) / 2) ) AS distance_arcsec
    INTO dist
    FROM extractedsource x1
        ,extractedsource x2
   WHERE x1.id = id1     
     AND x2.id = id2 
  ;

  RETURN dist;
  
END;
