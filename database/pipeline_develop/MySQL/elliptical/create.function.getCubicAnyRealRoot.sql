DROP FUNCTION IF EXISTS getCubicAnyRealRoot;

DELIMITER //

/** 
 * This function returns any real root of a cubic of the form
 * x^3 + a2 x^2 + a1 x + a0 = 0
 *
 * It will be rewritten into the form:
 * x^3 + p x = q
 *
 * To find any real root we evaluate p, and another defined 
 * value C. 
 *
 * Functions to be tested:
 * (1)
 * x^3 + 8/15 x^2 -7/45 x - 2/45 = 0 => one of (1/3,-2/3,1/5)
 *
 * (2)
 * x^3 - 10/3 x^2 + 14/3 x + 27/3 = 0 => -1, this one also has two 
 * complex solutions 13/6+yi, 13/6-yi
 *
 */
CREATE FUNCTION getCubicAnyRealRoot(ia2 DOUBLE
                                   ,ia1 DOUBLE
                                   ,ia0 DOUBLE
                                   ) RETURNS DOUBLE 
BEGIN

  DECLARE p_small_denom,p_small_nom,q_small_denom,q_small_nom,C,y DOUBLE;
/*my comment*/
  SET p_small_denom = 3 * ia1 - ia2 * ia2;
  SET p_small_nom = 3;
  SET q_small_denom = 9 * ia1 * ia2 - 27 * ia0 - 2 * ia2 * ia2 * ia2;
  SET q_small_nom = 27;
  SET C = q_small_denom / (2 * ABS(3 * ia1 - ia2 * ia2) 
                          * SQRT(ABS(3 * ia1 - ia2 * ia2)));

  /* Check if p > 0, and usage of */
  IF 3 * ia1 > ia2 * ia2 THEN
    SET y = sinh(asinh(C) / 3);
  ELSE
    IF 3 * ia1 < ia2 * ia2 THEN
      IF ABS(C) < 1 THEN
        SET y = COS(ACOS(C) / 3);
      ELSE
        IF C >= 1 THEN
          SET y = cosh(acosh(C) / 3);
        END IF;
        IF C <= -1 THEN
          SET y = -cosh(acosh(ABS(C)) / 3);
        END IF;
      END IF;
    ELSE
      IF q_small_denom = 0 THEN
        SET y = 0;
      END IF;
    END IF;
  END IF;
  
  RETURN (2 * SQRT(ABS(p_small_denom)) * y - ia2) / 3;

END;
//

DELIMITER ;

