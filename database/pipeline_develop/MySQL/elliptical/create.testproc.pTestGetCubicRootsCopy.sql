DROP PROCEDURE IF EXISTS pTestGetCubicRootsCopy;

DELIMITER //

/** 
 * Find the roots for f(x), where
 * f(x) = ax^3 + bx^2 + cx + d
 *
 * f(x) = x^3 + a2 x^2 + a1 x + a0
 *
 * f(x) = x^3 + 8/15 x^2 -7/45 x - 2/45 = 0
 * does not give all the roots
 *
 */
CREATE PROCEDURE pTestGetCubicRootsCopy(IN ia2 DOUBLE
                                       ,IN ia1 DOUBLE
                                       ,IN ia0 DOUBLE
                                       ,OUT op_small_denom DOUBLE
                                       ,OUT op_small_nom DOUBLE
                                       ,OUT oq_small_denom DOUBLE
                                       ,OUT oq_small_nom DOUBLE
                                       ,OUT oC DOUBLE
                                       ,OUT oQ_large_denom DOUBLE
                                       ,OUT oQ_large_nom DOUBLE
                                       ,OUT oR_large_denom DOUBLE
                                       ,OUT oR_large_nom DOUBLE
                                       ,OUT otheta DOUBLE
                                       ,OUT oz DOUBLE
                                       ,OUT ogeval INT
                                       ,OUT oarg DOUBLE
                                       ,OUT oy  DOUBLE
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
  DECLARE Q_denom,Q_nom,R_denom,R_nom,D_denom,D_nom DOUBLE;
  DECLARE p_small_denom,p_small_nom,q_small_denom,q_small_nom,C,arg,y DOUBLE;
  DECLARE Q_large_denom,Q_large_nom,R_large_denom,R_large_nom DOUBLE;
  DECLARE x1 DOUBLE DEFAULT NULL;
  DECLARE x2 DOUBLE DEFAULT NULL;
  DECLARE x3 DOUBLE DEFAULT NULL;

  SET Q_denom = 3 * ia1 - ia2 * ia2;
  SET Q_nom = 9;
  SET R_denom = 9 * ia2 * ia1 - 27 * ia0 - 2 * ia2 * ia2 * ia2;
  SET R_nom = 54;
  SET D_denom =   R_nom * R_nom * Q_denom * Q_denom * Q_denom
                + Q_nom * Q_nom * Q_nom * R_denom * R_denom;
  SET D_nom = Q_nom * Q_nom * Q_nom * R_nom * R_nom;

    /*SET theta = ACOS(R_denom * SQRT(-Q_denom * Q_denom * Q_denom) / 2 );*/

  SET p_small_denom = 3 * ia1 - ia2 * ia2;
  SET op_small_denom = p_small_denom;
  SET p_small_nom = 3;
  SET op_small_nom = p_small_nom;
  SET q_small_denom = 9 * ia2 * ia1 - 27 * ia0 - 2 * ia2 * ia2 * ia2;
  SET oq_small_denom = q_small_denom;
  SET q_small_nom = 27;
  SET oq_small_nom = q_small_nom;
  SET C =   q_small_denom 
          / (2 * ABS(3 * ia1 - ia2 * ia2) * SQRT(ABS(3 * ia1 - ia2 * ia2)));
  SET oC = C;
  
  SET Q_large_denom = p_small_denom;
  SET oQ_large_denom = Q_large_denom;
  SET Q_large_nom = 9;
  SET oQ_large_nom = Q_large_nom;
  SET R_large_denom = q_small_denom;
  SET oR_large_denom = R_large_denom;
  SET R_large_nom = 54;
  SET oR_large_nom = R_large_nom;
  SET theta = ACOS( R_large_denom 
                  / (18 * SQRT(-Q_large_denom * Q_large_denom * Q_large_denom))
                  );
  SET otheta = theta;
  SET x2 = (2 * SQRT(Q_large_denom) * COS(theta) - ia2) / 3;
  SET oz = x2;

  IF 3 * ia1 > ia2 * ia2 THEN
    SET ogeval = 1;
    /* sinh^-1 x := ln(x + sqrt(x*x+1)) */
    SET arg = LN(C + SQRT(C * C + 1)) / 3;
    SET y = (EXP(arg) - EXP(-arg)) / 2;
  ELSE
    IF 3 * ia1 < ia2 * ia2 THEN
      IF ABS(C) <= 1 THEN
        SET ogeval = 2;
        SET y = COS(ACOS(C) / 3);
      ELSE
        IF C > 1 THEN
          SET ogeval = 3;
          /* cosh^-1 x := ln(x + sqrt(x*x-1)), for x>=1 */
          SET arg = LN(C + SQRT(C * C - 1)) / 3;
          SET y = (EXP(arg) + EXP(-arg)) / 2;
        END IF;
        IF C < -1 THEN
          SET ogeval = 4;
          SET arg = LN(ABS(C) + SQRT(C * C - 1)) / 3;
          SET y = -(EXP(arg) + EXP(-arg)) / 2;
        END IF;
      END IF;
    ELSE 
      SET ogeval = 5;
    END IF;
  END IF;

  SET oarg = arg;
  SET oy = y;
  SET x1 = (2 * SQRT(ABS(p_small_denom)) * y - ia2) / 3;


/*
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
*/
  SET ox1 = x1;
  SET ox2 = x2;
  SET ox3 = x3;
  /*SET ox2 = r + SQRT(Delta);
  SET ox3 = r - SQRT(Delta);*/

END;
//

DELIMITER ;

