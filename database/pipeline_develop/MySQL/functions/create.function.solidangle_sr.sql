DROP FUNCTION IF EXISTS solidangle_sr;

DELIMITER //

/**
 * This function computes the solid angle of and area subtended by
 * an ra_min and _max and a decl_min and _max.
 * INPUT in degrees, OUTPUT in arcsec^2.
 */
CREATE FUNCTION solidangle_sr(ra_min DOUBLE
                             ,ra_max DOUBLE
                             ,decl_min DOUBLE
                             ,decl_max DOUBLE
                             ) RETURNS DOUBLE 
DETERMINISTIC 

BEGIN

  RETURN PI() * (ra_max - ra_min) * (SIN(RADIANS(decl_max)) - SIN(RADIANS(decl_min))) / 180;

END;
//

DELIMITER ;
