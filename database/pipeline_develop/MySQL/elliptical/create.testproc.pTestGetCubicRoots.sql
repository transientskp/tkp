DROP PROCEDURE IF EXISTS pTestGetCubicRoots;

DELIMITER //

/** 
 * Find the roots for f(x), where
 * f(x) = ax^3 + bx^2 + cx + d
 *
 */
CREATE PROCEDURE pTestGetCubicRoots(IN ia DOUBLE
                              ,IN ib DOUBLE
                              ,IN ic DOUBLE
                              ,IN id DOUBLE
                              ,OUT oq DOUBLE
                              ,OUT oer DOUBLE
                              ,OUT oDelta DOUBLE
                              ,OUT os DOUBLE
                              ,OUT os_arg DOUBLE
                              ,OUT ot DOUBLE
                              ,OUT ot_arg DOUBLE
                              ,OUT orho DOUBLE
                              ,OUT otheta DOUBLE
                              ,OUT ox1 DOUBLE
                              ,OUT ox2 DOUBLE
                              ,OUT ox3 DOUBLE
                             ) 
BEGIN
  DECLARE nroots INT DEFAULT 0;

  DECLARE q, r, Delta DOUBLE;
  DECLARE s, s_arg, t, t_arg DOUBLE;
  DECLARE rho, theta DOUBLE;
  DECLARE x1, x2, x3 DOUBLE DEFAULT NULL;

  SET q = (3 * ia * ic - ib * ib) / (9 * ia * ia);
  SET oq = q;
  SET r = (9 * ia * ib * ic - 27 * ia * ia * id - 2 * ib * ib * ib) / (54 * ia * ia * ia);
  SET oer = r;
  SET Delta = q * q * q + r * r;
  SET oDelta = Delta;

  IF Delta >= 0 THEN
    SET s_arg = r + SQRT(Delta);
    SET os_arg = s_arg;
    IF s_arg < 0 THEN
      SET s = -POW(-s_arg, 1/3);
    ELSE 
      SET s = POW(s_arg, 1/3);
    END IF;
    SET os = s;
    SET t_arg = r - SQRT(Delta);
    SET ot_arg = t_arg;
    IF t_arg < 0 THEN
      SET t = -POW(-t_arg, 1/3);
    ELSE 
      SET t = POW(t_arg, 1/3);
    END IF;
    SET ot = t;
    SET x1 = s + t - (ib / (3 * ia));
  ELSE
    SET rho = SQRT(r * r - Delta);
    SET orho = rho;
    SET theta = ACOS(r / rho);
    SET otheta = theta;
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
//

DELIMITER ;

