--DROP FUNCTION getDistanceXSource2CatArcsec;

/**
 * This function calculates the distance between two point sources.
 * Input ra and decl are in degrees
 * Output distance is in arcsec.
 */
CREATE FUNCTION getDistanceXSource2CatArcsec(ixtrsrcid INT
                                            ,icatsrcid INT
                                            ) RETURNS DOUBLE
BEGIN

  DECLARE dist DOUBLE;

  SELECT 3600 * DEGREES(2 * ASIN(SQRT( (x1.x - c1.x) * (x1.x - c1.x)  
                                     + (x1.y - c1.y) * (x1.y - c1.y)  
                                     + (x1.z - c1.z) * (x1.z - c1.z)  
                                     ) / 2) ) AS distance_arcsec
    INTO dist
    FROM extractedsource x1
        ,catalogedsource c1
   WHERE x1.id = ixtrsrcid     
     AND c1.id = icatsrcid 
  ;

  RETURN dist;
  
END;
