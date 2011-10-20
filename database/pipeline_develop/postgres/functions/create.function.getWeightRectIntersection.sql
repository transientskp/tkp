--DROP FUNCTION getWeightRectIntersection;

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
CREATE FUNCTION getWeightRectIntersection(i1ra double precision
                                         ,i1decl double precision
                                         ,i1ra_err double precision
                                         ,i1decl_err double precision
                                         ,i2ra double precision
                                         ,i2decl double precision
                                         ,i2ra_err double precision
                                         ,i2decl_err double precision
                                         ) RETURNS double precision as $$
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
  DECLARE ra_min double precision;
declare ra_max double precision;
declare decl_min double precision;
declare decl_max double precision;
  DECLARE intersection_area double precision;
declare area1 double precision;
declare area2 double precision;
declare weight double precision;
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
    IF dointersect = TRUE THEN
      IF tr_ra < i2ra - ra2_err THEN
        ra_min := i2ra - ra2_err;
      ELSE
        ra_min := tr_ra;
      END IF;
      IF bl_ra > i1ra + ra1_err THEN
        ra_max := i1ra + ra1_err;
      ELSE
        ra_max := bl_ra;
      END IF;
      IF bl_decl < i1decl - decl1_err THEN
        decl_min := i1decl - decl1_err;
      ELSE
        decl_min := bl_decl;
      END IF;
      IF tr_decl > i2decl + decl2_err THEN
        decl_max := i2decl + decl2_err;
      ELSE
        decl_max := tr_decl;
      END IF;
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
    IF dointersect = TRUE THEN
      IF br_ra < i2ra - ra2_err THEN
        ra_min := i2ra - ra2_err;
      ELSE
        ra_min := br_ra;
      END IF;
      IF tl_ra > i1ra + ra1_err THEN
        ra_max := i1ra + ra1_err;
      ELSE
        ra_max := tl_ra;
      END IF;
      IF br_decl < i2decl - decl2_err THEN
        decl_min := i2decl - decl2_err;
      ELSE
        decl_min := br_decl;
      END IF;
      IF tl_decl > i1decl + decl1_err THEN
        decl_max := i1decl + decl1_err;
      ELSE
        decl_max := tl_decl;
      END IF;
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
    IF dointersect = TRUE THEN
      IF br_ra < i1ra - ra1_err THEN
        ra_min := i1ra - ra1_err;
      ELSE
        ra_min := br_ra;
      END IF;
      IF tl_ra > i2ra + ra2_err THEN
        ra_max := i2ra + ra2_err;
      ELSE
        ra_max := tl_ra;
      END IF;
      IF br_decl < i1decl - decl1_err THEN
        decl_min := i1decl - decl1_err;
      ELSE
        decl_min := br_decl;
      END IF;
      IF tl_decl > i2decl + decl2_err THEN
        decl_max := i2decl + decl2_err;
      ELSE
        decl_max := tl_decl;
      END IF;
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
    IF dointersect = TRUE THEN
      IF tr_ra < i1ra - ra1_err THEN
        ra_min := i1ra - ra1_err;
      ELSE
        ra_min := tr_ra;
      END IF;
      IF bl_ra > i2ra + ra2_err THEN
        ra_max := i2ra + ra2_err;
      ELSE
        ra_max := bl_ra;
      END IF;
      IF bl_decl < i2decl - decl2_err THEN
        decl_min := i2decl - decl2_err;
      ELSE
        decl_min := bl_decl;
      END IF;
      IF tr_decl > i1decl + decl1_err THEN
        decl_max := i1decl + decl1_err;
      ELSE
        decl_max := tr_decl;
      END IF;
    END IF;
  END IF;

  IF dointersect = TRUE THEN
    intersection_area := solidangle_arcsec2(ra_min
                                              ,ra_max
                                              ,decl_min
                                              ,decl_max
                                              );
    area1 := solidangle_arcsec2(i1ra - ra1_err
                                  ,i1ra + ra1_err
                                  ,i1decl - decl1_err
                                  ,i1decl + decl1_err
                                  );
    area2 := solidangle_arcsec2(i2ra - ra2_err
                                  ,i2ra + ra2_err
                                  ,i2decl - decl2_err
                                  ,i2decl + decl2_err
                                  );
    IF area1 < area2 THEN
      weight := intersection_area / area1;
    ELSE
      weight := intersection_area / area2;
    END IF;
  ELSE
    weight := -1;
  END IF;

  RETURN weight;

END;
$$ language plpgsql;
