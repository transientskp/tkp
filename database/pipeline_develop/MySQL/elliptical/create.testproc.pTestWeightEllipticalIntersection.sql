DROP PROCEDURE IF EXISTS pTestWeightEllipticalIntersection;

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
 */
CREATE PROCEDURE pTestWeightEllipticalIntersection(IN ie1_a DOUBLE
                                         ,IN ie1_b DOUBLE
                                         ,IN ie2_h DOUBLE
                                         ,IN ie2_k DOUBLE
                                         ,IN ie2_a DOUBLE
                                         ,IN ie2_b DOUBLE
                                         ,IN ie2_phi DOUBLE
                                         ,OUT oe2_phi DOUBLE
                                         ,OUT odistance DOUBLE
                                         ,OUT oready BOOLEAN
                                         ,OUT odoIntersect BOOLEAN
                                         ,OUT oe1_q1 DOUBLE
                                         ,OUT oe1_q3 DOUBLE
                                         ,OUT oe1_q6 DOUBLE
                                         ,OUT oe2_q1 DOUBLE
                                         ,OUT oe2_q2 DOUBLE
                                         ,OUT oe2_q3 DOUBLE
                                         ,OUT oe2_q4 DOUBLE
                                         ,OUT oe2_q5 DOUBLE
                                         ,OUT oe2_q6 DOUBLE
                                         ,OUT oalpha4 DOUBLE
                                         ,OUT oalpha3 DOUBLE
                                         ,OUT oalpha2 DOUBLE
                                         ,OUT oalpha1 DOUBLE
                                         ,OUT oalpha0 DOUBLE
                                         ,OUT oNroots INT
                                         ,OUT ox1 DOUBLE
                                         ,OUT oy1 DOUBLE
                                         ,OUT ox2 DOUBLE
                                         ,OUT oy2 DOUBLE
                                         ,OUT ox3 DOUBLE
                                         ,OUT oy3 DOUBLE
                                         ,OUT ox4 DOUBLE
                                         ,OUT oy4 DOUBLE
                                         ,OUT oangle_1 DOUBLE
                                         ,OUT oangle_2 DOUBLE
                                         ,OUT oP0_x DOUBLE
                                         ,OUT oP0_y DOUBLE
                                         ,OUT oP1_x DOUBLE
                                         ,OUT oP1_y DOUBLE
                                         ,OUT oslope DOUBLE
                                         ,OUT oe1_theta_0 DOUBLE
                                         ,OUT oe1_theta_1 DOUBLE
                                         ,OUT oe2_beta_0 DOUBLE
                                         ,OUT oe2_beta_1 DOUBLE
                                         ,OUT oe2_theta_0 DOUBLE
                                         ,OUT oe2_theta_1 DOUBLE
                                         ,OUT ogeval INT
                                         ,OUT oC1_above BOOLEAN
                                         ,OUT oleast_e_area DOUBLE
                                         ,OUT oe1_area DOUBLE
                                         ,OUT oe2_area DOUBLE
                                         ,OUT oweight DOUBLE
                                         ) 

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

  DECLARE i INT;
  DECLARE yi_root, yi, y1, y2, y3, y4, y1_x DOUBLE;
  DECLARE yi_x, yi_e1_x1, yi_e1_x2, yi_e2_x1, yi_e2_x2 DOUBLE;
  DECLARE abc_a, abc_b, abc_c, abc_D DOUBLE;
  DECLARE x1, x2, x3, x4 DOUBLE;

  DECLARE angle_1, angle_2, angle_3, angle_4 DOUBLE;
  DECLARE e2_beta_0, e2_beta_1 DOUBLE;
  DECLARE P0_x, P0_y, P1_x, P1_y, P2_x, P2_y, P3_x, P3_y, slope DOUBLE;
  DECLARE e1_theta_0, e1_theta_1, e1_theta_2, e1_theta_3 DOUBLE;
  DECLARE e2_theta_0, e2_theta_1, e2_theta_2, e2_theta_3 DOUBLE;
  
  DECLARE e1_m_0, e1_m_1, e1_m_2, e2_m_0, e2_m_1, e2_m_2 DOUBLE;
  DECLARE e1_area, e2_area, least_e_area DOUBLE;
  DECLARE C1_above BOOLEAN;

  DECLARE weight DOUBLE;

  /**
   * For Ellipse 1 we should have (x,y) = (0,0), and pa = 90,
   * We constrain ellipse 2 by setting the angle of rotation according
   * to the x-axis to [-pi, pi]
   */
  IF ie2_phi > 90 THEN
    SET ie2_phi = ie2_phi - 180;
  ELSE
    IF ie2_phi < -90 THEN
      SET ie2_phi = ie2_phi + 180;
    END IF;
  END IF;
  SET e2_phi = RADIANS(ie2_phi);
  set oe2_phi = e2_phi;
  /** 
   * These tests can be executed immediately, to know
   * whether one there is separation or containment.
   */
  SET distance = SQRT(ie2_h * ie2_h + ie2_k * ie2_k);
  SET odistance = distance;
  IF distance > (ie1_a + ie2_a) THEN
    SET doIntersect = FALSE;
    /*SET weight = -1;*/
    /* They do not intersect, we do not have to calculate roots 
     * and stuff like that*/
    SET ready = TRUE;
  END IF;

  IF ready = FALSE THEN
    IF distance <= (ie1_b + ie2_b) THEN
      SET doIntersect = TRUE;
      /* We are sure they intersect, but have still have to 
       * calculate the intersection area
       */
     SET ready = FALSE;
    END IF;
  END IF;

  SET oready = ready;

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

    SET oe1_q1 = e1_q1;
    SET oe1_q3 = e1_q3;
    SET oe1_q6 = e1_q6;
    
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
    
    SET oe2_q1 = e2_q1;
    SET oe2_q2 = e2_q2;
    SET oe2_q3 = e2_q3;
    SET oe2_q4 = e2_q4;
    SET oe2_q5 = e2_q5;
    SET oe2_q6 = e2_q6;

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

    SET oalpha4 = alpha4;
    SET oalpha3 = alpha3;
    SET oalpha2 = alpha2;
    SET oalpha1 = alpha1;
    SET oalpha0 = alpha0;

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
    
    SET Nroots = sign_change_neg - sign_change_pos;
    set oNroots = Nroots;
    IF Nroots > 0 THEN
      SET doIntersect = TRUE;
    ELSE
      SET doIntersect = FALSE;
    END IF;
  
  END IF; 
  
  SET odoIntersect = doIntersect;

  /* Here we will calculate the points of intersection*/
  IF doIntersect = TRUE THEN
    IF Nroots > 0 THEN
      /* We will get the roots of the Bezout determinant */
      CALL getQuarticRoots(alpha4,alpha3,alpha2,alpha1,alpha0
                          ,y1,y2,y3,y4);
      SET i = 1;
      WHILE (i < Nroots + 1) DO
        CASE i
          WHEN 1 THEN SET yi = y1;
          WHEN 2 THEN SET yi = y2;
          WHEN 3 THEN SET yi = y3;
          WHEN 4 THEN SET yi = y4;
        END CASE;
        /* check solutions in ellipse 1: 
         * E1: e1_q1 y^2 + e1_q3 + e1_q6 x^2
         */
        SET yi_root = (-e1_q1 * yi * yi - e1_q3) / e1_q6;
        IF yi_root >= 0 THEN
          SET yi_e1_x1 = SQRT(yi_root);
          SET yi_e1_x2 = -yi_e1_x1;
          /* Now we check the solutions in ellipse 2:
           * E2(x,y) = (e2_q1 y^2 + e2_q2 y + e2_q3) 
           *           + (e2_q4 y + e2_q5) x 
           *           + e2_q6 x^2 = 0
           * We have sol. y1, check quadr eq. discr.
           */
          SET abc_a = e2_q6;
          SET abc_b = e2_q4 * yi + e2_q5;
          SET abc_c = e2_q1 * yi * yi + e2_q2 * yi + e2_q3;
          SET abc_D = abc_b * abc_b - 4 * abc_a * abc_c;
          IF abc_D >= 0 THEN
            SET yi_e2_x1 = (-abc_b + SQRT(abc_D)) / (2 * abc_a);
            SET yi_e2_x2 = (-abc_b - SQRT(abc_D)) / (2 * abc_a);
          END IF;
        END IF;
        /* Now we have to select the valid solutions only,
         * therefore it is enough to take one of */
        IF ABS(yi_e1_x1 - yi_e2_x1) BETWEEN -0.001 AND 0.001 THEN 
          SET yi_x = yi_e1_x1;
        END IF;
        IF ABS(yi_e1_x1 - yi_e2_x2) BETWEEN -0.001 AND 0.001 THEN 
          SET yi_x = yi_e1_x1;
        END IF;
        IF ABS(yi_e1_x2 - yi_e2_x1) BETWEEN -0.001 AND 0.001 THEN 
          SET yi_x = yi_e1_x2;
        END IF;
        IF ABS(yi_e1_x2 - yi_e2_x2) BETWEEN -0.001 AND 0.001 THEN 
          SET yi_x = yi_e1_x2;
        END IF;
        CASE i
          WHEN 1 THEN 
            SET x1 = yi_x;
          WHEN 2 THEN 
            SET x2 = yi_x;
          WHEN 3 THEN 
            SET x3 = yi_x;
          WHEN 4 THEN 
            SET x4 = yi_x;
        END CASE;
        SET i = i + 1;
      END WHILE;
      SET ox1 = x1;
      SET oy1 = y1;
      SET ox2 = x2;
      SET oy2 = y2;
      SET ox3 = x3;
      SET oy3 = y3;
      SET ox4 = x4;
      SET oy4 = y4;
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
        /* This is strange! We have an intersection but no roots...?*/
        SET weight = -1;
      WHEN 1 THEN
        /* Determine if it inside or outside the other ellipse */
        SET weight = 1;
      WHEN 2 THEN
        SET angle_1 = ATAN(y1 / x1);
        IF x1 < 0 THEN 
          IF y1 < 0 THEN
            SET angle_1 = -PI() + angle_1;
          ELSE 
            SET angle_1 = PI() + angle_1;
          END IF;
        END IF;
        SET oangle_1 = angle_1;
        SET angle_2 = ATAN(y2 / x2);
        IF x2 < 0 THEN
          IF y2 < 0 THEN
            SET angle_2 = -PI() + angle_2;
          ELSE
            SET angle_2 = PI() + angle_2;
          END IF;
        END IF;
        SET oangle_2 = angle_2;
        IF angle_1 < angle_2 THEN
          SET e1_theta_0 = angle_1;
          SET P0_x = x1;
          SET P0_y = y1;
          SET e1_theta_1 = angle_2;
          SET P1_x = x2;
          SET P1_y = y2;
        ELSE
          SET e1_theta_0 = angle_2;
          SET P0_x = x2;
          SET P0_y = y2;
          SET e1_theta_1 = angle_1;
          SET P1_x = x1;
          SET P1_y = y1;
        END IF;
        SET oP0_x = P0_x;
        SET oP0_y = P0_y;
        SET oP1_x = P1_x;
        SET oP1_y = P1_y;
        SET oe1_theta_0 = e1_theta_0;
        SET oe1_theta_1 = e1_theta_1;
        SET slope = SIGN(ATAN((P1_y - P0_y) / (P1_x - P0_x)));
        SET oslope = slope;
        /* the angles of the intersection points of ellipse 2
         * are inversely ordered wrt ellipse 1,
         * e1: P0 -> P1 = e1_theta_0 -> e1_theta_1
         * then:
         * e2: P1 -> P0 = ...
         */
        /* To calculate the theta's we use the dot product: 
         * (P1-C2) dot g = |(P1-C2)| |g| cos(theta1)
         */
        /* e2_beta is the angle from x-axis to P1*/
        SET e2_beta_1 = ATAN((P1_y - ie2_k) / (P1_x - ie2_h));
        IF (P1_x - ie2_h) < 0 THEN
          IF (P1_y - ie2_k) < 0 THEN
            SET e2_beta_1 = -PI() + e2_beta_1;
          ELSE
            SET e2_beta_1 = PI() + e2_beta_1;
          END IF;
        END IF;
        SET oe2_beta_1 = e2_beta_1;
        SET e2_theta_1 = e2_beta_1 - e2_phi;
        IF e2_theta_1 < -PI() THEN
          SET e2_theta_1 = e2_theta_1 + 2 * PI();
        ELSE
          IF e2_theta_1 > PI() THEN
            SET e2_theta_1 = e2_theta_1 - 2 * PI();
          END IF;
        END IF;
        SET oe2_theta_1 = e2_theta_1;

        SET e2_beta_0 = ATAN((P0_y - ie2_k) / (P0_x - ie2_h));
        IF (P0_x - ie2_h) < 0 THEN
          IF (P0_y - ie2_k) < 0 THEN
            SET e2_beta_0 = -PI() + e2_beta_0;
          ELSE
            SET e2_beta_0 = PI() + e2_beta_0;
          END IF;
        END IF;
        SET oe2_beta_0 = e2_beta_0;
        SET e2_theta_0 = e2_beta_0 - e2_phi;
        IF e2_theta_0 < -PI() THEN
          SET e2_theta_0 = e2_theta_0 + 2 * PI();
        ELSE
          IF e2_theta_0 > PI() THEN
            SET e2_theta_0 = e2_theta_0 - 2 * PI();
          END IF;
        END IF;
        SET oe2_theta_0 = e2_theta_0;
        
        SET least_e_area = PI() * LEAST(ie1_a * ie1_b, ie2_a * ie2_b);
        SET oleast_e_area = least_e_area;

        IF (P0_y - (P0_y - P1_y) / (P0_x - P1_x)) < 0 THEN
          SET C1_above = TRUE;
        ELSE
          SET C1_above = FALSE;
        END IF;
        SET oC1_above = C1_above;
        IF e2_phi > 0 THEN
          IF slope >= 0 THEN
            IF e1_theta_0 < 0 THEN
              SET ogeval = 1;
              SET e1_area = areaLineEllipticalArc(ie1_a
                                                 ,ie1_b
                                                 ,e1_theta_0
                                                 ,e1_theta_1);
              SET e2_area = areaLineEllipticalArc(ie2_a
                                                 ,ie2_b
                                                 ,e2_theta_1
                                                 ,e2_theta_0);
            ELSE
              SET ogeval = 2;
              SET e1_area = complementAreaLineEllipticalArc(ie1_a
                                                           ,ie1_b
                                                           ,theta_0
                                                           ,theta_1);
              SET e2_area = complementAreaLineEllipticalArc(ie2_a
                                                           ,ie2_b
                                                           ,theta_1
                                                           ,theta_0);
            END IF;
          ELSE
            IF C1_above = TRUE THEN
              IF e1_theta_1 < 0 THEN
                SET ogeval = 3;
                /*P0 -> P1*/
                SET e1_area = areaLineEllipticalArc(ie1_a
                                                   ,ie1_b
                                                   ,e1_theta_0
                                                   ,e1_theta_1);
                SET e2_area = areaLineEllipticalArc(ie2_a
                                                   ,ie2_b
                                                   ,e2_theta_1
                                                   ,e2_theta_0);
              ELSE
                SET ogeval = 4;
                /*INV*/
                SET e1_area = complementAreaLineEllipticalArc(ie1_a
                                                             ,ie1_b
                                                             ,theta_0
                                                             ,theta_1);
                SET e2_area = complementAreaLineEllipticalArc(ie2_a
                                                             ,ie2_b
                                                             ,theta_1
                                                             ,theta_0);
              END IF;
            ELSE
              SET ogeval = 5;
              /*P0 -> P1*/
              SET e1_area = areaLineEllipticalArc(ie1_a
                                                 ,ie1_b
                                                 ,e1_theta_0
                                                 ,e1_theta_1);
              SET e2_area = areaLineEllipticalArc(ie2_a
                                                 ,ie2_b
                                                 ,e2_theta_1
                                                 ,e2_theta_0);
            END IF;
          END IF;
        ELSE
          IF slope >= 0 THEN
            IF C1_above = TRUE THEN
              SET ogeval = 6;
              /*P0 -> P1*/
              SET e1_area = areaLineEllipticalArc(ie1_a
                                                 ,ie1_b
                                                 ,e1_theta_0
                                                 ,e1_theta_1);
              SET e2_area = areaLineEllipticalArc(ie2_a
                                                 ,ie2_b
                                                 ,e2_theta_1
                                                 ,e2_theta_0);
            ELSE
              IF e1_theta_0 > 0 THEN
                SET ogeval = 7;
                /*P0 -> P1*/
                SET e1_area = areaLineEllipticalArc(ie1_a
                                                   ,ie1_b
                                                   ,e1_theta_0
                                                   ,e1_theta_1);
                SET e2_area = areaLineEllipticalArc(ie2_a
                                                   ,ie2_b
                                                   ,e2_theta_1
                                                   ,e2_theta_0);
              ELSE
                SET ogeval = 8;
                /*INV*/
                SET e1_area = complementAreaLineEllipticalArc(ie1_a
                                                             ,ie1_b
                                                             ,theta_0
                                                             ,theta_1);
                SET e2_area = complementAreaLineEllipticalArc(ie2_a
                                                             ,ie2_b
                                                             ,theta_1
                                                             ,theta_0);
              END IF;
            END IF;
          ELSE
            IF e1_theta_1 < 0 THEN
              SET ogeval = 9;
              /*P0 -> P1*/
              SET e1_area = areaLineEllipticalArc(ie1_a
                                                 ,ie1_b
                                                 ,e1_theta_0
                                                 ,e1_theta_1);
              SET e2_area = areaLineEllipticalArc(ie2_a
                                                 ,ie2_b
                                                 ,e2_theta_1
                                                 ,e2_theta_0);
            ELSE
              SET ogeval = 10;
              /*INV*/
              SET e1_area = complementAreaLineEllipticalArc(ie1_a
                                                           ,ie1_b
                                                           ,theta_0
                                                           ,theta_1);
              SET e2_area = complementAreaLineEllipticalArc(ie2_a
                                                           ,ie2_b
                                                           ,theta_1
                                                           ,theta_0);
            END IF;
          END IF;
        END IF;
        SET oe1_area = e1_area;
        SET oe2_area = e2_area;
        SET weight = (e1_area + e2_area) / least_e_area;
      WHEN 3 THEN
        SET ogeval = 11;
        /**
         * We have to find out what is the tangent point of intersection
         * and skip it in the area calculations
         */
        SET e1_m_0 = ATAN(-(2 * e2_q6 * P0_x) / (2 * e2_q1 * P0_y));
        SET e1_m_1 = ATAN(-(2 * e2_q6 * P1_x) / (2 * e2_q1 * P1_y));
        SET e1_m_2 = ATAN(-(2 * e2_q6 * P2_x) / (2 * e2_q1 * P2_y));
        
        SET e2_m_0 = ATAN( -(2 * e2_q6 * P0_x + e2_q4 * P0_y + e2_q5)
                         /  (2 * e2_q1 * P0_y + e2_q4 * P0_x + e2_q2)
                         );
        SET e2_m_1 = ATAN( -(2 * e2_q6 * P1_x + e2_q4 * P1_y + e2_q5)
                         /  (2 * e2_q1 * P1_y + e2_q4 * P1_x + e2_q2)
                         );
        SET e2_m_2 = ATAN( -(2 * e2_q6 * P1_x + e2_q4 * P1_y + e2_q5)
                         /  (2 * e2_q1 * P1_y + e2_q4 * P1_x + e2_q2)
                         );
        IF e1_m_0 = e2_m_0 THEN
          /*SET P0_skip = TRUE;*/
          SET P0_x = P1_x;
          SET P0_y = P1_y;
          SET P1_x = P2_x;
          SET P1_y = P2_y;
        ELSE 
          IF e1_m_1 = e2_m_1 THEN
            /*SET P1_skip = TRUE;*/
            SET P1_x = P2_x;
            SET P1_y = P2_y;
          ELSE
            IF e1_m_2 = e2_m_2 THEN
              SET P2_x = NULL;
              SET P2_y = NULL;
            END IF;
          END IF;
        END IF;
      WHEN 4 THEN
        SET ogeval = 12;
    END CASE;
  ELSE
    SET ogeval = 13;
    SET weight = -2;
  END IF;

  SET oweight = weight;

--  RETURN weight;

END;
//

DELIMITER ;
