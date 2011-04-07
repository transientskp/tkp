DROP PROCEDURE IF EXISTS getCubicRootsAlt;

DELIMITER //

/** 
 * Find the roots for f(x), where
 * f(x) = x^3 + a2 x^2 + a1 x + a2
 *
 * f(x) = x^3 + 7 x^2 + 8 x - 16
 * should give 1;
 * 
 */
CREATE PROCEDURE getCubicRootsAlt(IN ia2 DOUBLE
                                 ,IN ia1 DOUBLE
                                 ,IN ia0 DOUBLE
                                 ,OUT oQ_denom DOUBLE
                                 ,OUT oQ_nom DOUBLE
                                 ,OUT oR_denom DOUBLE
                                 ,OUT oR_nom DOUBLE
                                 ,OUT oD_denom DOUBLE
                                 ,OUT oD_nom DOUBLE
                                 ,OUT oDelta DOUBLE
                                 ,OUT ox1 DOUBLE
                                 ,OUT ox2 DOUBLE
                                 ,OUT ox3 DOUBLE
                                 ) 
BEGIN
  DECLARE nroots INT DEFAULT 0;

  DECLARE q, r, Delta DOUBLE;
  DECLARE Q_denom, Q_nom, R_denom, R_nom, D_denom, D_nom DOUBLE;
  DECLARE s, s_arg, t, t_arg DOUBLE;
  DECLARE rho, theta DOUBLE;
  DECLARE x1, x2, x3 DOUBLE DEFAULT NULL;

  /*SET q = (3 * ia * ic - ib * ib) / (9 * ia * ia);
  SET r = (9 * ia * ib * ic - 27 * ia * ia * id - 2 * ib * ib * ib) / (54 * ia * ia * ia);
  SET Delta = q * q * q + r * r;*/
  SET q = (3 * ia1 - ia2 * ia2) / 9 ;
  SET r = (9 * ia2 * ia1 - 27 * ia0 - 2 * ia2 * ia2 * ia2) / 54;

  SET Q_denom = 3 * ia1 - ia2 * ia2;
  SET oQ_denom = Q_denom;
  SET Q_nom = 9;
  SET oQ_nom = Q_nom;
  SET R_denom = 9 * ia1 * ia2 - 27 * ia0 - 2 * ia2 * ia2 *ia2;
  SET oR_denom = R_denom;
  SET R_nom = 54;
  SET oR_nom = R_nom;
  SET D_denom =   Q_denom * Q_denom * Q_denom * R_nom * R_nom
                + Q_nom * Q_nom * Q_nom * R_denom * R_denom;
  SET oD_denom = D_denom;
  SET D_nom = Q_nom * Q_nom * Q_nom * R_nom * R_nom;
  SET oD_nom = D_nom;

  SET Delta = D_denom / D_nom; 

  IF D_denom >= 0 THEN
    SET s_arg = R_denom / R_nom + SQRT(D_denom / D_nom);
    IF s_arg < 0 THEN
      SET s = -POW(-s_arg, 1/3);
    ELSE 
      SET s = POW(s_arg, 1/3);
    END IF;
    SET t_arg = R_denom / R_nom - SQRT(D_denom / D_nom);
    IF t_arg < 0 THEN
      SET t = -POW(-t_arg, 1/3);
    ELSE 
      SET t = POW(t_arg, 1/3);
    END IF;
    SET x1 = s + t - ia2 / 3;
  ELSE
    SET rho = SQRT(r * r - Delta);
    SET theta = ACOS(r / rho);
    SET x1 = 2 * POW(rho, 1/3) * COS(theta/3) - (ia2 / 3);
    SET x2 = - POW(rho, 1/3) * COS(theta/3)
             - (ia2 / 3) 
             - SQRT(3) * POW(rho, 1/3) * SIN(theta/3);
    SET x3 = - POW(rho, 1/3) * COS(theta/3) 
             - (ia2 / 3) 
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

