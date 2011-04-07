DROP FUNCTION IF EXISTS getDistance_rad;


DELIMITER //

/**
 * This function calculates the distance between two point sources.
 * Input ra and decl are in degrees
 * Output distance is in rad.
 */
CREATE FUNCTION getDistance_rad(ira1 DOUBLE
                               ,idecl1 DOUBLE
                               ,ira2 DOUBLE
                               ,idecl2 DOUBLE
                               ) RETURNS DOUBLE 
DETERMINISTIC 
BEGIN

  DECLARE cosd, u1, u2, u3, v1, v2, v3 DOUBLE;

  SET cosd = COS(RADIANS(idecl1));
  SET u1 = cosd * COS(RADIANS(ira1));
  SET u2 = cosd * SIN(RADIANS(ira1));
  SET u3 = SIN(RADIANS(idecl1));

  SET cosd = COS(RADIANS(idecl2));
  SET v1 = cosd * COS(RADIANS(ira2));
  SET v2 = cosd * SIN(RADIANS(ira2));
  SET v3 = SIN(RADIANS(idecl2));

  /* this also works but we prefer to minimize calling functions 
  RETURN 2 * ASIN(getVectorLength(v1 - u1, v2 - u2, v3 - u3) / 2);
   */
  RETURN 2 * ASIN(SQRT(POW(v1 - u1, 2) + POW(v2 - u2, 2) + POW(v3 - u3, 2)) / 2);

END;
//

DELIMITER ;
