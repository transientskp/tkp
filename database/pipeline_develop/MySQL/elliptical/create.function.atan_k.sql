DROP FUNCTION IF EXISTS atan_k;

DELIMITER //

/**
 * 
 * Based on D. Eberly's "The Area Of Intersecting Ellipses",
 * http://www.geometrictools.com/documentation/.
 *
 * This is the inverse tangent function that correspnds to 
 * the angle at which z (z := TAN(theta)) was evaluated,
 * so k is dependent on theta.
 * This function is used to calculate an elliptical sector.
 *
 * k = -1   : for theta BETWEEN (-3 PI() / 2, -PI() / 2)
 * k = 0    : for theta BETWEEN (-PI() / 2, PI() / 2)
 * k = 1    : for theta BETWEEN (PI() / 2, 3 PI() / 2)
 * z        : is TAN(theta)
 *
 */
CREATE FUNCTION atan_k(k INT
                      ,z DOUBLE
                      ) RETURNS DOUBLE 
DETERMINISTIC 
BEGIN

  RETURN ATAN(z) + k * PI();

END;
//

DELIMITER ;
