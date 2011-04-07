--DROP FUNCTION alpha;

/**
 * This function computes the ra expansion for a given theta at 
 * a given declination.
 * theta and decl are both in degrees.
 */
CREATE FUNCTION alpha(theta DOUBLE, decl DOUBLE) RETURNS DOUBLE 
BEGIN
  IF ABS(decl) + theta > 89.9 THEN 
    RETURN 180;
  ELSE 
    RETURN deg(ABS(ATAN(SIN(rad(theta)) / SQRT(ABS(COS(rad(decl - theta)) * COS(rad(decl + theta))))))) ; 
  END IF ;
END;
