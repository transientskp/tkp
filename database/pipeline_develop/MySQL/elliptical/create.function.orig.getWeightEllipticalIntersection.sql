DROP FUNCTION IF EXISTS getWeightEllipticalIntersection;

DELIMITER //

/**
 * This boolean functions determines if two ellipses intersect.
 * A carthesian coordinate system is used for this.
 * The input arguments for ellipse 1 (e1_*) are the semi-major and
 * -minor axes (a, b). It is ASSUMED that its center is at (0,0) and
 * that the x-axis is aligned with the major axis.
 * In this coordinate system, the input arguments for ellipse 2 (e2_*)
 * are its centre C2 = (h,k), semi-major and -minor axes (a, b), and 
 * the rotation angle phi (phi is counterclockwise oriented, 
 * going from +x to +y), which is in [-pi, pi].
 *
 * Intersection points are named P0, P1, P2, P3, sorted according to 
 * ascending angle in the [-pi, pi] domain.
 * E1, theta_i   : the angle from the centre of E1 to Pi
 *
 * E2, beta_i   : the angle between the vector (Pi - C2) and the x-axis,
 *                also in [-pi, pi].
 * E2, theta_i  : the angle between the vector (Pi - C2) and the semi-
 *                major axis of E2, also in [-pi, pi].
 *                 
 * The theta angles are used to compute the areas of intersection.
 *
 * TODO: 
 * (1) The case when we have two intersection points (2 roots) and one
 * ellipse in inside the other
 *                 
 */
CREATE FUNCTION getWeightEllipticalIntersection(ie1_a DOUBLE
                                               ,ie1_b DOUBLE
                                               ,ie2_h DOUBLE
                                               ,ie2_k DOUBLE
                                               ,ie2_a DOUBLE
                                               ,ie2_b DOUBLE
                                               ,ie2_phi DOUBLE
                                               ) RETURNS DOUBLE 

BEGIN
  DECLARE ready, doIntersect, doContain BOOLEAN DEFAULT FALSE;

  DECLARE e1_q1, e1_q3, e1_q6 DOUBLE;
  DECLARE e2_phi, e2_q1, e2_q2, e2_q3, e2_q4, e2_q5, e2_q6 DOUBLE;
  DECLARE distance DOUBLE DEFAULT NULL;

  DECLARE v0, v1, v2, v3, v4, v5, v6, v7, v8 DOUBLE;
  DECLARE alpha0, alpha1, alpha2, alpha3, alpha4 DOUBLE;
  DECLARE delta0, delta1, delta2, eta0, eta1, vartheta0 DOUBLE;
  
  DECLARE s_f0, s_f1, s_f2, s_f3, s_f4 INT DEFAULT NULL;
  DECLARE sign_change_neg, sign_change_pos, Nroots INT DEFAULT NULL;

  DECLARE x1_arg, x1, x2, y1, y2, y3, y4  DOUBLE;
  DECLARE y1_x1, y1_x2, y2_x1, y2_x2, y3_x1, y3_x2, y4_x1, y4_x2 DOUBLE;
  DECLARE abc_a, abc_b, abc_c, abc_D DOUBLE;
  DECLARE eps_sols DOUBLE DEFAULT 1E-05;
  DECLARE nPoints INT;
  DECLARE Q0_x, Q0_y, Q1_x, Q1_y, Q2_x, Q2_y, Q3_x, Q3_y DOUBLE;
  DECLARE R0_x, R0_y, R1_x, R1_y, R2_x, R2_y, R3_x, R3_y DOUBLE;

  DECLARE c1_angle_0, c1_angle_1, c1_angle_2, c1_angle_3 DOUBLE;
  DECLARE c2_beta_0, c2_beta_1, c2_beta_2, c2_beta_3 DOUBLE;
  DECLARE P0_x, P0_y, P1_x, P1_y, P2_x, P2_y, P3_x, P3_y, slope DOUBLE;
  DECLARE m, c DOUBLE;
  DECLARE C1_above, C2_above BOOLEAN;
  DECLARE c1_theta_0, c1_theta_1, c1_theta_2, c1_theta_3 DOUBLE;
  DECLARE e1_theta_0, e1_theta_1, e1_theta_2, e1_theta_3 DOUBLE;
  DECLARE c2_theta_0, c2_theta_1, c2_theta_2, c2_theta_3 DOUBLE;
  DECLARE e2_theta_0, e2_theta_1, e2_theta_2, e2_theta_3 DOUBLE;
  
  DECLARE e1_m_0, e1_m_1, e1_m_2, e2_m_0, e2_m_1, e2_m_2 DOUBLE;
  DECLARE e2_a_m_x, e2_a_m_y, e2_b_m_x, e2_b_m_y DOUBLE;
  DECLARE e2_P0_vec_x, e2_P0_vec_y, e2_P1_vec_x, e2_P1_vec_y DOUBLE;
  DECLARE e2_P2_vec_x, e2_P2_vec_y, e2_P3_vec_x, e2_P3_vec_y DOUBLE;
  DECLARE e2_P0_proj_x, e2_P0_proj_y, e2_P1_proj_x, e2_P1_proj_y DOUBLE;
  DECLARE e2_P2_proj_x, e2_P2_proj_y, e2_P3_proj_x, e2_P3_proj_y DOUBLE;
  DECLARE e_area, e_triangles, least_e_area DOUBLE;
  DECLARE ogeval INT;

  DECLARE weight DOUBLE;

  /**
   * For Ellipse 1 we should have (x,y) = (0,0), and pa = 90 => phi = 0. 
   * We constrain ellipse 2 by setting the angle of rotation according
   * to the x-axis to (-pi/2, pi/2]
   */
  IF ie2_phi > 90 THEN
    SET ie2_phi = ie2_phi - 180;
  ELSE
    IF ie2_phi <= -90 THEN
      SET ie2_phi = ie2_phi + 180;
    END IF;
  END IF;
  SET e2_phi = RADIANS(ie2_phi);
  /** 
   * These tests can be executed immediately, to know
   * whether one there is separation or containment.
   */
  SET distance = SQRT(ie2_h * ie2_h + ie2_k * ie2_k);
  IF distance > (ie1_a + ie2_a) THEN
    SET doIntersect = FALSE;
    /*SET weight = -1;*/
    /* They do not intersect, we do not have to calculate roots 
     * and stuff like that*/
    SET ready = TRUE;
  END IF;

  /*IF ready = FALSE THEN
    IF distance <= (ie1_b + ie2_b) THEN
      SET doIntersect = TRUE;*/
      /* We are sure they intersect, except for the case when there
       * is containment. If not we still have to 
       * calculate the intersection area
       */
     /*SET ready = FALSE;
    END IF;
  END IF;*/


  /**
   * If the ellipses are to far there is separation and 
   * the ellipses do not doIntersect.
   * If the ellipses are to close there is doIntersection 
   * and we are done as well.
   * The other cases we have to evaluate.
   */
  IF (ready = FALSE) THEN

    SET e1_q1 = ie1_a * ie1_a;
    SET e1_q6 = ie1_b * ie1_b;
    SET e1_q3 = -e1_q1 * e1_q6;

    /* We should check value < 1e-14 and set them to 0 */
    SET e2_q1 = ie2_a * ie2_a * COS(e2_phi) * COS(e2_phi) 
                + ie2_b * ie2_b * SIN(e2_phi) * SIN(e2_phi);
    SET e2_q6 = ie2_a * ie2_a * SIN(e2_phi) * SIN(e2_phi)
                + ie2_b * ie2_b * COS(e2_phi) * COS(e2_phi);
    SET e2_q4 = (ie2_b * ie2_b - ie2_a * ie2_a) * SIN(2 * e2_phi);
    IF ABS(e2_q4) < 1E-14 THEN
      SET e2_q4 = 0;
    END IF;
    SET e2_q2 = -2 * ie2_k * e2_q1 - ie2_h * e2_q4;
    SET e2_q3 = ie2_h * ie2_h * e2_q6 + ie2_k * ie2_k * e2_q1 
                + ie2_h * ie2_k * e2_q4 - ie2_a * ie2_a * ie2_b * ie2_b;
    SET e2_q5 = -2 * ie2_h * e2_q6 - ie2_k * e2_q4;
    IF ABS(e2_q5) < 1E-14 THEN
      SET e2_q5 = 0;
    END IF;
    
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
    IF ABS(eta1) < 1E-11 THEN
      SET eta1 = 0;
    END IF;
    SET eta0 = (delta0/delta2) * 
               (3 * alpha3 - (4 * (alpha4 * delta1 / delta2))) - 
               alpha1;
    IF ABS(eta0) < 1E-11 THEN
      SET eta0 = 0;
    END IF;
    IF eta1 = 0 THEN
      SET vartheta0 = 0;
    ELSE
      SET vartheta0 = (eta0/eta1) * 
                      (delta1 - (eta0 * delta2 / eta1)) - delta0;
    END IF;

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

    /*set osign_change_neg = sign_change_neg;*/
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

    /*set osign_change_pos = sign_change_pos;*/
    
    /* Roots may be repetitive, in which case the 
     * the variable nPoints will be used
     */
    SET Nroots = sign_change_neg - sign_change_pos;
    IF Nroots > 0 THEN
      SET doIntersect = TRUE;
    ELSE
      SET doIntersect = FALSE;
      /* Below we will take care of the situation
       * when there is no intersection. Then we have
       * to determine if there is containment or separation
       */
    END IF;
  
  END IF; 
  
  /* Here we will calculate the points of intersection*/
  IF doIntersect = TRUE THEN
    IF Nroots > 0 THEN
      /* We will get the roots of the Bezout determinant */
      CALL GetQuarticRootsAlt(1,alpha3,alpha2,alpha1,alpha0
                             ,y1,y2,y3,y4);
      SET nPoints = 0;
      IF y1 IS NOT NULL THEN
        SET x1_arg = (-e1_q1 * y1 * y1 - e1_q3) / e1_q6;
        IF ABS(x1_arg) < eps_sols THEN
          SET x1_arg = 0;
        END IF;
        SET x1 = SQRT(x1_arg);
        SET x2 = -x1;
        SET abc_a = e2_q6;
        SET abc_b = e2_q4 * y1 + e2_q5;
        SET abc_c = e2_q1 * y1 * y1 + e2_q2 * y1 + e2_q3;
        IF ABS(abc_c + abc_b * x1 + abc_a * x1 * x1) < eps_sols THEN
          SET y1_x1 = x1;
          SET nPoints = nPoints + 1;
        END IF;
        IF x1 <> x2 THEN
          IF ABS(abc_c + abc_b * x2 + abc_a * x2 * x2) < eps_sols THEN
            SET y1_x2 = x2;
            SET nPoints = nPoints + 1;
          END IF;
        END IF;
      END IF;
      
      IF y2 IS NOT NULL THEN
        /*IF y2 <> y1 THEN*/
        IF ABS(y2 - y1) > 1E-6 THEN
          SET x1_arg = (-e1_q1 * y2 * y2 - e1_q3) / e1_q6;
          IF ABS(x1_arg) < eps_sols THEN
            SET x1_arg = 0;
          END IF;
          SET x1 = SQRT(x1_arg);
          SET x2 = -x1;
          SET abc_a = e2_q6;
          SET abc_b = e2_q4 * y2 + e2_q5;
          SET abc_c = e2_q1 * y2 * y2 + e2_q2 * y2 + e2_q3;
          IF ABS(abc_c + abc_b * x1 + abc_a * x1 * x1) < eps_sols THEN
            SET y2_x1 = x1; 
            SET nPoints = nPoints + 1;
          END IF;
          IF x1 <> x2 THEN
            IF ABS(abc_c + abc_b * x2 + abc_a * x2 * x2) < eps_sols THEN
              SET y2_x2 = x2;
              SET nPoints = nPoints + 1;
            END IF;
          END IF;
        END IF;
      END IF;
      
      IF y3 IS NOT NULL THEN
        /*IF y3 <> y2 THEN*/
        IF ABS(y3 - y2) > 1E-6 THEN
          /*IF y3 <> y1 THEN*/
          IF ABS(y3 - y1) > 1E-6 THEN
            SET x1_arg = (-e1_q1 * y3 * y3 - e1_q3) / e1_q6;
            IF ABS(x1_arg) < eps_sols THEN
              SET x1_arg = 0;
            END IF;
            SET x1 = SQRT(x1_arg);
            SET x2 = -x1;
            SET abc_a = e2_q6;
            SET abc_b = e2_q4 * y3 + e2_q5;
            SET abc_c = e2_q1 * y3 * y3 + e2_q2 * y3 + e2_q3;
            IF ABS(abc_c + abc_b * x1 + abc_a * x1 * x1) < eps_sols THEN
              SET y3_x1 = x1; 
              SET nPoints = nPoints + 1;
            END IF;
            IF x1 <> x2 THEN
              IF ABS(abc_c + abc_b * x2 + abc_a * x2 * x2) < eps_sols THEN
                SET y3_x2 = x2;
                SET nPoints = nPoints + 1;
              END IF;
            END IF;
          END IF;
        END IF;
      END IF;
      
      IF y4 IS NOT NULL THEN
        /*IF y4 <> y3 THEN*/
        IF ABS(y4 - y3) > 1E-6 THEN
          /*IF y4 <> y2 THEN*/
          IF ABS(y4 - y2) > 1E-6 THEN
            /*IF y4 <> y1 THEN*/
            IF ABS(y4 - y1) > 1E-6 THEN
              SET x1_arg = (-e1_q1 * y4 * y4 - e1_q3) / e1_q6;
              IF ABS(x1_arg) < eps_sols THEN
                SET x1_arg = 0;
              END IF;
              SET x1 = SQRT(x1_arg);
              SET x2 = -x1;
              SET abc_a = e2_q6;
              SET abc_b = e2_q4 * y4 + e2_q5;
              SET abc_c = e2_q1 * y4 * y4 + e2_q2 * y4 + e2_q3;
              IF ABS(abc_c + abc_b * x1 + abc_a * x1 * x1) < eps_sols THEN
                SET y4_x1 = x1; 
                SET nPoints = nPoints + 1;
              END IF;
              IF x1 <> x2 THEN
                IF ABS(abc_c + abc_b * x2 + abc_a * x2 * x2) < eps_sols THEN
                  SET y4_x2 = x2;
                  SET nPoints = nPoints + 1;
                END IF;
              END IF;
            END IF;
          END IF;
        END IF;
      END IF;
     
      /* Here we will sort the points */
      IF y1_x1 IS NOT NULL THEN
        SET Q0_x = y1_x1;
        SET Q0_y = y1;
      END IF;
      IF y1_x2 IS NOT NULL THEN
        IF Q0_x IS NOT NULL THEN
          SET Q1_x = y1_x2;
          SET Q1_y = y1;
        ELSE
          SET Q0_x = y1_x2;
          SET Q0_y = y1;
        END IF;
      END IF;
      IF y2_x1 IS NOT NULL THEN
        IF Q0_x IS NOT NULL THEN
          IF Q1_x IS NOT NULL THEN
            SET Q2_x = y2_x1;
            SET Q2_y = y2;
          ELSE 
            SET Q1_x = y2_x1;
            SET Q1_y = y2;
          END IF;
        ELSE
          SET Q0_x = y2_x1;
          SET Q0_y = y2;
        END IF;
      END IF;
      IF y2_x2 IS NOT NULL THEN
        IF Q0_x IS NOT NULL THEN
          IF Q1_x IS NOT NULL THEN
            IF Q2_x IS NOT NULL THEN
              SET Q3_x = y2_x2;
              SET Q3_y = y2;
            ELSE
              SET Q2_x = y2_x2;
              SET Q2_y = y2;
            END IF;
          ELSE
            SET Q1_x = y2_x2;
            SET Q1_y = y2;
          END IF;
        ELSE
          SET Q0_x = y2_x2;
          SET Q0_y = y2;
        END IF;
      END IF;
      IF y3_x1 IS NOT NULL THEN
        IF Q0_x IS NOT NULL THEN
          IF Q1_x IS NOT NULL THEN
            IF Q2_x IS NOT NULL THEN
              SET Q3_x = y3_x1;
              SET Q3_y = y3;
            ELSE
              SET Q2_x = y3_x1;
              SET Q2_y = y3;
            END IF;
          ELSE
            SET Q1_x = y3_x1;
            SET Q1_y = y3;
          END IF;
        ELSE
          SET Q0_x = y3_x1;
          SET Q0_y = y3;
        END IF;
      END IF;
      IF y3_x2 IS NOT NULL THEN
        IF Q0_x IS NOT NULL THEN
          IF Q1_x IS NOT NULL THEN
            IF Q2_x IS NOT NULL THEN
              SET Q3_x = y3_x2;
              SET Q3_y = y3;
            ELSE
              SET Q2_x = y3_x2;
              SET Q2_y = y3;
            END IF;
          ELSE
            SET Q1_x = y3_x2;
            SET Q1_y = y3;
          END IF;
        ELSE
          SET Q0_x = y3_x2;
          SET Q0_y = y3;
        END IF;
      END IF;
      IF y4_x1 IS NOT NULL THEN
        IF Q0_x IS NOT NULL THEN
          IF Q1_x IS NOT NULL THEN
            IF Q2_x IS NOT NULL THEN
              SET Q3_x = y4_x1;
              SET Q3_y = y4;
            ELSE
              SET Q2_x = y4_x1;
              SET Q2_y = y4;
            END IF;
          ELSE
            SET Q1_x = y4_x1;
            SET Q1_y = y4;
          END IF;
        ELSE
          SET Q0_x = y4_x1;
          SET Q0_y = y4;
        END IF;
      END IF;
      IF y4_x2 IS NOT NULL THEN
        IF Q0_x IS NOT NULL THEN
          IF Q1_x IS NOT NULL THEN
            IF Q2_x IS NOT NULL THEN
              SET Q3_x = y4_x2;
              SET Q3_y = y4;
            ELSE
              SET Q2_x = y4_x2;
              SET Q2_y = y4;
            END IF;
          ELSE
            SET Q1_x = y4_x2;
            SET Q1_y = y4;
          END IF;
        ELSE
          SET Q0_x = y4_x2;
          SET Q0_y = y4;
        END IF;
      END IF;

    END IF;
  ELSE
   IF distance <= (ie1_b + ie2_b) THEN
     /* No intersection, but containment*/
     SET doIntersect = TRUE;
     SET doContain = TRUE;
   ELSE
     /* No intersection, and no containment (ie separated)*/
     SET doContain = FALSE;
   END IF;
  END IF;

  /* Now that we have the intersection points, we will calculate
   * the area of intersection. 
   * For every intersection point we need the angle theta.
   * Theta runs from [-pi, pi].
   * We need two angles for this: theta_0 and theta_1,
   * but how do we now the orientation?
   * Therefore we need to know whether the center of e1 is inside
   * the area of doIntersect (i.e. inside e2), and vv center
   * of e2 inside e1?
   */
  /* First we order the points from quadrant 1-4*/
  IF doIntersect = TRUE THEN
    CASE Nroots
      WHEN 0 THEN
        IF doContain = TRUE THEN
          SET ogeval = 1;
          SET weight = 1;
        ELSE
          SET ogeval = 1;
          SET weight = -1;
        END IF;
      WHEN 1 THEN
        /* Determine if the centre of E2 is outside or inside E1 */
        IF  e1_q1 * ie2_k * ie2_k + e1_q1 + e1_q6 * ie2_h * ie2_h > 0 THEN
          SET ogeval = 2;
          SET weight = 0;
        ELSE
          SET ogeval = 3;
          SET weight = 1;
        END IF;
      WHEN 2 THEN
        /* We might have three points of intersection, 
         * when one of them is tangent. The tangent point can then be
         * skipped in calculating the areas.
         */
        IF nPoints = 3 THEN
          SET ogeval = 4;
          /**
           * We have to find out what is the tangent point of intersection
           * and skip it in the area calculations
           */
          SET e1_m_0 = ATAN(-(2 * e2_q6 * Q0_x) / (2 * e2_q1 * Q0_y));
          SET e1_m_1 = ATAN(-(2 * e2_q6 * Q1_x) / (2 * e2_q1 * Q1_y));
          SET e1_m_2 = ATAN(-(2 * e2_q6 * Q2_x) / (2 * e2_q1 * Q2_y));
        
          SET e2_m_0 = ATAN( -(2 * e2_q6 * Q0_x + e2_q4 * Q0_y + e2_q5)
                           /  (2 * e2_q1 * Q0_y + e2_q4 * Q0_x + e2_q2)
                           );
          SET e2_m_1 = ATAN( -(2 * e2_q6 * Q1_x + e2_q4 * Q1_y + e2_q5)
                           /  (2 * e2_q1 * Q1_y + e2_q4 * Q1_x + e2_q2)
                           );
          SET e2_m_2 = ATAN( -(2 * e2_q6 * Q2_x + e2_q4 * Q2_y + e2_q5)
                           /  (2 * e2_q1 * Q2_y + e2_q4 * Q2_x + e2_q2)
                           );
          IF ABS(e1_m_0 - e2_m_0) < 1E-10 THEN
            /*SET P0_skip = TRUE;*/
            SET Q0_x = Q1_x;
            SET Q0_y = Q1_y;
            SET Q1_x = Q2_x;
            SET Q1_y = Q2_y;
          ELSE 
            IF ABS(e1_m_1 - e2_m_1) < 1E-10 THEN
              /*SET P1_skip = TRUE;*/
              SET Q1_x = Q2_x;
              SET Q1_y = Q2_y;
            ELSE
              IF ABS(e1_m_2 - e2_m_2) < 1E-10 THEN
                SET Q2_x = NULL;
                SET Q2_y = NULL;
              END IF;
            END IF;
          END IF;
        END IF;
        
        IF nPoints = 1 THEN
          IF e1_q1 * ie2_k * ie2_k + e1_q3 + e1_q6 * ie2_h * ie2_h > 0 THEN
            SET ogeval = 5;
            SET weight = 0;
          ELSE
            SET ogeval = 6;
            SET weight = 1;
          END IF;
        ELSE
          /**
           * TODO: If the two points are tangent we have the special case 
           * that one of the ellipses is contained by the other
           */
          SET ogeval = 7;
          /* c1_* is the angle on the circle, e1_* is the angle in the ellipse*/
          SET c1_angle_0 = ATAN((ie1_a * Q0_y) / (ie1_b * Q0_x));
          IF Q0_x < 0 THEN 
            IF Q0_y < 0 THEN
              SET c1_angle_0 = -PI() + c1_angle_0;
            ELSE 
              SET c1_angle_0 = PI() + c1_angle_0;
            END IF;
          END IF;
          SET c1_angle_1 = ATAN((ie1_a * Q1_y) / (ie1_b * Q1_x));
          IF Q1_x < 0 THEN
            IF Q1_y < 0 THEN
              SET c1_angle_1 = -PI() + c1_angle_1;
            ELSE
              SET c1_angle_1 = PI() + c1_angle_1;
            END IF;
          END IF;
          IF c1_angle_0 < c1_angle_1 THEN
            SET c1_theta_0 = c1_angle_0;
            SET P0_x = Q0_x;
            SET P0_y = Q0_y;
            SET c1_theta_1 = c1_angle_1;
            SET P1_x = Q1_x;
            SET P1_y = Q1_y;
          ELSE
            SET c1_theta_0 = c1_angle_1;
            SET P0_x = Q1_x;
            SET P0_y = Q1_y;
            SET c1_theta_1 = c1_angle_0;
            SET P1_x = Q0_x;
            SET P1_y = Q0_y;
          END IF;

          SET e1_theta_0 = ATAN(P0_y / P0_x);
          IF P0_x < 0 THEN
            IF P0_y < 0 THEN
              SET e1_theta_0 = -PI() + e1_theta_0;
            ELSE
              SET e1_theta_0 = PI() + e1_theta_0;
            END IF;
          END IF;
          SET e1_theta_1 = ATAN(P1_y / P1_x);
          IF P1_x < 0 THEN
            IF P1_y < 0 THEN
              SET e1_theta_1 = -PI() + e1_theta_1;
            ELSE
              SET e1_theta_1 = PI() + e1_theta_1;
            END IF;
          END IF;

          /* the angles of the intersection points of ellipse 2
           * are inversely ordered wrt ellipse 1,
           * e1: P0 -> P1 = e1_theta_0 -> e1_theta_1
           * then:
           * e2: P1 -> P0 = ...
           */
          /* To calculate the theta's we use the dot product: 
           * (P1-C2) dot g = |(P1-C2)| |g| cos(theta1)
           */
          /* c2_beta is the angle from x-axis to point P projected
           * on ellipse 2 */
        
          IF ABS(TAN(e2_phi)) < 1E+10 THEN
            SET e2_a_m_x = 1;
            SET e2_a_m_y = TAN(e2_phi);
            SET e2_b_m_x = -TAN(e2_phi);
            SET e2_b_m_y = 1;
          ELSE
            SET e2_a_m_x = 0;
            SET e2_a_m_y = 1;
            SET e2_b_m_x = -1;
            SET e2_b_m_y = 0;
          END IF;
        
          SET e2_P1_vec_x = P1_x - ie2_h;
          SET e2_P1_vec_y = P1_y - ie2_k;
          SET e2_P1_proj_x =   (e2_P1_vec_x * e2_a_m_x + e2_P1_vec_y * e2_a_m_y)
                             / SQRT(e2_a_m_x * e2_a_m_x + e2_a_m_y * e2_a_m_y);
          SET e2_P1_proj_y =   (e2_P1_vec_x * e2_b_m_x + e2_P1_vec_y * e2_b_m_y)
                             / SQRT(e2_b_m_x * e2_b_m_x + e2_b_m_y * e2_b_m_y);
          SET c2_beta_1 = ATAN( (ie2_a * (e2_P1_vec_x * e2_b_m_x + e2_P1_vec_y * e2_b_m_y))
                              / (ie2_b * (e2_P1_vec_x * e2_a_m_x + e2_P1_vec_y * e2_a_m_y))
                              );
          SET e2_theta_1 = ATAN(e2_P1_proj_y / e2_P1_proj_x);
          IF e2_P1_proj_x < 0 THEN
            IF e2_P1_proj_y < 0 THEN
              SET c2_beta_1 = -PI() + c2_beta_1;
              SET e2_theta_1 = -PI() + e2_theta_1;
            ELSE
              SET c2_beta_1 = PI() + c2_beta_1;
              SET e2_theta_1 = PI() + e2_theta_1;
            END IF;
          END IF;
          SET c2_theta_1 = c2_beta_1;

          SET e2_P0_vec_x = P0_x - ie2_h;
          SET e2_P0_vec_y = P0_y - ie2_k;
          SET e2_P0_proj_x =   (e2_P0_vec_x * e2_a_m_x + e2_P0_vec_y * e2_a_m_y)
                             / SQRT(e2_a_m_x * e2_a_m_x + e2_a_m_y * e2_a_m_y);
          SET e2_P0_proj_y =   (e2_P0_vec_x * e2_b_m_x + e2_P0_vec_y * e2_b_m_y)
                             / SQRT(e2_b_m_x * e2_b_m_x + e2_b_m_y * e2_b_m_y);
          SET c2_beta_0 = ATAN( (ie2_a * (e2_P0_vec_x * e2_b_m_x + e2_P0_vec_y * e2_b_m_y))
                              / (ie2_b * (e2_P0_vec_x * e2_a_m_x + e2_P0_vec_y * e2_a_m_y))
                              );
          SET e2_theta_0 = ATAN(e2_P0_proj_y / e2_P0_proj_x);
          IF e2_P0_proj_x < 0 THEN
            IF e2_P0_proj_y < 0 THEN
              SET c2_beta_0 = -PI() + c2_beta_0;
              SET e2_theta_0 = -PI() + e2_theta_0;
            ELSE
              SET c2_beta_0 = PI() + c2_beta_0;
              SET e2_theta_0 = PI() + e2_theta_0;
            END IF;
          END IF;
          SET c2_theta_0 = c2_beta_0;

          SET least_e_area = PI() * LEAST(ie1_a * ie1_b, ie2_a * ie2_b);

          /* Here we determine whether the centres are above 
           * the P0-P1 line: L: y = mx+c
           */
          IF ABS(P1_x - P0_x) > 1E-10 THEN
            SET m = (P1_y - P0_y) / (P1_x - P0_x);
            SET c = P0_y - m * P0_x;
            SET slope = SIGN(ATAN(m));
          ELSE
            SET slope = 1;
          END IF;
          IF ABS(P1_x - P0_x) > 1E-10 THEN
            IF c < 0 THEN
              SET C1_above = TRUE;
            ELSE
              SET C1_above = FALSE;
            END IF;
          ELSE
            SET C1_above = FALSE;
          END IF;
        
          IF ABS(P1_x - P0_x) > 1E-10 THEN
            IF ie2_k > m * ie2_h - c THEN
              SET C2_above = TRUE;
            ELSE
              SET C2_above = FALSE;
            END IF;
          ELSE
            SET C2_above = FALSE;
          END IF;
        
          SET e_area = areaIntersection2P(e2_phi
                                         ,slope
                                         ,C1_above 
                                         ,C2_above
                                         ,ie1_a
                                         ,ie1_b
                                         ,e1_theta_0
                                         ,e1_theta_1
                                         ,c1_theta_0
                                         ,c1_theta_1
                                         ,ie2_a
                                         ,ie2_b
                                         ,e2_theta_1
                                         ,e2_theta_0
                                         ,c2_theta_1
                                         ,c2_theta_0);

          SET weight = e_area / least_e_area;
        END IF;
      WHEN 3 THEN
        SET ogeval = 8;
      WHEN 4 THEN
        SET ogeval = 9;
        /* c1_* is the angle on the circle, e1_* is the angle in the ellipse*/
        SET c1_angle_0 = ATAN((ie1_a * Q0_y) / (ie1_b * Q0_x));
        IF Q0_x < 0 THEN 
          IF Q0_y < 0 THEN
            SET c1_angle_0 = -PI() + c1_angle_0;
          ELSE 
            SET c1_angle_0 = PI() + c1_angle_0;
          END IF;
        END IF;
        
        SET c1_angle_1 = ATAN((ie1_a * Q1_y) / (ie1_b * Q1_x));
        IF Q1_x < 0 THEN
          IF Q1_y < 0 THEN
            SET c1_angle_1 = -PI() + c1_angle_1;
          ELSE
            SET c1_angle_1 = PI() + c1_angle_1;
          END IF;
        END IF;
        
        SET c1_angle_2 = ATAN((ie1_a * Q2_y) / (ie1_b * Q2_x));
        IF Q2_x < 0 THEN
          IF Q2_y < 0 THEN
            SET c1_angle_2 = -PI() + c1_angle_2;
          ELSE
            SET c1_angle_2 = PI() + c1_angle_2;
          END IF;
        END IF;
        
        SET c1_angle_3 = ATAN((ie1_a * Q3_y) / (ie1_b * Q3_x));
        IF Q3_x < 0 THEN
          IF Q3_y < 0 THEN
            SET c1_angle_3 = -PI() + c1_angle_3;
          ELSE
            SET c1_angle_3 = PI() + c1_angle_3;
          END IF;
        END IF;
        
        CALL pTestSortAngles(c1_angle_0
                            ,c1_angle_1
                            ,c1_angle_2
                            ,c1_angle_3
                            ,Q0_x
                            ,Q0_y
                            ,Q1_x
                            ,Q1_y
                            ,Q2_x
                            ,Q2_y
                            ,Q3_x
                            ,Q3_y
                            ,c1_theta_0
                            ,c1_theta_1
                            ,c1_theta_2
                            ,c1_theta_3
                            ,P0_x
                            ,P0_y
                            ,P1_x
                            ,P1_y
                            ,P2_x
                            ,P2_y
                            ,P3_x
                            ,P3_y
                            );
        
        SET e1_theta_0 = ATAN(P0_y / P0_x);
        IF P0_x < 0 THEN
          IF P0_y < 0 THEN
            SET e1_theta_0 = -PI() + e1_theta_0;
          ELSE
            SET e1_theta_0 = PI() + e1_theta_0;
          END IF;
        END IF;
        
        SET e1_theta_1 = ATAN(P1_y / P1_x);
        IF P1_x < 0 THEN
          IF P1_y < 0 THEN
            SET e1_theta_1 = -PI() + e1_theta_1;
          ELSE
            SET e1_theta_1 = PI() + e1_theta_1;
          END IF;
        END IF;

        SET e1_theta_2 = ATAN(P2_y / P2_x);
        IF P2_x < 0 THEN
          IF P2_y < 0 THEN
            SET e1_theta_2 = -PI() + e1_theta_2;
          ELSE
            SET e1_theta_2 = PI() + e1_theta_2;
          END IF;
        END IF;

        SET e1_theta_3 = ATAN(P3_y / P3_x);
        IF P3_x < 0 THEN
          IF P3_y < 0 THEN
            SET e1_theta_3 = -PI() + e1_theta_3;
          ELSE
            SET e1_theta_3 = PI() + e1_theta_3;
          END IF;
        END IF;

        IF ABS(TAN(e2_phi)) < 1E+10 THEN
          SET e2_a_m_x = 1;
          SET e2_a_m_y = TAN(e2_phi);
          SET e2_b_m_x = -TAN(e2_phi);
          SET e2_b_m_y = 1;
        ELSE
          SET e2_a_m_x = 0;
          SET e2_a_m_y = 1;
          SET e2_b_m_x = -1;
          SET e2_b_m_y = 0;
        END IF;
        
        SET e2_P0_vec_x = P0_x - ie2_h;
        SET e2_P0_vec_y = P0_y - ie2_k;
        SET e2_P0_proj_x =   (e2_P0_vec_x * e2_a_m_x + e2_P0_vec_y * e2_a_m_y)
                           / SQRT(e2_a_m_x * e2_a_m_x + e2_a_m_y * e2_a_m_y);
        SET e2_P0_proj_y =   (e2_P0_vec_x * e2_b_m_x + e2_P0_vec_y * e2_b_m_y)
                           / SQRT(e2_b_m_x * e2_b_m_x + e2_b_m_y * e2_b_m_y);
        SET c2_beta_0 = ATAN( (ie2_a * (e2_P0_vec_x * e2_b_m_x + e2_P0_vec_y * e2_b_m_y))
                            / (ie2_b * (e2_P0_vec_x * e2_a_m_x + e2_P0_vec_y * e2_a_m_y))
                            );
        SET e2_theta_0 = ATAN(e2_P0_proj_y / e2_P0_proj_x);
        IF e2_P0_proj_x < 0 THEN
          IF e2_P0_proj_y < 0 THEN
            SET c2_beta_0 = -PI() + c2_beta_0;
            SET e2_theta_0 = -PI() + e2_theta_0;
          ELSE
            SET c2_beta_0 = PI() + c2_beta_0;
            SET e2_theta_0 = PI() + e2_theta_0;
          END IF;
        END IF;
        SET c2_theta_0 = c2_beta_0;

        SET e2_P1_vec_x = P1_x - ie2_h;
        SET e2_P1_vec_y = P1_y - ie2_k;
        SET e2_P1_proj_x =   (e2_P1_vec_x * e2_a_m_x + e2_P1_vec_y * e2_a_m_y)
                           / SQRT(e2_a_m_x * e2_a_m_x + e2_a_m_y * e2_a_m_y);
        SET e2_P1_proj_y =   (e2_P1_vec_x * e2_b_m_x + e2_P1_vec_y * e2_b_m_y)
                           / SQRT(e2_b_m_x * e2_b_m_x + e2_b_m_y * e2_b_m_y);
        SET c2_beta_1 = ATAN( (ie2_a * (e2_P1_vec_x * e2_b_m_x + e2_P1_vec_y * e2_b_m_y))
                            / (ie2_b * (e2_P1_vec_x * e2_a_m_x + e2_P1_vec_y * e2_a_m_y))
                            );
        SET e2_theta_1 = ATAN(e2_P1_proj_y / e2_P1_proj_x);
        IF e2_P1_proj_x < 0 THEN
          IF e2_P1_proj_y < 0 THEN
            SET c2_beta_1 = -PI() + c2_beta_1;
            SET e2_theta_1 = -PI() + e2_theta_1;
          ELSE
            SET c2_beta_1 = PI() + c2_beta_1;
            SET e2_theta_1 = PI() + e2_theta_1;
          END IF;
        END IF;
        SET c2_theta_1 = c2_beta_1;

        SET e2_P2_vec_x = P2_x - ie2_h;
        SET e2_P2_vec_y = P2_y - ie2_k;
        SET e2_P2_proj_x =   (e2_P2_vec_x * e2_a_m_x + e2_P2_vec_y * e2_a_m_y)
                           / SQRT(e2_a_m_x * e2_a_m_x + e2_a_m_y * e2_a_m_y);
        SET e2_P2_proj_y =   (e2_P2_vec_x * e2_b_m_x + e2_P2_vec_y * e2_b_m_y)
                           / SQRT(e2_b_m_x * e2_b_m_x + e2_b_m_y * e2_b_m_y);
        SET c2_beta_2 = ATAN( (ie2_a * (e2_P2_vec_x * e2_b_m_x + e2_P2_vec_y * e2_b_m_y))
                            / (ie2_b * (e2_P2_vec_x * e2_a_m_x + e2_P2_vec_y * e2_a_m_y))
                            );
        SET e2_theta_2 = ATAN(e2_P2_proj_y / e2_P2_proj_x);
        IF e2_P2_proj_x < 0 THEN
          IF e2_P2_proj_y < 0 THEN
            SET c2_beta_2 = -PI() + c2_beta_2;
            SET e2_theta_2 = -PI() + e2_theta_2;
          ELSE
            SET c2_beta_2 = PI() + c2_beta_2;
            SET e2_theta_2 = PI() + e2_theta_2;
          END IF;
        END IF;
        SET c2_theta_2 = c2_beta_2;

        SET e2_P3_vec_x = P3_x - ie2_h;
        SET e2_P3_vec_y = P3_y - ie2_k;
        SET e2_P3_proj_x =   (e2_P3_vec_x * e2_a_m_x + e2_P3_vec_y * e2_a_m_y)
                           / SQRT(e2_a_m_x * e2_a_m_x + e2_a_m_y * e2_a_m_y);
        SET e2_P3_proj_y =   (e2_P3_vec_x * e2_b_m_x + e2_P3_vec_y * e2_b_m_y)
                           / SQRT(e2_b_m_x * e2_b_m_x + e2_b_m_y * e2_b_m_y);
        SET c2_beta_3 = ATAN( (ie2_a * (e2_P3_vec_x * e2_b_m_x + e2_P3_vec_y * e2_b_m_y))
                            / (ie2_b * (e2_P3_vec_x * e2_a_m_x + e2_P3_vec_y * e2_a_m_y))
                            );
        SET e2_theta_3 = ATAN(e2_P3_proj_y / e2_P3_proj_x);
        IF e2_P3_proj_x < 0 THEN
          IF e2_P3_proj_y < 0 THEN
            SET c2_beta_3 = -PI() + c2_beta_3;
            SET e2_theta_3 = -PI() + e2_theta_3;
          ELSE
            SET c2_beta_3 = PI() + c2_beta_3;
            SET e2_theta_3 = PI() + e2_theta_3;
          END IF;
        END IF;
        SET c2_theta_3 = c2_beta_3;

        SET least_e_area = PI() * LEAST(ie1_a * ie1_b, ie2_a * ie2_b);
        
        SET e_area =   areaLineEllipticalArc(ie1_a,ie1_b,e1_theta_0,e1_theta_1,c1_theta_0,c1_theta_1)
                     + areaLineEllipticalArc(ie1_a,ie1_b,e1_theta_2,e1_theta_3,c1_theta_2,c1_theta_3)
                     + areaLineEllipticalArc(ie2_a,ie2_b,e2_theta_1,e2_theta_2,c2_theta_1,c2_theta_2)
                     + areaLineEllipticalArc(ie2_a,ie2_b,e2_theta_3,e2_theta_0,c2_theta_3,c2_theta_0);
        SET e_triangles =   ABS((P2_x - P0_x) * (P1_y - P0_y) - (P1_x - P0_x) * (P2_y - P0_y)) / 2
                          + ABS((P0_x - P2_x) * (P3_y - P2_y) - (P3_x - P2_x) * (P0_y - P2_y)) / 2;
        SET weight = (e_area + e_triangles) / least_e_area;
    END CASE;
  ELSE
    SET ogeval = 10;
    SET weight = -2;
  END IF;

  RETURN weight;

END;
//

DELIMITER ;
