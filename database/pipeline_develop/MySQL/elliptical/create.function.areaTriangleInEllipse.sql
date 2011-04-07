DROP FUNCTION IF EXISTS areaTriangleInEllipse;

DELIMITER //

/**
 * 
 * Based on D. Eberly's "The Area Of Intersecting Ellipses",
 * http://www.geometrictools.com/documentation/.
 *
 * An elliptical arc is determined by angles theta_0 and theta_1,
 * both in [-pi, pi].
 * If theta_0 < theta_1 it means that the arc does not cross 
 * the negative y axis else it does, in which case we set 
 * theta_1 = theta_1 + 2pi.
 *
 * This function computes the area of the triangle bounded by
 * the center of the ellipse and the angles theta_0 and *_1,
 * where the theta's are the angles projected on the circle
 * e_a      : the semi-major axis [arcsec]
 * e_b      : the semi-minor axis [arcsec]
 * theta_0  : startpoint of arc (in radians in range [-pi, pi])
 *            theta is defined as the angle from the center to 
 *            the projected points on the circle:
 *            x = a cos theta
 *            y = b sin theta
 * theta_1  : endpoint of arc (in radians in range [-pi, pi])
 *            See theta_0 for definition
 * We assume both theta's are set properly, so we 
 * do not have to reorder them.
 * 
 * area     : area of the triangle bounded by the origin
 *            and the angles theta_0 and theta_1
 */
CREATE FUNCTION areaTriangleInEllipse(e_a DOUBLE
                                     ,e_b DOUBLE
                                     ,c_theta_0 DOUBLE
                                     ,c_theta_1 DOUBLE
                                     ) RETURNS DOUBLE 
DETERMINISTIC 
BEGIN

  /**
   * Check the arc for crossing the negative y-axis,
   * if so we set theta_1 to theta_1 + 2pi.
   */
  IF c_theta_1 < c_theta_0 THEN
    /* In this case we have negative y crossing */
    SET c_theta_1 = c_theta_1 + 2 * PI();
  END IF;

  RETURN (e_a * e_b / 2) * ABS(SIN(c_theta_1 - c_theta_0));

END;
//

DELIMITER ;
