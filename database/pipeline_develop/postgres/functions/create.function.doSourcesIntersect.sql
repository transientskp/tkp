--DROP FUNCTION IF EXISTS doSourcesIntersect;

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
CREATE FUNCTION doSourcesIntersect(i1ra double precision
                                  ,i1decl double precision
                                  ,i1ra_err double precision
                                  ,i1decl_err double precision
                                  ,i2ra double precision
                                  ,i2decl double precision
                                  ,i2ra_err double precision
                                  ,i2decl_err double precision
                                  ) RETURNS BOOLEAN as $$
  DECLARE southeast boolean;
declare northeast boolean;
declare southwest boolean;
declare northwest BOOLEAN;
  DECLARE ra1_err double precision;
declare decl1_err double precision;
declare ra2_err double precision;
declare decl2_err double precision;
  DECLARE tr_ra double precision;
declare tr_decl double precision;
declare bl_ra double precision;
declare bl_decl double precision;
  DECLARE tl_ra double precision;
declare tl_decl double precision;
declare br_ra double precision;
declare br_decl double precision;
  DECLARE dointersect BOOLEAN;
BEGIN
  
  SELECT FALSE
        ,FALSE
        ,FALSE
        ,FALSE
        ,FALSE
    INTO southeast
        ,northeast
        ,southwest
        ,northwest
        ,dointersect
        ;
  

  /**
   * The ra_err is inflated at declinations near the pole. 
   * To calculate the new value we use the function alpha and
   * convert from arcsec to degrees.
   */
  ra1_err := alpha(i1ra_err / 3600, i1decl);
  decl1_err := i1decl_err / 3600;
  ra2_err := alpha(i2ra_err / 3600, i2decl);
  decl2_err := i2decl_err / 3600;
  
  IF i1ra > i2ra THEN
    /* source 1 is east of source 2 */
    IF i1decl < i2decl THEN
      /* source 1 is southeast of source 2 */
      southeast := TRUE;
    ELSE
      /* source 1 is northeast of source 2 */
      northeast := TRUE;
    END IF;
  ELSE
    /* source 1 is west of source 2 */
    IF i1decl < i2decl THEN
      /* source 1 is southwest of source 2 */
      southwest := TRUE;
    ELSE
      /* source 1 is northwest of source 2 */
      northwest := TRUE;
    END IF;
  END IF;

  IF southeast = TRUE THEN
    tr_ra := i1ra - ra1_err;
    tr_decl := i1decl + decl1_err;
    bl_ra := i2ra + ra2_err;
    bl_decl := i2decl - decl2_err;
    IF tr_ra < bl_ra AND tr_decl > bl_decl THEN
      dointersect := TRUE;
    END IF;
  END IF;

  IF northeast = TRUE THEN
    br_ra := i1ra - ra1_err;
    br_decl := i1decl - decl1_err;
    tl_ra := i2ra + ra2_err;
    tl_decl := i2decl + decl2_err;
    IF tl_ra > br_ra AND tl_decl > br_decl THEN
      dointersect := TRUE;
    END IF;
  END IF;

  IF southwest = TRUE THEN
    tl_ra := i1ra + ra1_err;
    tl_decl := i1decl + decl1_err;
    br_ra := i2ra - ra2_err;
    br_decl := i2decl - decl2_err;
    IF tl_ra > br_ra AND tl_decl > br_decl THEN
      dointersect := TRUE;
    END IF;
  END IF;

  IF northwest = TRUE THEN
    bl_ra := i1ra + ra1_err;
    bl_decl := i1decl - decl1_err;
    tr_ra := i2ra - ra2_err;
    tr_decl := i2decl + decl2_err;
    IF tr_ra < bl_ra AND tr_decl > bl_decl THEN
      dointersect := TRUE;
    END IF;
  END IF;

  RETURN dointersect;

END;
$$ language plpgsql;
