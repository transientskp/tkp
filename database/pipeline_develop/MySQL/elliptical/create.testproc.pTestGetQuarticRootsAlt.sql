DROP PROCEDURE IF EXISTS pTestGetQuarticRootsAlt;

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
 * call pTestGetQuarticRootsAlt(1,0,6,-60,36,@a3,@a2,@a1,@a0,@b2,@b1,@b0,@y1,@geval,@R_cap,@D_cap,@E_cap,@zz1,@zz2,@zz3,@zz4,@z1,@z2,@z3,@z4);select @a3,@a2,@a1,@a0,@b2,@b1,@b0,@y1;select @geval,@R_cap,@D_cap,@E_cap,@zz1,@zz2,@zz3,@zz4,@z1,@z2,@z3,@z4;
 *
 */
CREATE PROCEDURE pTestGetQuarticRootsAlt(IN iA DOUBLE
                                ,IN iB DOUBLE
                                ,IN iC DOUBLE
                                ,IN iD DOUBLE
                                ,IN iE DOUBLE
                                ,OUT oa3 DOUBLE
                                ,OUT oa2 DOUBLE
                                ,OUT oa1 DOUBLE
                                ,OUT oa0 DOUBLE
                                ,OUT ob2 DOUBLE
                                ,OUT ob1 DOUBLE
                                ,OUT ob0 DOUBLE
                                ,OUT oy1 DOUBLE
                                ,OUT ogeval DOUBLE
                                ,OUT oR_cap DOUBLE
                                ,OUT oD_cap DOUBLE
                                ,OUT oE_cap DOUBLE
                                ,OUT ozz1 DOUBLE
                                ,OUT ozz2 DOUBLE
                                ,OUT ozz3 DOUBLE
                                ,OUT ozz4 DOUBLE
                                ,OUT oz1 DOUBLE
                                ,OUT oz2 DOUBLE
                                ,OUT oz3 DOUBLE
                                ,OUT oz4 DOUBLE
                                ) 
BEGIN

  DECLARE a3, a2, a1, a0, b2, b1, b0 DOUBLE;
  DECLARE y1, R_cap, D_cap, E_cap, D_cap_arg, E_cap_arg DOUBLE;
  DECLARE z1, z2, z3, z4 DOUBLE;

  SET a3 = iB / iA;
  SET a2 = iC / iA;
  SET a1 = iD / iA;
  SET a0 = iE / iA;
  SET oa3 = a3;
  SET oa2 = a2;
  SET oa1 = a1;
  SET oa0 = a0;

  SET b2 = -a2;
  SET b1 = a1 * a3 - 4 * a0;
  SET b0 = 4 * a2 * a0 - a1 * a1 - a3 * a3 * a0;

  SET ob2 = b2;
  SET ob1 = b1;
  SET ob0 = b0;

  SET y1 = getCubicAnyRealRoot(b2,b1,b0);
  SET oy1 = y1;

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
  SET oR_cap = R_cap;
  SET oD_cap = D_cap;
  SET oE_cap = E_cap;

  SET z1 = -a3 / 4 + R_cap / 2 + D_cap / 2;
  SET z2 = -a3 / 4 + R_cap / 2 - D_cap / 2;
  SET z3 = -a3 / 4 - R_cap / 2 + E_cap / 2;
  SET z4 = -a3 / 4 - R_cap / 2 - E_cap / 2;

  SET ozz1 = z1;
  SET ozz2 = z2;
  SET ozz3 = z3;
  SET ozz4 = z4;

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

