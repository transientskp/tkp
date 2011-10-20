DECLARE i1ra,i1,decl double precision;
                                        ,i1decl double precision
                                        ,i1ra_err double precision
                                        ,i1decl_err double precision
                                        ,i2ra double precision
                                        ,i2decl double precision
                                        ,i2ra_err double precision
                                        ,i2decl_err double precision
                                        ) RETURNS BOOLEAN


SELECT *
  FROM assocxtrsources
;





BEGIN
  
  /* Units in arcsec */
  DECLARE avg_radius, distance double precision;
  DECLARE dointersect BOOLEAN;

  SET avg_radius = SQRT(i1ra_err * i1ra_err + i2ra_err * i2ra_err
                       + i1decl_err * i1decl_err + i2decl_err * i2decl_err
                       );

  SET distance = 3600 * DEGREES(2 * ASIN(SQRT(POWER((COS(RADIANS(i1decl)) * COS(RADIANS(i1ra))
                                                    - COS(RADIANS(i2decl)) * COS(RADIANS(i2ra))
                                                    ), 2)
                                             + POWER((COS(RADIANS(i1decl)) * SIN(RADIANS(i1ra))
                                                    - COS(RADIANS(i2decl)) * SIN(RADIANS(i2ra))
                                                    ), 2)
                                             + POWER((SIN(RADIANS(i1decl))
                                                    - SIN(RADIANS(i2decl))
                                                    ), 2)
                                             ) / 2));

  IF distance / avg_radius < 2.1 THEN
    SET dointersect = TRUE;
  ELSE
    SET dointersect = FALSE;
  END IF;

  RETURN dointersect;

END;

