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

CREATE FUNCTION doIntersectElls(ie1_ra double precision
                               ,ie1_decl double precision
                               ,ie1_ra_err double precision
                               ,ie1_decl_err double precision
                               ,ie2_ra double precision
                               ,ie2_decl double precision
                               ,ie2_ra_err double precision
                               ,ie2_decl_err double precision) RETURNS BOOLEAN as $$
  DECLARE ready BOOLEAN;
  DECLARE intersection BOOLEAN;  
  
  DECLARE e1_a double precision;
  DECLARE e1_b double precision;
  DECLARE e1_pa double precision;
  DECLARE e2_a double precision;
  DECLARE e2_b double precision;
  DECLARE e2_pa double precision;

  DECLARE theta_rot double precision;
  DECLARE e2_phi double precision;

  DECLARE e1_q1 double precision;
  DECLARE e1_q3 double precision;
  DECLARE e1_q6 double precision;

  DECLARE distance double precision;
  DECLARE e2_h double precision;
  DECLARE e2_k double precision;
  DECLARE e2_h_acc double precision;
  DECLARE e2_k_acc double precision;
  DECLARE e2_q1 double precision;
  DECLARE e2_q2 double precision;
  DECLARE e2_q3 double precision;
  DECLARE e2_q4 double precision;
  DECLARE e2_q5 double precision;
  DECLARE e2_q6 double precision;

  DECLARE v0 double precision;
  DECLARE v1 double precision;
  DECLARE v2 double precision;
  DECLARE v3 double precision;
  DECLARE v4 double precision;
  DECLARE v5 double precision;
  DECLARE v6 double precision;
  DECLARE v7 double precision;
  DECLARE v8 double precision;

  DECLARE alpha0 double precision;
  DECLARE alpha1 double precision;
  DECLARE alpha2 double precision;
  DECLARE alpha3 double precision;
  DECLARE alpha4 double precision;

  DECLARE delta0 double precision;
  DECLARE delta1 double precision;
  DECLARE delta2 double precision;
  DECLARE eta0 double precision;
  DECLARE eta1 double precision;
  DECLARE vartheta0 double precision;
  
  DECLARE s_f0 INT;
  DECLARE s_f1 INT;
  DECLARE s_f2 INT;
  DECLARE s_f3 INT;
  DECLARE s_f4 INT;

  DECLARE sign_change_neg INT;
  DECLARE sign_change_pos INT;
  DECLARE Nroots INT;
BEGIN

  ready := FALSE;
  intersection := FALSE;
  
  /**
   * We convert from degrees to arcseconds
   */
  e1_a := 3600 * SQL_MAX(ie1_ra_err, ie1_decl_err);
  e1_b := 3600 * SQL_MIN(ie1_ra_err, ie1_decl_err);
  IF ie1_ra_err > ie1_decl_err THEN
    e1_pa := 90;
  ELSE 
    e1_pa := 0;
  END IF;
  e2_a := 3600 * SQL_MAX(ie2_ra_err, ie2_decl_err);
  e2_b := 3600 * SQL_MIN(ie2_ra_err, ie2_decl_err);
  IF ie2_ra_err > ie2_decl_err THEN
    e2_pa := 90;
  ELSE 
    e2_pa := 0;
  END IF;

  e2_h := 3600 * (ie1_ra - ie2_ra);
  e2_k := 3600 * (ie2_decl - ie1_decl);

  theta_rot := radians(e1_pa - 90);
  e2_phi := radians(e2_pa - e1_pa);

  e2_h_acc :=  e2_h * COS(theta_rot) + e2_k * SIN(theta_rot);
  e2_k_acc := -e2_h * SIN(theta_rot) + e2_k * COS(theta_rot);

  /* We drop the _acc suffix */
  e2_h := e2_h_acc;
  e2_k := e2_k_acc;

  /** 
   * These tests can be executed immediately, to know
   * whether one there is separation or containment.
   */
  distance := SQRT(e2_h * e2_h + e2_k * e2_k);
  IF distance > (e1_a + e2_a) THEN
    intersection := FALSE;
    ready := TRUE;
  END IF;

  IF ready = FALSE THEN
    IF distance <= (e1_b + e2_b) THEN
      intersection := TRUE;
      ready := TRUE;
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

    e1_q1 := e1_a * e1_a;
    e1_q6 := e1_b * e1_b;
    e1_q3 := -e1_q1 * e1_q6;

    e2_q1 := e2_a * e2_a * COS(e2_phi) * COS(e2_phi) 
                + e2_b * e2_b * SIN(e2_phi) * SIN(e2_phi);
    e2_q6 := e2_a * e2_a * SIN(e2_phi) * SIN(e2_phi)
                + e2_b * e2_b * COS(e2_phi) * COS(e2_phi);
    e2_q4 := (e2_b * e2_b - e2_a * e2_a) * SIN(2 * e2_phi);
    e2_q2 := -2 * e2_k * e2_q1 - e2_h * e2_q4;
    e2_q3 := e2_h * e2_h * e2_q6 + e2_k * e2_k * e2_q1 
                + e2_h * e2_k * e2_q4 - e2_a * e2_a * e2_b * e2_b;
    e2_q5 := -2 * e2_h * e2_q6 - e2_k * e2_q4;

    v0 := e1_q6 * e2_q4;
    v1 := e1_q6 * e2_q1 - e2_q6 * e1_q1;
    v2 := e1_q6 * e2_q5;
    v3 := e1_q6 * e2_q2;
    v4 := e1_q6 * e2_q3 - e2_q6 * e1_q3;
    v5 := -e2_q4 * e1_q1;
    v6 := -e2_q4 * e1_q3;
    v7 := e1_q1 * e2_q5;
    v8 := -e2_q5 * e1_q3;

    /**
     * The coefficients of the Bezout determinant
     */
    alpha0 := v2 * v8 - v4 * v4;
    alpha1 := v0 * v8 + v2 * v6 - 2 * v3 * v4;
    alpha2 := v0 * v6 - v2 * v7 - v3 * v3 - 2 * v1 * v4;
    alpha3 := -v0 * v7 + v2 * v5 - 2 * v1 * v3;
    alpha4 := v0 * v5 - v1 * v1;

    alpha0 := alpha0 / alpha4;
    alpha1 := alpha1 / alpha4;
    alpha2 := alpha2 / alpha4;
    alpha3 := alpha3 / alpha4;
    alpha4 := 1;

    delta2 := ((3 * alpha3 * alpha3) / (16 * alpha4)) - (alpha2/2);
    delta1 := ((alpha2 * alpha3) / (8 * alpha4)) - ((3 * alpha1)/4);
    delta0 := (alpha1 * alpha3 / (16 * alpha4)) - alpha0;
    eta1 := (delta1/delta2) * 
               (3 * alpha3 - (4 * (alpha4 * delta1 / delta2))) - 
               (2 * alpha2 - (4 * (alpha4 * delta0 / delta2))); 
    eta0 := (delta0/delta2) * 
               (3 * alpha3 - (4 * (alpha4 * delta1 / delta2))) - 
               (3 * alpha3);
    vartheta0 := (eta0/eta1) * 
                    (delta1 - (eta0 * delta2 / eta1)) - delta0;

    /**
     * Determine sign for -infty
     */
    s_f0 := SIGN(alpha4);
    s_f1 := SIGN((-4*alpha4));
    s_f2 := SIGN(delta2);
    s_f3 := SIGN(-eta1);
    s_f4 := SIGN(vartheta0);

    sign_change_neg := 0;
  
    IF s_f0 * s_f1 < 0 THEN
      sign_change_neg := sign_change_neg + 1;
    END IF;
    IF s_f1 * s_f2 < 0 THEN
      sign_change_neg := sign_change_neg + 1;
    END IF;
    IF s_f2 * s_f3 < 0 THEN
      sign_change_neg := sign_change_neg + 1;
    END IF;
    IF s_f3 * s_f4 < 0 THEN
      sign_change_neg := sign_change_neg + 1;
    END IF;

    /**
     * Determine sign for +infty
     */
    s_f0 := SIGN(alpha4);
    s_f1 := SIGN((4*alpha4));
    s_f2 := SIGN(delta2);
    s_f3 := SIGN(eta1);
    s_f4 := SIGN(vartheta0);

    sign_change_pos := 0;
  
    IF s_f0 * s_f1 < 0 THEN
      sign_change_pos := sign_change_pos + 1;
    END IF;
    IF s_f1 * s_f2 < 0 THEN
      sign_change_pos := sign_change_pos + 1;
    END IF;
    IF s_f2 * s_f3 < 0 THEN
      sign_change_pos := sign_change_pos + 1;
    END IF;
    IF s_f3 * s_f4 < 0 THEN
      sign_change_pos := sign_change_pos + 1;
    END IF;

    Nroots := sign_change_neg - sign_change_pos;
    IF Nroots > 0 THEN
      intersection := TRUE;
    ELSE
      intersection := FALSE;
    END IF;
  
  END IF; 
  
  RETURN intersection;

END;
$$ language plpgsql;
