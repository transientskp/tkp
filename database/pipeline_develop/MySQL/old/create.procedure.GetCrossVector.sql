DROP PROCEDURE IF EXISTS GetCrossVector;

DELIMITER //

/*+--------------------------------------------------------------------+
 */
CREATE PROCEDURE GetCrossVector(IN a1 DOUBLE
                               ,IN a2 DOUBLE
                               ,IN a3 DOUBLE
                               ,IN b1 DOUBLE
                               ,IN b2 DOUBLE
                               ,IN b3 DOUBLE
                               ,OUT c1 DOUBLE
                               ,OUT c2 DOUBLE
                               ,OUT c3 DOUBLE
                               ) 

BEGIN
  
  SET c1 = a2 * b3 - a3 * b2;
  SET c2 = a3 * b1 - a1 * b3;
  SET c3 = a1 * b2 - a2 * b1;

END;
//

DELIMITER ;
