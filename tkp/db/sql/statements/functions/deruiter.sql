--DROP FUNCTION deruiter;

/**
 All parameters should be in *degrees*.
 Returns a dimensionless number.
 
 (Currently just a placeholder while I re-learn the different SQL dialects...)
 */
CREATE FUNCTION deruiter(ra1 DOUBLE PRECISION, dec1 DOUBLE PRECISION,
						 ra1_err DOUBLE PRECISION, dec1_err DOUBLE PRECISION,
						 ra2 DOUBLE PRECISION, dec2 DOUBLE PRECISION,
						 ra2_err DOUBLE PRECISION, dec2_err DOUBLE PRECISION
						 )
RETURNS DOUBLE PRECISION

{% ifdb postgresql %}
AS $$
DECLARE delta_dec DOUBLE PRECISION;
BEGIN
/*  delta_ra := (MOD(CAST(ra1 + 180 AS NUMERIC(11,8)), 360) * COS(RADIANS(dec1)) 
  				- MOD(CAST(ra2 + 180 AS NUMERIC(11,8)), 360) * COS(RADIANS(dec1)))
*/
  delta_dec := dec1 - dec2; 

  RETURN delta_dec;
END;
$$ LANGUAGE plpgsql;
{% endifdb %}

{% ifdb monetdb %}

BEGIN
DECLARE delta_dec DOUBLE PRECISION;
  set delta_dec = dec1 - dec2;
  RETURN delta_dec;
  
END;

{% endifdb %}