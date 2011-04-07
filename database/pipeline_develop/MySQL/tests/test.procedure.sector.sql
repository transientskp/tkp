DROP PROCEDURE IF EXISTS testAreaEllSector;
/**
 * Test for area of elliptical sector
 */

DELIMITER //

CREATE PROCEDURE testAreaEllSector()

BEGIN
  DECLARE theta_0 DOUBLE;
  DECLARE theta_1 DOUBLE;
  DECLARE area DOUBLE;
  DECLARE sector DOUBLE;
  DECLARE e_a DOUBLE DEFAULT 4/3600;
  DECLARE e_b DOUBLE DEFAULT 3/3600;

  SET theta_0 = 20;
  SET theta_1 = 70;




END;
//

DELIMITER ;

