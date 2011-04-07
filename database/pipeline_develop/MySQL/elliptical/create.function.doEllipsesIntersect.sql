DROP FUNCTION IF EXISTS doEllipsesIntersect;

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
CREATE FUNCTION doEllipsesIntersect(ie1_a DOUBLE
                                   ,ie1_b DOUBLE
                                   ,ie2_h DOUBLE
                                   ,ie2_k DOUBLE
                                   ,ie2_a DOUBLE
                                   ,ie2_b DOUBLE
                                   ,ie2_phi DOUBLE
                                   ) RETURNS BOOLEAN

BEGIN
  DECLARE ready, doIntersect BOOLEAN DEFAULT FALSE;

  DECLARE e1_q1, e1_q3, e1_q6 DOUBLE;
  DECLARE e2_phi, e2_q1, e2_q2, e2_q3, e2_q4, e2_q5, e2_q6 DOUBLE;
  DECLARE distance DOUBLE DEFAULT NULL;

  DECLARE v0, v1, v2, v3, v4, v5, v6, v7, v8 DOUBLE;
  DECLARE alpha0, alpha1, alpha2, alpha3, alpha4 DOUBLE;
  DECLARE delta0, delta1, delta2, eta0, eta1, vartheta0 DOUBLE;
  
  DECLARE s_f0, s_f1, s_f2, s_f3, s_f4 INT DEFAULT NULL;
  DECLARE sign_change_neg, sign_change_pos, Nroots INT DEFAULT NULL;

  /**
   * For Ellipse 1 we should have the centre at (x,y) = (0,0), and 
   * the major axis aligned with the x-axis (e1_phi = 0)
   */
  SET e2_phi = RADIANS(ie2_phi);

  /** 
   * These tests can be executed immediately, to know
   * whether one there is separation or containment.
   */
  SET distance = SQRT(ie2_h * ie2_h + ie2_k * ie2_k);
  IF distance > (ie1_a + ie2_a) THEN
    SET doIntersect = FALSE;
    SET ready = TRUE;
  END IF;

  IF ready = FALSE THEN
    IF distance <= (ie1_b + ie2_b) THEN
      SET doIntersect = TRUE;
      SET ready = TRUE;
    END IF;
  END IF;

  /**
   * If the ellipses are to far there is separation and 
   * the ellipses do not intersection.
   * If the ellipses are to close there is intersection
   * and we are done as well.
   * The other cases we have to evaluate.
   */
  IF (ready = FALSE) THEN

    SET e1_q1 = ie1_a * ie1_a;
    SET e1_q6 = ie1_b * ie1_b;
    SET e1_q3 = -e1_q1 * e1_q6;

    SET e2_q1 =   ie2_a * ie2_a * COS(e2_phi) * COS(e2_phi) 
                + ie2_b * ie2_b * SIN(e2_phi) * SIN(e2_phi);
    SET e2_q6 =   ie2_a * ie2_a * SIN(e2_phi) * SIN(e2_phi)
                + ie2_b * ie2_b * COS(e2_phi) * COS(e2_phi);
    SET e2_q4 = (ie2_b * ie2_b - ie2_a * ie2_a) * SIN(2 * e2_phi);
    SET e2_q2 = -2 * ie2_k * e2_q1 - ie2_h * e2_q4;
    SET e2_q3 =   ie2_h * ie2_h * e2_q6 
                + ie2_k * ie2_k * e2_q1 
                + ie2_h * ie2_k * e2_q4 
                - ie2_a * ie2_a * ie2_b * ie2_b;
    SET e2_q5 = -2 * ie2_h * e2_q6 - ie2_k * e2_q4;

    SET v0 = e1_q6 * e2_q4;
    SET v1 = e1_q6 * e2_q1 - e2_q6 * e1_q1;
    SET v2 = e1_q6 * e2_q5;
    SET v3 = e1_q6 * e2_q2;
    SET v4 = e1_q6 * e2_q3 - e2_q6 * e1_q3;
    SET v5 = -e2_q4 * e1_q1;
    SET v6 = -e2_q4 * e1_q3;
    SET v7 = e1_q1 * e2_q5;
    SET v8 = -e2_q5 * e1_q3;

    /**
     * The coefficients of the Bezout determinant
     */
    SET alpha0 = v2 * v8 - v4 * v4;
    SET alpha1 = v0 * v8 + v2 * v6 - 2 * v3 * v4;
    SET alpha2 = v0 * v6 - v2 * v7 - v3 * v3 - 2 * v1 * v4;
    SET alpha3 = -v0 * v7 + v2 * v5 - 2 * v1 * v3;
    SET alpha4 = v0 * v5 - v1 * v1;

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
    IF Nroots > 0 THEN
      SET doIntersect = TRUE;
    ELSE
      SET doIntersect = FALSE;
    END IF;
  
  END IF; 
  
  RETURN doIntersect;

END;
//

DELIMITER ;
