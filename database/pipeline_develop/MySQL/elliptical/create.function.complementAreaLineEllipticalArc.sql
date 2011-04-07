DROP FUNCTION IF EXISTS complementAreaLineEllipticalArc;

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
 * This function computes the area of the elliptical sector,
 * the region bound by an elliptical arc and the line segments 
 * containing the origin and the endpoints of the arc.
 * e_a      : the semi-major axis [arcsec]
 * e_b      : the semi-minor axis [arcsec]
 * theta_0  : startpoint of arc (in radians in range [-pi, pi])
 * theta_1  : endpoint of arc (in radians in range [-pi, pi])
 * We assume both theta's are set properly, so we 
 * do not have to reorder them.
 * 
 * area     : area of the elliptical sector [arcsec^2]
 */
CREATE FUNCTION complementAreaLineEllipticalArc(e_a DOUBLE
                                               ,e_b DOUBLE
                                               ,e_theta_0 DOUBLE
                                               ,e_theta_1 DOUBLE
                                               ,c_theta_0 DOUBLE
                                               ,c_theta_1 DOUBLE
                                               ) RETURNS DOUBLE 
DETERMINISTIC 
BEGIN

  /**
   * Everything is taken care of in the areaLineEllipticalArc function,
   * so we only have to subtract it from the total area of the ellipse
   */
    
  RETURN PI() * e_a * e_b 
         - areaLineEllipticalArc(e_a, e_b, e_theta_0, e_theta_1, c_theta_0, c_theta_1);

END;
//

DELIMITER ;
