DROP FUNCTION IF EXISTS getValue;

DELIMITER //

/**
 * This function computes the ra expansion for a given theta at 
 * a given declination.
 * theta and decl are both in degrees.
 */
CREATE FUNCTION getValue(col1 DOUBLE, col2 DOUBLE) RETURNS DOUBLE 
DETERMINISTIC 
BEGIN
    RETURN col1 + col2 ; 
END;
//

DELIMITER ;
