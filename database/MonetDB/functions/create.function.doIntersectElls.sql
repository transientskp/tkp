--DROP FUNCTION doIntersectElls;

/**
 * This boolean functions determines if two ellipses intersection.
 * The arguments for for ellipse 1 (e1_*) are the centre (ra,decl)
 * and the semi-major and semi-minor axes (ra_err,decl_err). All
 * units are in degrees.
 * The input should be typical the source position in ra and dec,
 * and the errors on the position (in degrees). 
 * It is assumed that a preselection is done so that the two ellipses
 * are close together, and that the ellipses are either alligned or
 * perpendicular oriented wrt each other. 
 * No ra-inflation has to be taken into account.
 */

CREATE FUNCTION doIntersectElls(ie1_ra DOUBLE
                               ,ie1_decl DOUBLE
                               ,ie1_ra_err DOUBLE
                               ,ie1_decl_err DOUBLE
                               ,ie2_ra DOUBLE
                               ,ie2_decl DOUBLE
                               ,ie2_ra_err DOUBLE
                               ,ie2_decl_err DOUBLE) RETURNS BOOLEAN 
BEGIN
  DECLARE ready BOOLEAN;
  DECLARE intersection BOOLEAN;  
  
  DECLARE e1_a DOUBLE;
  DECLARE e1_b DOUBLE;
  DECLARE e1_pa DOUBLE;
  DECLARE e2_a DOUBLE;
  DECLARE e2_b DOUBLE;
  DECLARE e2_pa DOUBLE;

  DECLARE theta_rot DOUBLE;
  DECLARE e2_phi DOUBLE;

  DECLARE e1_q1 DOUBLE;
  DECLARE e1_q3 DOUBLE;
  DECLARE e1_q6 DOUBLE;

  DECLARE distance DOUBLE;
  DECLARE e2_h DOUBLE;
  DECLARE e2_k DOUBLE;
  DECLARE e2_h_acc DOUBLE;
  DECLARE e2_k_acc DOUBLE;
  DECLARE e2_q1 DOUBLE;
  DECLARE e2_q2 DOUBLE;
  DECLARE e2_q3 DOUBLE;
  DECLARE e2_q4 DOUBLE;
  DECLARE e2_q5 DOUBLE;
  DECLARE e2_q6 DOUBLE;

  DECLARE v0 DOUBLE;
  DECLARE v1 DOUBLE;
  DECLARE v2 DOUBLE;
  DECLARE v3 DOUBLE;
  DECLARE v4 DOUBLE;
  DECLARE v5 DOUBLE;
  DECLARE v6 DOUBLE;
  DECLARE v7 DOUBLE;
  DECLARE v8 DOUBLE;

  DECLARE alpha0 DOUBLE;
  DECLARE alpha1 DOUBLE;
  DECLARE alpha2 DOUBLE;
  DECLARE alpha3 DOUBLE;
  DECLARE alpha4 DOUBLE;

  DECLARE delta0 DOUBLE;
  DECLARE delta1 DOUBLE;
  DECLARE delta2 DOUBLE;
  DECLARE eta0 DOUBLE;
  DECLARE eta1 DOUBLE;
  DECLARE vartheta0 DOUBLE;
  
  DECLARE s_f0 INT;
  DECLARE s_f1 INT;
  DECLARE s_f2 INT;
  DECLARE s_f3 INT;
  DECLARE s_f4 INT;

  DECLARE sign_change_neg INT;
  DECLARE sign_change_pos INT;
  DECLARE Nroots INT;

  SET ready = FALSE;
  SET intersection = FALSE;
  
  /**
   * We convert from degrees to arcseconds
   */
  SET e1_a = 3600 * SQL_MAX(ie1_ra_err, ie1_decl_err);
  SET e1_b = 3600 * SQL_MIN(ie1_ra_err, ie1_decl_err);
  IF ie1_ra_err > ie1_decl_err THEN
    SET e1_pa = 90;
  ELSE 
    SET e1_pa = 0;
  END IF;
  SET e2_a = 3600 * SQL_MAX(ie2_ra_err, ie2_decl_err);
  SET e2_b = 3600 * SQL_MIN(ie2_ra_err, ie2_decl_err);
  IF ie2_ra_err > ie2_decl_err THEN
    SET e2_pa = 90;
  ELSE 
    SET e2_pa = 0;
  END IF;

  SET e2_h = 3600 * (ie1_ra - ie2_ra);
  SET e2_k = 3600 * (ie2_decl - ie1_decl);

  SET theta_rot = radians(e1_pa - 90);
  SET e2_phi = radians(e2_pa - e1_pa);

  SET e2_h_acc =  e2_h * COS(theta_rot) + e2_k * SIN(theta_rot);
  SET e2_k_acc = -e2_h * SIN(theta_rot) + e2_k * COS(theta_rot);

  /* We drop the _acc suffix */
  SET e2_h = e2_h_acc;
  SET e2_k = e2_k_acc;

  /** 
   * These tests can be executed immediately, to know
   * whether one there is separation or containment.
   */
  SET distance = SQRT(e2_h * e2_h + e2_k * e2_k);
  IF distance > (e1_a + e2_a) THEN
    SET intersection = FALSE;
    SET ready = TRUE;
  END IF;

  IF ready = FALSE THEN
    IF distance <= (e1_b + e2_b) THEN
      SET intersection = TRUE;
      SET ready = TRUE;
    END IF;
  END IF;

  /**
   * If the ellipses are to far there is separation and 
   * the ellipses do not intersection.
   * If the ellipses are to close there is intersectionion 
   * and we are done as well.
   * The other cases we have to evaluate.
   */
  IF (ready = FALSE) THEN

    SET e1_q1 = e1_a * e1_a;
    SET e1_q6 = e1_b * e1_b;
    SET e1_q3 = -e1_q1 * e1_q6;

    SET e2_q1 = e2_a * e2_a * COS(e2_phi) * COS(e2_phi) 
                + e2_b * e2_b * SIN(e2_phi) * SIN(e2_phi);
    SET e2_q6 = e2_a * e2_a * SIN(e2_phi) * SIN(e2_phi)
                + e2_b * e2_b * COS(e2_phi) * COS(e2_phi);
    SET e2_q4 = (e2_b * e2_b - e2_a * e2_a) * SIN(2 * e2_phi);
    SET e2_q2 = -2 * e2_k * e2_q1 - e2_h * e2_q4;
    SET e2_q3 = e2_h * e2_h * e2_q6 + e2_k * e2_k * e2_q1 
                + e2_h * e2_k * e2_q4 - e2_a * e2_a * e2_b * e2_b;
    SET e2_q5 = -2 * e2_h * e2_q6 - e2_k * e2_q4;

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
               (3 * alpha3);
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
      SET intersection = TRUE;
    ELSE
      SET intersection = FALSE;
    END IF;
  
  END IF; 
  
  RETURN intersection;

END;
