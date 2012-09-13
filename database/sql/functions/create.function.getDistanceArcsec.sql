--DROP FUNCTION getDistanceArcsec;

/**
 * This function calculates the distance on the sky 
 * between two point sources.
 * Input ra and decl are in degrees, 
 * and utput distance is in arcsec.
 */
CREATE FUNCTION getDistanceArcsec(ira1 DOUBLE
                                 ,idecl1 DOUBLE
                                 ,ira2 DOUBLE
                                 ,idecl2 DOUBLE
                                 ) RETURNS DOUBLE 
BEGIN

  RETURN 3600 * DEGREES(2 * ASIN(SQRT(   (COS(RADIANS(idecl1)) * COS(RADIANS(ira1)) - COS(RADIANS(idecl2)) * COS(RADIANS(ira2))) 
                                       * (COS(RADIANS(idecl1)) * COS(RADIANS(ira1)) - COS(RADIANS(idecl2)) * COS(RADIANS(ira2))) 
                                     +   (COS(RADIANS(idecl1)) * SIN(RADIANS(ira1)) - COS(RADIANS(idecl2)) * SIN(RADIANS(ira2))) 
                                       * (COS(RADIANS(idecl1)) * SIN(RADIANS(ira1)) - COS(RADIANS(idecl2)) * SIN(RADIANS(ira2))) 
                                     +   (SIN(RADIANS(idecl1)) - SIN(RADIANS(idecl2))) 
                                       * (SIN(RADIANS(idecl1)) - SIN(RADIANS(idecl2)))
                                     ) 
                                / 2
                                )
                       );
  
END;
