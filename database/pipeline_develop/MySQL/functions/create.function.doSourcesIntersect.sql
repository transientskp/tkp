DROP FUNCTION IF EXISTS doSourcesIntersect;

DELIMITER //

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
CREATE FUNCTION doSourcesIntersect(i1ra DOUBLE
                                  ,i1decl DOUBLE
                                  ,i1ra_err DOUBLE
                                  ,i1decl_err DOUBLE
                                  ,i2ra DOUBLE
                                  ,i2decl DOUBLE
                                  ,i2ra_err DOUBLE
                                  ,i2decl_err DOUBLE
                                  ) RETURNS BOOLEAN
DETERMINISTIC
BEGIN
  
  DECLARE southeast, northeast, southwest, northwest BOOLEAN DEFAULT FALSE;
  DECLARE ra1_err, decl1_err, ra2_err, decl2_err DOUBLE;
  DECLARE tr_ra, tr_decl, bl_ra, bl_decl DOUBLE;
  DECLARE tl_ra, tl_decl, br_ra, br_decl DOUBLE;
  DECLARE dointersect BOOLEAN DEFAULT FALSE;

  /**
   * The ra_err is inflated at declinations near the pole. 
   * To calculate the new value we use the function alpha and
   * convert from arcsec to degrees.
   */
  SET ra1_err = alpha(i1ra_err / 3600, i1decl);
  SET decl1_err = i1decl_err / 3600;
  SET ra2_err = alpha(i2ra_err / 3600, i2decl);
  SET decl2_err = i2decl_err / 3600;
  
  IF i1ra > i2ra THEN
    /* source 1 is east of source 2 */
    IF i1decl < i2decl THEN
      /* source 1 is southeast of source 2 */
      SET southeast = TRUE;
    ELSE
      /* source 1 is northeast of source 2 */
      SET northeast = TRUE;
    END IF;
  ELSE
    /* source 1 is west of source 2 */
    IF i1decl < i2decl THEN
      /* source 1 is southwest of source 2 */
      SET southwest = TRUE;
    ELSE
      /* source 1 is northwest of source 2 */
      SET northwest = TRUE;
    END IF;
  END IF;

  IF southeast = TRUE THEN
    SET tr_ra = i1ra - ra1_err;
    SET tr_decl = i1decl + decl1_err;
    SET bl_ra = i2ra + ra2_err;
    SET bl_decl = i2decl - decl2_err;
    IF tr_ra < bl_ra AND tr_decl > bl_decl THEN
      SET dointersect = TRUE;
    END IF;
  END IF;

  IF northeast = TRUE THEN
    SET br_ra = i1ra - ra1_err;
    SET br_decl = i1decl - decl1_err;
    SET tl_ra = i2ra + ra2_err;
    SET tl_decl = i2decl + decl2_err;
    IF tl_ra > br_ra AND tl_decl > br_decl THEN
      SET dointersect = TRUE;
    END IF;
  END IF;

  IF southwest = TRUE THEN
    SET tl_ra = i1ra + ra1_err;
    SET tl_decl = i1decl + decl1_err;
    SET br_ra = i2ra - ra2_err;
    SET br_decl = i2decl - decl2_err;
    IF tl_ra > br_ra AND tl_decl > br_decl THEN
      SET dointersect = TRUE;
    END IF;
  END IF;

  IF northwest = TRUE THEN
    SET bl_ra = i1ra + ra1_err;
    SET bl_decl = i1decl - decl1_err;
    SET tr_ra = i2ra - ra2_err;
    SET tr_decl = i2decl + decl2_err;
    IF tr_ra < bl_ra AND tr_decl > bl_decl THEN
      SET dointersect = TRUE;
    END IF;
  END IF;

  RETURN dointersect;

END;
//

DELIMITER ;
