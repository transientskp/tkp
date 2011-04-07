DROP FUNCTION IF EXISTS getVectorLength;

DELIMITER //

/**
 */
CREATE FUNCTION getVectorLength(v1 DOUBLE
                               ,v2 DOUBLE
                               ,v3 DOUBLE
                               ) RETURNS DOUBLE 
DETERMINISTIC 
BEGIN
  
  RETURN SQRT(POW(v1, 2) + POW(v2, 2) + POW(v3, 2));

END;
//

DELIMITER ;
