DROP FUNCTION IF EXISTS areaEllipticalSector;

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
 *            the angle is defined as from the center of the
 *            ellipse to the intersection point on the ellipse:
 *            x = r cos theta
 *            y = r sin theta
 *            NOTE that this is different from calculation the 
 *            triangular area.
 * theta_1  : endpoint of arc (in radians in range [-pi, pi])
 *            See theta_0 for definition
 * We assume both theta's are set properly, so we 
 * do not have to reorder them.
 * 
 * area     : area of the elliptical sector [arcsec^2]
 */
CREATE FUNCTION areaEllipticalSector(e_a DOUBLE
                                    ,e_b DOUBLE
                                    ,e_theta_0 DOUBLE
                                    ,e_theta_1 DOUBLE
                                    ) RETURNS DOUBLE 
DETERMINISTIC 
BEGIN

  DECLARE epsilon DOUBLE DEFAULT 1E-15;
  
  /**
   * Check the arc for crossing the negative y-axis,
   * if so we set theta_1 to theta_1 + 2pi.
   */
  IF e_theta_1 < e_theta_0 THEN
    SET e_theta_1 = e_theta_1 + 2 * PI();
  END IF;

  /**
   * Here we catch the cases where one of the theta's = pi/2 + k pi.
   * (These cases are not handled in getK().)
   * theta_0 is always the start point of the arc, so we add epsilon
   * theta_1 is always the end point of the arc, so we subtract epsilon
   */
  IF (e_theta_0 - PI() / 2) % PI() = 0 THEN
      SET e_theta_0 = e_theta_0 + epsilon;
  END IF;
  IF (e_theta_1 - PI() / 2) % PI() = 0 THEN
      SET e_theta_1 = e_theta_1 - epsilon;
  END IF;

  RETURN e_a * e_b * 
         (ATAN_k(getK(e_theta_1), e_a * TAN(e_theta_1) / e_b) 
         - ATAN_k(getK(e_theta_0), e_a * TAN(e_theta_0) / e_b)
         )
         / 2;

END;
//

DELIMITER ;
