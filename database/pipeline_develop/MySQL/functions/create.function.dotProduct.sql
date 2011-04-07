DROP FUNCTION IF EXISTS dotProduct;

DELIMITER //

/**
 */
CREATE FUNCTION dotProduct(a1 DOUBLE
                          ,a2 DOUBLE
                          ,a3 DOUBLE
                          ,b1 DOUBLE
                          ,b2 DOUBLE
                          ,b3 DOUBLE
                          ) RETURNS DOUBLE 
DETERMINISTIC 
BEGIN
  
  RETURN a1 * b1 + a2 * b2 + a3 * b3;

END;
//

DELIMITER ;
