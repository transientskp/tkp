DROP FUNCTION IF EXISTS getQuarticNumberRoots;

DELIMITER //

/**
 * This boolean functions determines if two ellipses intersect.
 * A cartesian coordinate system is used for this.
 * The arguments for ellipse 1 (e1_*) are the semi-major and 
 * -minor axes (a, b). It is ASSUMED that the centre is at (0,0) and
 * that the x-axis is aligned with the major axis (phi = 0).
 * The input arguments for ellipse 2 (e2_*) are its centre (h,k)
 * semi-major and -minor axes (a, b), and rotation angle phi (phi
 * is counterclockwise oriented, from +x to +y).
 */
CREATE FUNCTION getQuarticNumberRoots(ialpha4 DOUBLE
                                     ,ialpha3 DOUBLE
                                     ,ialpha2 DOUBLE
                                     ,ialpha1 DOUBLE
                                     ,ialpha0 DOUBLE
                                     ) RETURNS INT

BEGIN

  DECLARE alpha0, alpha1, alpha2, alpha3, alpha4 DOUBLE;
  DECLARE delta0, delta1, delta2, eta0, eta1, vartheta0 DOUBLE;
  
  DECLARE s_f0, s_f1, s_f2, s_f3, s_f4 INT DEFAULT NULL;
  DECLARE sign_change_neg, sign_change_pos, Nroots INT DEFAULT NULL;

  SET alpha4 = ialpha4;
  SET alpha3 = ialpha3;
  SET alpha2 = ialpha2; 
  SET alpha1 = ialpha1;
  SET alpha0 = ialpha0;

  SET alpha0 = alpha0 / alpha4;
  SET alpha1 = alpha1 / alpha4;
  SET alpha2 = alpha2 / alpha4;
  SET alpha3 = alpha3 / alpha4;
  SET alpha4 = 1;

  SET delta2 = ((3 * alpha3 * alpha3) / (16 * alpha4)) - (alpha2/2);
  SET delta1 = ((alpha2 * alpha3) / (8 * alpha4)) - ((3 * alpha1)/4);
  SET delta0 = (alpha1 * alpha3 / (16 * alpha4)) - alpha0;
  SET eta1 = (delta1/delta2) * 
             (3 * alpha3 - (4 * (alpha4 * delta1 / delta2))) - 
             (2 * alpha2 - (4 * (alpha4 * delta0 / delta2))); 
  SET eta0 = (delta0/delta2) * 
             (3 * alpha3 - (4 * (alpha4 * delta1 / delta2))) - 
             alpha1;
  SET vartheta0 = (eta0/eta1) * 
                  (delta1 - (eta0 * delta2 / eta1)) - delta0;

  /**
   * Determine sign for -infty
   */
  SET s_f0 = SIGN(alpha4);
  SET s_f1 = SIGN((-4*alpha4));
  SET s_f2 = SIGN(delta2);
  SET s_f3 = SIGN(-eta1);
  SET s_f4 = SIGN(vartheta0);

  SET sign_change_neg = 0;
  
  IF s_f0 * s_f1 < 0 THEN
    SET sign_change_neg = sign_change_neg + 1;
  END IF;
  IF s_f1 * s_f2 < 0 THEN
    SET sign_change_neg = sign_change_neg + 1;
  END IF;
  IF s_f2 * s_f3 < 0 THEN
    SET sign_change_neg = sign_change_neg + 1;
  END IF;
  IF s_f3 * s_f4 < 0 THEN
    SET sign_change_neg = sign_change_neg + 1;
  END IF;

  /**
   * Determine sign for +infty
   */
  SET s_f0 = SIGN(alpha4);
  SET s_f1 = SIGN((4*alpha4));
  SET s_f2 = SIGN(delta2);
  SET s_f3 = SIGN(eta1);
  SET s_f4 = SIGN(vartheta0);

  SET sign_change_pos = 0;
  
  IF s_f0 * s_f1 < 0 THEN
    SET sign_change_pos = sign_change_pos + 1;
  END IF;
  IF s_f1 * s_f2 < 0 THEN
    SET sign_change_pos = sign_change_pos + 1;
  END IF;
  IF s_f2 * s_f3 < 0 THEN
    SET sign_change_pos = sign_change_pos + 1;
  END IF;
  IF s_f3 * s_f4 < 0 THEN
    SET sign_change_pos = sign_change_pos + 1;
  END IF;

  SET Nroots = sign_change_neg - sign_change_pos;
  
  RETURN Nroots;

END;
//

DELIMITER ;
