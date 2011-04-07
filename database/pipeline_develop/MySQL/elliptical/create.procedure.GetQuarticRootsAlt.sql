DROP PROCEDURE IF EXISTS GetQuarticRootsAlt;

DELIMITER //

/** 
 * Find the roots for the quartic equation in the form of
 * A x^4 + B x^3 + C x^2 + D x + E = 0
 * or standard:
 * x^4 + a3 x^3 + a2 x^2 + a1 x + a0 = 0
 * 
 * It will be rewritten in the standard form:
 * x^4 + p x^2 + q x + r = 0
 *
 * By using any real root of the resolvent cubic, we
 * can solve for the roots of the quartic.
 *
 * NOTE: In conjunction with the procedures and function for
 * elliptical intersection the output values are actually the y-values
 * for the intersection points.
 *
 * TODO: 
 * (1):
 * (x-2)^4 = 0, x^4 -8 x^3 +24 x^2 -32  x + 16 = 0
 * does give all NULL results, but this should be 4 times 2.
 *
 * (2):
 * a4 = 1,
 * a3 = -36.5714285714286
 * a2 = 399.510204081633 
 * a1 = -1191.18367346939 
 * a0 = 1060.89795918367
 * should give two times 16.2857142857143 , and two times 2.
 * But it may incorrectly give all NULL results. 
 *
 * call GetQuarticRootsAlt(1,0,6,-60,36,@z1,@z2,@z3,@z4);select @z1,@z2,@z3,@z4;
 *
 */
CREATE PROCEDURE GetQuarticRootsAlt(IN iA DOUBLE
                                ,IN iB DOUBLE
                                ,IN iC DOUBLE
                                ,IN iD DOUBLE
                                ,IN iE DOUBLE
                                ,OUT oz1 DOUBLE
                                ,OUT oz2 DOUBLE
                                ,OUT oz3 DOUBLE
                                ,OUT oz4 DOUBLE
                                ) 
BEGIN

  DECLARE a3, a2, a1, a0, b2, b1, b0 DOUBLE;
  DECLARE ogeval INT;
  DECLARE y1, R_cap, D_cap, E_cap, D_cap_arg, E_cap_arg DOUBLE;
  DECLARE z1, z2, z3, z4 DOUBLE;

  SET a3 = iB / iA;
  SET a2 = iC / iA;
  SET a1 = iD / iA;
  SET a0 = iE / iA;

  SET b2 = -a2;
  SET b1 = a1 * a3 - 4 * a0;
  SET b0 = 4 * a2 * a0 - a1 * a1 - a3 * a3 * a0;

  SET y1 = getCubicAnyRealRoot(b2,b1,b0);

  IF ABS(a3 * a3 / 4 - a2 + y1) < 1E-10 THEN
    /* We assume R = 0 */
    SET ogeval = 1;
    SET R_cap = 0;
    SET D_cap = SQRT(3 * a3 * a3 / 4 - 2 * a2 + 2 * SQRT(y1 * y1 - 4 * a0));
    SET E_cap = SQRT(3 * a3 * a3 / 4 - 2 * a2 - 2 * SQRT(y1 * y1 - 4 * a0));
  ELSE
    IF a2 - a3 * a3 / 4 > y1 THEN
      /* root argument is negative */
      SET ogeval = 2;
    ELSE
      SET ogeval = 3;
      SET R_cap = SQRT(a3 * a3 / 4 - a2 + y1);
      SET D_cap_arg =   3 * a3 * a3 / 4 
                      - R_cap * R_cap 
                      - 2 * a2 
                      + (4 * a2 * a3 - 8 * a1 - a3 * a3 * a3) / (4 * R_cap);
      IF D_cap_arg < 1E-10 THEN
        SET D_cap = 0;
      ELSE
        SET D_cap = SQRT(D_cap_arg); 
      END IF;
      SET E_cap_arg =   3 * a3 * a3 / 4 
                      - R_cap * R_cap 
                      - 2 * a2 
                      - (4 * a2 * a3 - 8 * a1 - a3 * a3 * a3) / (4 * R_cap);
      IF E_cap_arg < 1E-10 THEN
        SET E_cap = 0;
      ELSE
        SET E_cap = SQRT(E_cap_arg);
      END IF;
    END IF;
  END IF;

  SET z1 = -a3 / 4 + R_cap / 2 + D_cap / 2;
  SET z2 = -a3 / 4 + R_cap / 2 - D_cap / 2;
  SET z3 = -a3 / 4 - R_cap / 2 + E_cap / 2;
  SET z4 = -a3 / 4 - R_cap / 2 - E_cap / 2;

  IF z1 IS NOT NULL THEN
    SET oz1 = z1;
  END IF;
  IF z2 IS NOT NULL THEN
    IF oz1 IS NOT NULL THEN
      SET oz2 = z2;
    ELSE
      SET oz1 = z2;
    END IF;
  END IF;
  IF z3 IS NOT NULL THEN
    IF oz1 IS NOT NULL THEN
      IF oz2 IS NOT NULL THEN
        SET oz3 = z3;
      ELSE
        SET oz2 = z3;
      END IF;
    ELSE
      SET oz1 = z3;
    END IF;
  END IF;
  IF z4 IS NOT NULL THEN
    IF oz1 IS NOT NULL THEN
      IF oz2 IS NOT NULL THEN
        IF oz3 IS NOT NULL THEN
          SET oz4 = z4;
        ELSE
          SET oz3 = z4;
        END IF;
      ELSE
        SET oz2 = z4;
      END IF;
    ELSE
      SET oz1 = z4;
    END IF;
  END IF;

END;
//

DELIMITER ;

