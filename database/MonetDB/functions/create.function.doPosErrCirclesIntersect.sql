/* These functions need to be dropped first before doPos
 * can be dropped 
 */
--DROP PROCEDURE AssocXSources2XSourcesByImage;
--DROP PROCEDURE AssocXSources2CatByZones;
--DROP FUNCTION doPosErrCirclesIntersect;

/*+-------------------------------------------------------------------+
 *| This function quantifies a source intersection by a weight number.|
 *| If two sources do not intersect the weight is -1, if there is     |
 *| the weight is the solid angle of the intersection area divided by |
 *| the area of the smallest positional error.                        |
 *| This function uses the ra and decl, and their errors in arcsec.   |
 *| To take ra inflation into account, we use the function alpha, so  |
 *| the ra + alpha(ra_err) are correctly set.                         |
 *|                                                                   |
 *| As an example the case where source 1 is SOUTHEAST of source 2:   |
 *|                                                                   |
 *|              +---------+                                          |
 *|              |  tr     |                                          |
 *|      +-------+---o* 2  |< decl_max                                |
 *|      |       |   |     |                ^                         |
 *|      |       o---+-----+< decl_min      |                         |
 *|      |    1* bl  |                     decl                       |
 *|      |           |                      |                         |
 *|      |           |                                                |
 *|      +-----------+                                                |
 *|              ^   ^                                                |
 *|          ra_max  ra_min                                           |
 *|                                                                   |
 *|                     <-- ra --                                     |
 *|                                                                   |
 *+-------------------------------------------------------------------+
 *|                                                                   |
 *+-------------------------------------------------------------------+
 */
CREATE FUNCTION doPosErrCirclesIntersect(i1ra DOUBLE
                                        ,i1decl DOUBLE
                                        ,i1ra_err DOUBLE
                                        ,i1decl_err DOUBLE
                                        ,i2ra DOUBLE
                                        ,i2decl DOUBLE
                                        ,i2ra_err DOUBLE
                                        ,i2decl_err DOUBLE
                                        ) RETURNS BOOLEAN
BEGIN
  
  /* Units in arcsec */
  DECLARE avg_radius, distance DOUBLE;
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

  IF distance / avg_radius < 6.0 THEN
    SET dointersect = TRUE;
  ELSE
    SET dointersect = FALSE;
  END IF;

  RETURN dointersect;

END;

