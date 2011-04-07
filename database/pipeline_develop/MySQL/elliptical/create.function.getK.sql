DROP FUNCTION IF EXISTS getK;

DELIMITER //

/**
 * Based on D. Eberly's "The Area Of Intersecting Ellipses",
 * http://www.geometrictools.com/documentation/.
 *
 * This is the inverse tangent function that correspnds to 
 * the angle at which z (z := TAN(theta) was evaluated,
 * so k is dependent on theta.
 * This function is used to calculate an elliptical sector.
 *
 * k = -1   : for theta BETWEEN (-3 PI() / 2, -PI() / 2)
 * k = 0    : for theta BETWEEN (-PI() / 2, PI() / 2)
 * k = 1    : for theta BETWEEN (PI() / 2, 3 PI() / 2)
 * theta    : the angle that is to be evaluated (in radians)
 *
 */
CREATE FUNCTION getK(itheta DOUBLE) RETURNS INT 
DETERMINISTIC 
BEGIN

  /**
   * NOTE: The cases where theta = pi/2 + k pi are taken care of
   * in the areaEllipticalSector() function itself (by adding or 
   * subtracting an epsilon value of theta, so forcing it to be in
   * of the cases from below.
   */
  CASE 
    WHEN itheta > (-3 * PI() / 2) AND itheta < (-PI() / 2) THEN
      RETURN -1;
    WHEN itheta > (-PI() / 2) AND itheta < (PI() / 2) THEN
      RETURN 0;
    WHEN itheta > (PI() / 2) AND itheta < (3 * PI() / 2) THEN
      RETURN 1;
    WHEN itheta > (3 * PI() / 2) AND itheta < (5 * PI() / 2) THEN
      RETURN 2;
    WHEN itheta > (5 * PI() / 2) AND itheta < (7 * PI() / 2) THEN
      RETURN 3;
    ELSE
      RETURN NULL;
  END CASE;

END;
//

DELIMITER ;
