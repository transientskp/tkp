DROP PROCEDURE IF EXISTS getQuarticRoots;

DELIMITER //

/** 
 * Find the roots for f(x), where
 * f(x) = Ax^4 + Bx^3 + Cx^2 + Dx + E = 0
 *
 * call getquarticroots(3,6,-123,-126,1080,@oalpha,@obeta,@ogamma,@ox1,@ox2,@ox3,@ox4);
 * must give
 * x1 = 5, x2 = 3, x3 = -4, x4 = -6
 * 
 * NOTE: In conjunction with the procedures and function for
 * elliptical intersection the output values are actually the y-values
 * for the intersection points.
 */
CREATE PROCEDURE getQuarticRoots(IN iA DOUBLE
                                ,IN iB DOUBLE
                                ,IN iC DOUBLE
                                ,IN iD DOUBLE
                                ,IN iE DOUBLE
                                ,OUT ox1 DOUBLE
                                ,OUT ox2 DOUBLE
                                ,OUT ox3 DOUBLE
                                ,OUT ox4 DOUBLE
                                ) 
BEGIN
  DECLARE alpha, beta, gamma DOUBLE;
  DECLARE P, Q, W, y DOUBLE;
  DECLARE v, v1, v2, v3 DOUBLE;
  DECLARE x1, x2, x3, x4 DOUBLE DEFAULT NULL;

  SET alpha = - (3 * iB * iB) / (8 * iA * iA) 
              + iC / iA;
  SET beta = (iB * iB * iB) / (8 * iA * iA * iA)
             - (iB * iC) / (2 * iA * iA)
             + iD / iA;
  SET gamma = - (3 * iB * iB * iB * iB) / (256 * iA * iA * iA * iA)
              + (iC * iB * iB) / (16 * iA * iA * iA)
              - (iB * iD) / (4 * iA * iA)
              + iE / iA;

  IF beta = 0 THEN
    SET x1 = -iB / (4 * iA) + SQRT((-alpha + SQRT(alpha * alpha - 4 * gamma)) / 2);
    SET x2 = -iB / (4 * iA) + SQRT((-alpha - SQRT(alpha * alpha - 4 * gamma)) / 2);
    SET x3 = -iB / (4 * iA) - SQRT((-alpha + SQRT(alpha * alpha - 4 * gamma)) / 2);
    SET x4 = -iB / (4 * iA) - SQRT((-alpha - SQRT(alpha * alpha - 4 * gamma)) / 2);
  ELSE 
    SET P = - alpha * alpha / 12 
            - gamma;
    SET Q = - alpha * alpha * alpha / 108
            + (alpha * gamma) / 3
            - (beta * beta) / 8;
    CALL getCubicRoots(1, 0, P, Q, v1, v2, v3);
    /* Any solution will do, so we pick one*/
    IF v1 IS NOT NULL THEN
      SET v = v1;
    ELSE
      IF v2 IS NOT NULL THEN
        SET v = v2;
      ELSE
        IF v3 IS NOT NULL THEN
          SET v = v3;
        END IF;
      END IF;
    END IF;
    SET y = - (5 * alpha) / 6 + v;
    SET W = SQRT(alpha + 2 * y);
    SET x1 = - iB / (4 * iA)
             + (W + SQRT(-(3 * alpha + 2 * y + (2 * beta) / W))) / 2;
    SET x2 = - iB / (4 * iA)
             + (W - SQRT(-(3 * alpha + 2 * y + (2 * beta) / W))) / 2;
    SET x3 = - iB / (4 * iA)
             + (-W + SQRT(-(3 * alpha + 2 * y - (2 * beta) / W))) / 2;
    SET x4 = - iB / (4 * iA)
             + (-W - SQRT(-(3 * alpha + 2 * y - (2 * beta) / W))) / 2;
  END IF;

  /* We shift the NULL values backwards */
  IF x1 IS NOT NULL THEN
    SET ox1 = x1;
  END IF;
  IF x2 IS NOT NULL THEN
    IF ox1 IS NOT NULL THEN
      SET ox2 = x2;
    ELSE
      SET ox1 = x2;
    END IF;
  END IF;
  IF x3 IS NOT NULL THEN
    IF ox1 IS NOT NULL THEN
      IF ox2 IS NOT NULL THEN
        SET ox3 = x3;
      ELSE
        SET ox2 = x3;
      END IF;
    ELSE
      SET ox1 = x3;
    END IF;
  END IF;
  IF x4 IS NOT NULL THEN
    IF ox1 IS NOT NULL THEN
      IF ox2 IS NOT NULL THEN
        IF ox3 IS NOT NULL THEN
          SET ox4 = x4;
        ELSE
          SET ox3 = x4;
        END IF;
      ELSE
        SET ox2 = x4;
      END IF;
    ELSE
      SET ox1 = x4;
    END IF;
  END IF;
  
END;
//

DELIMITER ;

