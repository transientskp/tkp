--DROP FUNCTION solidangle_arcsec2;

/**
 * This function computes the solid angle of and area subtended by
 * an ra_min and _max and a decl_min and _max.
 * INPUT in degrees, OUTPUT in arcsec^2.
 *
 * because input units are in degrees we have to convert
 * and we have to inflate ra toward the poles, therefore, 
 * use as follows to determine the solid angle of a source with
 * positional errors:
 * SELECT solidangle_arcsec2(@ra - alpha(@ra_err / 3600, @decl)
 *                          ,@ra + alpha(@ra_err / 3600, @decl)
 *                          ,@decl - @decl_err / 3600
 *                          ,@decl + @decl_err / 3600
 *                          ) AS 'solid angle [arcsec^2]'
 * ;
 */
CREATE FUNCTION solidangle_arcsec2(ra_min DOUBLE
                                  ,ra_max DOUBLE
                                  ,decl_min DOUBLE
                                  ,decl_max DOUBLE
                                  ) RETURNS DOUBLE 
BEGIN

  RETURN 2332800000 * (ra_max - ra_min) * (SIN(RADIANS(decl_max)) - SIN(RADIANS(decl_min))) / PI();

END;
