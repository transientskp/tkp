USE pipeline;

DROP PROCEDURE IF EXISTS getRootsCubic;
DROP FUNCTION IF EXISTS testIntersect;

DELIMITER //

/** 
 * Find the roots for f(x), where
 * f(x) = ax^3 + bx^2 + cx + d
 *
 */
CREATE PROCEDURE getRootsCubic(IN ia DOUBLE
                              ,IN ib DOUBLE
                              ,IN ic DOUBLE
                              ,IN id DOUBLE
                              ,OUT ox1 DOUBLE
                              ,OUT ox2 DOUBLE
                              ,OUT ox3 DOUBLE
                             ) 
BEGIN
  DECLARE nroots INT DEFAULT 0;

  DECLARE q DOUBLE DEFAULT NULL;
  DECLARE r DOUBLE DEFAULT NULL;
  DECLARE Delta DOUBLE DEFAULT NULL; /* the disrciminant */
  DECLARE s DOUBLE DEFAULT NULL;
  DECLARE s_arg DOUBLE DEFAULT NULL;
  DECLARE t DOUBLE DEFAULT NULL;
  DECLARE t_arg DOUBLE DEFAULT NULL;
  DECLARE rho DOUBLE DEFAULT NULL;
  DECLARE theta DOUBLE DEFAULT NULL;
  DECLARE x1 DOUBLE DEFAULT NULL;
  DECLARE x2 DOUBLE DEFAULT NULL;
  DECLARE x3 DOUBLE DEFAULT NULL;

  SET q = (3 * ia * ic - ib * ib) / (9 * ia * ia);
  SET r = (9 * ia * ib * ic - 27 * ia * ia * id - 2 * ib * ib * ib) / (54 * ia * ia * ia);
  SET Delta = q * q * q + r * r;

  IF Delta >= 0 THEN
    SET s_arg = r + SQRT(Delta);
    IF s_arg < 0 THEN
      SET s = -POW(-s_arg, 1/3);
    ELSE 
      SET s = POW(s_arg, 1/3);
    END IF;
    SET t_arg = r - SQRT(Delta);
    IF t_arg < 0 THEN
      SET t = -POW(-t_arg, 1/3);
    ELSE 
      SET t = POW(t_arg, 1/3);
    END IF;
    SET x1 = s + t - (ib / (3 * ia));
  ELSE
    SET rho = SQRT(r * r - Delta);
    SET theta = ACOS(r / rho);
    SET x1 = 2 * POW(rho, 1/3) * COS(theta/3) - (ib / (3 * ia));
    SET x2 = - POW(rho, 1/3) * COS(theta/3)
             - (ib / (3 * ia)) 
             - SQRT(3) * POW(rho, 1/3) * SIN(theta/3);
    SET x3 = - POW(rho, 1/3) * COS(theta/3) 
             - (ib / (3 * ia)) 
             + SQRT(3) * POW(rho, 1/3) * SIN(theta/3);

  END IF;

  SET ox1 = x1;
  SET ox2 = x2;
  SET ox3 = x3;
  /*SET ox2 = r + SQRT(Delta);
  SET ox3 = r - SQRT(Delta);*/

END;



CREATE FUNCTION testIntersect(ira1 DOUBLE
                             ,idec1 DOUBLE
                             ,ia1 DOUBLE
                             ,ib1 DOUBLE
                             ,iphi1 DOUBLE
                             ,ira2 DOUBLE
                             ,idec2 DOUBLE
                             ,ia2 DOUBLE
                             ,ib2 DOUBLE
                             ,iphi2 DOUBLE
                             ) RETURNS BOOLEAN
DETERMINISTIC
BEGIN
  DECLARE intersect BOOLEAN DEFAULT FALSE;
  DECLARE e1_a_11 DOUBLE DEFAULT NULL;
  DECLARE e1_b_1 DOUBLE DEFAULT NULL;
  DECLARE e1_c DOUBLE DEFAULT NULL;
  DECLARE e1_a_01 DOUBLE DEFAULT NULL;
  DECLARE e1_b_0 DOUBLE DEFAULT NULL;
  DECLARE e1_a_00 DOUBLE DEFAULT NULL;

  /**
   * First, we rewrite the two ellipses as a quartic equation
   */
  SET e1_a_11 = 1 / (ib1 * ib1);
  SET e1_b_1 = 0;
  SET e1_c = -1;
  SET e1_a_01 = 0;
  SET e1_b_0 = 0;
  SET e1_a_00 = 1 / (ia1 * ia1);
  


  /**
   * Second, we check the roots of the derivative of the quartic
   */

  /**
   * Third, if all the roots are positive, there are no real roots,
   * and consequently no intersection
   */

  RETURN intersect;

END;
//

DELIMITER ;

