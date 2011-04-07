DROP PROCEDURE IF EXISTS pTestGetQuarticRoots;

DELIMITER //

/** 
 * Find the roots for f(x), where
 * f(x) = Ax^4 + Bx^3 + Cx^2 + Dx + E = 0
 *
 * call getquarticroots(3,6,-123,-126,1080,@oalpha,@obeta,@ogamma,@ox1,@ox2,@ox3,@ox4);
 * must give
 * x1 = 5, x2 = 3, x3 = -4, x4 = -6
 *
 * Test f.ex. this function:
 * (A, ..., E) = (1,-2,-7,20,-12)
 * i.e (x-2)^2 (x-1) (x+3) = 0
 *
 * NOTE: In conjunction with the procedures and function for
 * elliptical intersection the output values are actually the y-values
 * for the intersection points.
 */
CREATE PROCEDURE pTestGetQuarticRoots(IN iA DOUBLE
                                ,IN iB DOUBLE
                                ,IN iC DOUBLE
                                ,IN iD DOUBLE
                                ,IN iE DOUBLE
                                ,OUT oalpha DOUBLE
                                ,OUT obeta DOUBLE
                                ,OUT ogamma DOUBLE
                                ,OUT oP DOUBLE
                                ,OUT oQ DOUBLE
                                ,OUT oRR DOUBLE
                                ,OUT oU DOUBLE
                                ,OUT oV DOUBLE
                                ,OUT osol1 DOUBLE
                                ,OUT osol2 DOUBLE
                                ,OUT osol3 DOUBLE
                                ,OUT osol DOUBLE
                                ,OUT oy DOUBLE
                                ,OUT oW DOUBLE
                                ,OUT ox1 DOUBLE
                                ,OUT ox2 DOUBLE
                                ,OUT ox3 DOUBLE
                                ,OUT ox4 DOUBLE
                                ) 
BEGIN
  DECLARE alpha, beta, gamma DOUBLE;
  DECLARE P, Q, /*R, U, V,*/ W, y DOUBLE;
  DECLARE sol, sol1, sol2, sol3 DOUBLE;
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
  SET oalpha = alpha;
  SET obeta = beta;
  SET ogamma = gamma;

  IF beta = 0 THEN
    SET x1 = -iB / (4 * iA) + SQRT((-alpha + SQRT(alpha * alpha - 4 * gamma)) / 2);
    SET x2 = -iB / (4 * iA) + SQRT((-alpha - SQRT(alpha * alpha - 4 * gamma)) / 2);
    SET x3 = -iB / (4 * iA) - SQRT((-alpha + SQRT(alpha * alpha - 4 * gamma)) / 2);
    SET x4 = -iB / (4 * iA) - SQRT((-alpha - SQRT(alpha * alpha - 4 * gamma)) / 2);
  ELSE 
    /*TODO: check if gamma = 0*/
    SET P = - alpha * alpha / 12 
            - gamma;
    SET oP = P;
    SET Q = - alpha * alpha * alpha / 108
            + (alpha * gamma) / 3
            - (beta * beta) / 8;
    SET oQ = Q;
    /*SET R = - Q / 2
            + SQRT(Q * Q / 4 + P * P * P / 27);
    SET U = POW(R, 1/3);
    SET oRR = R;
    SET oU = U;
    IF U = 0 THEN
      SET V = - POW(Q, 1/3);
    ELSE
      SET V = - P / (3 * U);
    END IF;
    SET oV = V;
    SET y = - (5 * alpha) / 6 + U + V;*/
    CALL getCubicRoots(1, 0, P, Q, sol1, sol2, sol3);
    /* Any solution will do, so we pick one*/
    SET osol1 = sol1;
    SET osol2 = sol2;
    SET osol3 = sol3;
    IF sol1 IS NOT NULL THEN
      SET sol = sol1;
    ELSE
      IF sol2 IS NOT NULL THEN
        SET sol = sol2;
      ELSE
        IF sol3 IS NOT NULL THEN
          SET sol = sol3;
        END IF;
      END IF;
    END IF;
    SET osol = sol;
    SET y = - (5 * alpha) / 6 + sol;
    SET oy = y;
    SET W = SQRT(alpha + 2 * y);
    SET oW = W;
    SET x1 = - iB / (4 * iA)
             + (W + SQRT(-(3 * alpha + 2 * y + (2 * beta) / W))) / 2;
    SET x2 = - iB / (4 * iA)
             + (W - SQRT(-(3 * alpha + 2 * y + (2 * beta) / W))) / 2;
    SET x3 = - iB / (4 * iA)
             + (-W + SQRT(-(3 * alpha + 2 * y - (2 * beta) / W))) / 2;
    SET x4 = - iB / (4 * iA)
             + (-W - SQRT(-(3 * alpha + 2 * y - (2 * beta) / W))) / 2;
  END IF;

  SET ox1 = x1;
  SET ox2 = x2;
  SET ox3 = x3;
  SET ox4 = x4;

END;
//

DELIMITER ;

