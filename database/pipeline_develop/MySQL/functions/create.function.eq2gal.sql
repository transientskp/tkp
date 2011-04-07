DROP FUNCTION IF EXISTS eq2gall;

DELIMITER //

/**
 * This function converts ra in HHMMSS format into degrees.
 * The input format must be delimited by one char:
 * 03 45 23.2 is ok as well as
 * 03:45:23.22 is ok as well as
 */
CREATE FUNCTION eq2gall(ira DOUBLE
                       ,idecl DOUBLE
                       ) RETURNS DOUBLE
DETERMINISTIC
BEGIN

  /* See Gal Astr, Binney*/
  DECLARE ra_GP DOUBLE DEFAULT 192.85948;
  DECLARE decl_GP DOUBLE DEFAULT 27.12825;
  DECLARE l_CP DOUBLE DEFAULT 123.932;

  SET sinb = SIN(RADIANS(decl_GP)) * SIN(RADIANS(idecl)) 
             + COS(RADIANS(decl_GP)) * COS(RADIANS(idecl)) * COS(RADIANS(ira - ra_GP));


END;
//

DELIMITER ;
