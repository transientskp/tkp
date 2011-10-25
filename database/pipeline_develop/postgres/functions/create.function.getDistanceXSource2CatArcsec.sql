--DROP FUNCTION getDistanceXSource2CatArcsec;

/**
 * This function calculates the distance between two point sources.
 * Input ra and decl are in degrees
 * Output distance is in arcsec.
 */
CREATE FUNCTION getDistanceXSource2CatArcsec(ixtrsrcid INT
                                            ,icatsrcid INT
                                            ) RETURNS double precision as $$
  DECLARE dist double precision;

BEGIN
  SELECT 3600.0 * degrees(2 * ASIN(SQRT((x1.x - c1.x) * (x1.x - c1.x.y - c1.y) * (x1.y - c1.y)  
                                     + (x1.z - c1.z) * (x1.z - c1.z)  
                                     ) / 2) ) AS distance_arcsec
    INTO dist
    FROM extractedsources x1
        ,catalogedsources c1
   WHERE x1.xtrsrcid = ixtrsrcid     
     AND c1.catsrcid = icatsrcid 
  ;

  RETURN dist;
  
END;
$$ language plpgsql;
