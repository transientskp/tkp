--DROP FUNCTION alpha;

/**
 * This function computes the ra expansion for a given theta at 
 * a given declination.
 * theta and decl are both in degrees.
 *
 * For a derivation, see MSR TR 2006 52, Section 2.1
 * http://research.microsoft.com/apps/pubs/default.aspx?id=64524
 */
CREATE FUNCTION alpha(theta DOUBLE PRECISION, decl DOUBLE PRECISION)
RETURNS DOUBLE PRECISION

{% if db.engine == 'postgresql' %}
AS $$
{% endif %}

BEGIN
  IF ABS(decl) + theta > 89.9 THEN 
    RETURN 180;
  ELSE 
    RETURN DEGREES(ABS(ATAN(SIN(RADIANS(theta)) / SQRT(ABS(COS(RADIANS(decl - theta)) * COS(RADIANS(decl + theta))))))) ; 
  END IF ;
END;

{% if db.engine == 'postgresql' %}
$$ LANGUAGE plpgsql;
{% endif %}
