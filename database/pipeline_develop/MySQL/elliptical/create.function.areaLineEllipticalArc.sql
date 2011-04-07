DROP FUNCTION IF EXISTS areaLineEllipticalArc;

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
 * This function computes the area bounded by the line segment connecting
 * the arc endpoints and the ellipse.
 * e_a      : the semi-major axis [arcsec]
 * e_b      : the semi-minor axis [in arc]
 * theta_0  : startpoint of arc (in radians in range [-pi, pi])
 * theta_1  : endpoint of arc (in radians in range [-pi, pi])
 * We assume both theta's are set properly, so we 
 * do not have to reorder them.
 * 
 * area     : area of the elliptical sector [arcsec^2]
 */
CREATE FUNCTION areaLineEllipticalArc(e_a DOUBLE
                                     ,e_b DOUBLE
                                     ,e_theta_0 DOUBLE
                                     ,e_theta_1 DOUBLE
                                     ,c_theta_0 DOUBLE
                                     ,c_theta_1 DOUBLE
                                     ) RETURNS DOUBLE 
DETERMINISTIC 
BEGIN

  /**
   * Check the arc for crossing the negative y-axis,
   * if so we set theta_1 to theta_1 + 2pi.
   */
  IF e_theta_1 < e_theta_0 THEN
    /* In this case we have negative y crossing */
    SET e_theta_1 = e_theta_1 + 2 * PI();
    SET c_theta_1 = c_theta_1 + 2 * PI();
  END IF;

  /**
   * Now we check if the area spans more than half the elliptical area
   * (i.e. theta_1 - theta_0 > PI()), in which case we have to add 
   * the triangular area, otherwise we subtract it.
   */
  IF e_theta_1 - e_theta_0 > PI() THEN
    RETURN areaEllipticalSector(e_a, e_b, e_theta_0, e_theta_1)
           +
           areaTriangleInEllipse(e_a, e_b, c_theta_0, c_theta_1)
           ;
  ELSE 
    RETURN areaEllipticalSector(e_a, e_b, e_theta_0, e_theta_1)
           -
           areaTriangleInEllipse(e_a, e_b, c_theta_0, c_theta_1)
           ;
  END IF;

END;
//

DELIMITER ;
