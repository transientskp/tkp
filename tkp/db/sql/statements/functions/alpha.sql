--DROP FUNCTION alpha;

/**
 * This function computes the ra expansion for a given theta at 
 * a given declination.
 * theta and decl are both in degrees.
 */
CREATE FUNCTION alpha(theta DOUBLE PRECISION, decl DOUBLE PRECISION)
RETURNS DOUBLE PRECISION

{% ifdb postgresql %}
AS $$
{% endifdb %}

BEGIN
  IF ABS(decl) + theta > 89.9 THEN 
    RETURN 180;
  ELSE 
    RETURN DEGREES(ABS(ATAN(SIN(RADIANS(theta)) / SQRT(ABS(COS(RADIANS(decl - theta)) * COS(RADIANS(decl + theta))))))) ; 
  END IF ;
END;

{% ifdb postgresql %}
$$ LANGUAGE plpgsql;
{% endifdb %}
