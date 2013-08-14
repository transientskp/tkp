/*
 All parameters should be in *degrees*.
 Returns a dimensionless number.

 Boolean `cross_meridian` should be true if the input RA values % 360 lie 
 either side of the meridian line. 
 */
CREATE FUNCTION deruiter(ra1 DOUBLE PRECISION, dec1 DOUBLE PRECISION,
						 ra1_err DOUBLE PRECISION, dec1_err DOUBLE PRECISION,
						 ra2 DOUBLE PRECISION, dec2 DOUBLE PRECISION,
						 ra2_err DOUBLE PRECISION, dec2_err DOUBLE PRECISION,
						 cross_meridian BOOL
						 )
RETURNS DOUBLE PRECISION

{% ifdb postgresql %}
AS $$
DECLARE delta_ra DOUBLE PRECISION;
DECLARE delta_dec DOUBLE PRECISION;
BEGIN
--	delta_ra := ra1 - ra2; 
--  Belt and braces approach: (can be reverted to simple version, *if*
--  it can be guaranteed that inputs are sanitised to  0 <= RA < 360.
	IF cross_meridian IS TRUE
	THEN
		delta_ra := MOD(CAST(ra1 + 180 AS NUMERIC(11,8)), 360) 
						- MOD(CAST(ra2 + 180 AS NUMERIC(11,8)), 360);
	ELSE
		delta_ra := MOD(CAST(ra1 AS NUMERIC(11,8)), 360) - MOD(CAST(ra2 AS NUMERIC(11,8)), 360);
	END IF;
	delta_dec := dec1 - dec2;
{% endifdb %}

{% ifdb monetdb %}
BEGIN
	DECLARE delta_ra DOUBLE PRECISION;
	DECLARE delta_dec DOUBLE PRECISION;
	IF cross_meridian = TRUE 
	THEN
		SET delta_ra = MOD( (ra1 + 180), 360) 
						- MOD( (ra2 + 180), 360);
	ELSE
		SET delta_ra = MOD(ra1, 360) - MOD(ra2, 360);
	END IF;
	SET delta_dec = dec1 - dec2;
{% endifdb %}
  
  RETURN SQRT(  delta_ra*delta_ra /
				(ra1_err*ra1_err + ra2_err*ra2_err)   
				+ 
				delta_dec*delta_dec /
				(dec1_err*dec1_err + dec2_err*dec2_err)
			);
END;
{% ifdb postgresql %}
$$ LANGUAGE plpgsql;
{% endifdb %}

