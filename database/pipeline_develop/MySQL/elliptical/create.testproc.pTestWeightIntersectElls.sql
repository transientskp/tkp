DROP PROCEDURE IF EXISTS pWeightIntersectElls;

DELIMITER //

/**
 * This boolean functions determines if two ellipses intersect.
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
CREATE PROCEDURE pWeightIntersectElls(IN ie1_ra DOUBLE
                                     ,IN ie1_decl DOUBLE
                                     ,IN ie1_ra_err DOUBLE
                                     ,IN ie1_decl_err DOUBLE
                                     ,IN ie2_ra DOUBLE
                                     ,IN ie2_decl DOUBLE
                                     ,IN ie2_ra_err DOUBLE
                                     ,IN ie2_decl_err DOUBLE
                                     ,OUT ointersect BOOLEAN
                                     ,OUT oalpha4 DOUBLE
                                     ,OUT oalpha3 DOUBLE
                                     ,OUT oalpha2 DOUBLE
                                     ,OUT oalpha1 DOUBLE
                                     ,OUT oalpha0 DOUBLE
                                     ,OUT oe2_q3 DOUBLE
                                     ,OUT onroots INT
                                     ,OUT oy1 DOUBLE
                                     ,OUT oy2 DOUBLE
                                     ,OUT oy3 DOUBLE
                                     ,OUT oy4 DOUBLE
                                     ,OUT ox1 DOUBLE
                                     ,OUT ox2 DOUBLE
                                     ,OUT ox3 DOUBLE
                                     ,OUT ox4 DOUBLE
                                     ,OUT oQuad1 INT
                                     ,OUT oQuad2 INT
                                     ,OUT oQuad3 INT
                                     ,OUT oQuad4 INT
                                     ,OUT otheta_0 DOUBLE
                                     ,OUT otheta_1 DOUBLE
                                     ,OUT oweight DOUBLE
                                     ) 

BEGIN
  DECLARE ready BOOLEAN DEFAULT FALSE;
  DECLARE intersect BOOLEAN DEFAULT FALSE;
  DECLARE weight DOUBLE DEFAULT -1;

  DECLARE e1_a DOUBLE DEFAULT NULL;
  DECLARE e1_b DOUBLE DEFAULT NULL;
  DECLARE e1_pa DOUBLE DEFAULT NULL;
  DECLARE e2_a DOUBLE DEFAULT NULL;
  DECLARE e2_b DOUBLE DEFAULT NULL;
  DECLARE e2_pa DOUBLE DEFAULT NULL;

  DECLARE theta_rot DOUBLE DEFAULT NULL;
  DECLARE e2_phi DOUBLE DEFAULT NULL;

  DECLARE e1_q1 DOUBLE DEFAULT NULL;
  DECLARE e1_q3 DOUBLE DEFAULT NULL;
  DECLARE e1_q6 DOUBLE DEFAULT NULL;

  DECLARE distance DOUBLE DEFAULT NULL;
  DECLARE e2_h DOUBLE DEFAULT NULL;
  DECLARE e2_k DOUBLE DEFAULT NULL;
  DECLARE e2_h_acc DOUBLE DEFAULT NULL;
  DECLARE e2_k_acc DOUBLE DEFAULT NULL;
  DECLARE e2_q1 DOUBLE DEFAULT NULL;
  DECLARE e2_q2 DOUBLE DEFAULT NULL;
  DECLARE e2_q3 DOUBLE DEFAULT NULL;
  DECLARE e2_q4 DOUBLE DEFAULT NULL;
  DECLARE e2_q5 DOUBLE DEFAULT NULL;
  DECLARE e2_q6 DOUBLE DEFAULT NULL;

  DECLARE v0 DOUBLE DEFAULT NULL;
  DECLARE v1 DOUBLE DEFAULT NULL;
  DECLARE v2 DOUBLE DEFAULT NULL;
  DECLARE v3 DOUBLE DEFAULT NULL;
  DECLARE v4 DOUBLE DEFAULT NULL;
  DECLARE v5 DOUBLE DEFAULT NULL;
  DECLARE v6 DOUBLE DEFAULT NULL;
  DECLARE v7 DOUBLE DEFAULT NULL;
  DECLARE v8 DOUBLE DEFAULT NULL;

  DECLARE alpha0 DOUBLE DEFAULT NULL;
  DECLARE alpha1 DOUBLE DEFAULT NULL;
  DECLARE alpha2 DOUBLE DEFAULT NULL;
  DECLARE alpha3 DOUBLE DEFAULT NULL;
  DECLARE alpha4 DOUBLE DEFAULT NULL;

  DECLARE delta0 DOUBLE DEFAULT NULL;
  DECLARE delta1 DOUBLE DEFAULT NULL;
  DECLARE delta2 DOUBLE DEFAULT NULL;
  DECLARE eta0 DOUBLE DEFAULT NULL;
  DECLARE eta1 DOUBLE DEFAULT NULL;
  DECLARE vartheta0 DOUBLE DEFAULT NULL;
  
  DECLARE s_f0 INT DEFAULT NULL;
  DECLARE s_f1 INT DEFAULT NULL;
  DECLARE s_f2 INT DEFAULT NULL;
  DECLARE s_f3 INT DEFAULT NULL;
  DECLARE s_f4 INT DEFAULT NULL;

  DECLARE sign_change_neg INT DEFAULT NULL;
  DECLARE sign_change_pos INT DEFAULT NULL;
  DECLARE Nroots INT DEFAULT NULL;

  DECLARE y1_root DOUBLE;
  DECLARE y1 DOUBLE;
  DECLARE y2 DOUBLE;
  DECLARE y3 DOUBLE;
  DECLARE y4 DOUBLE;
  DECLARE x1 DOUBLE;
  DECLARE x2 DOUBLE;
  DECLARE x3 DOUBLE;
  DECLARE x4 DOUBLE;

  /**
   * x1 coordinate of intersection point on ellipse 1 for 
   * Bezout solution y1
   */
  DECLARE i INT;
  DECLARE yi DOUBLE;
  DECLARE yi_root DOUBLE;
  DECLARE yi_e1_x1 DOUBLE;
  DECLARE yi_e1_x2 DOUBLE;
  DECLARE yi_e2_x1 DOUBLE;
  DECLARE yi_e2_x2 DOUBLE;
  DECLARE yi_x DOUBLE;
  
  DECLARE abc_a DOUBLE;
  DECLARE abc_b DOUBLE;
  DECLARE abc_c DOUBLE;
  DECLARE abc_D DOUBLE;

  DECLARE Quad1 INT;
  DECLARE Quad2 INT;
  DECLARE Quad3 INT;
  DECLARE Quad4 INT;

  DECLARE theta_0 DOUBLE;
  DECLARE theta_1 DOUBLE;

  /**
   * We convert from degrees to arcseconds
   */
  SET e1_a = 3600 * GREATEST(ie1_ra_err, ie1_decl_err);
  SET e1_b = 3600 * LEAST(ie1_ra_err, ie1_decl_err);
  IF ie1_ra_err > ie1_decl_err THEN
    /*TODO: adjust*/
    SET e1_pa = 70;
  ELSE 
    SET e1_pa = 0;
  END IF;
  SET e2_a = 3600 * GREATEST(ie2_ra_err, ie2_decl_err);
  SET e2_b = 3600 * LEAST(ie2_ra_err, ie2_decl_err);
  IF ie2_ra_err > ie2_decl_err THEN
    SET e2_pa = 120;
  ELSE 
    SET e2_pa = 0;
  END IF;

  SET e2_h = 3600 * (ie1_ra - ie2_ra);
  SET e2_k = 3600 * (ie2_decl - ie1_decl);

  SET theta_rot = RADIANS(e1_pa - 90);
  SET e2_phi = RADIANS(e2_pa - e1_pa);

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
    SET intersect = FALSE;
    SET ready = TRUE;
  END IF;

  IF ready = FALSE THEN
    IF distance <= (e1_b + e2_b) THEN
      SET intersect = TRUE;
      SET ready = TRUE;
    END IF;
  END IF;

  /**
   * If the ellipses are to far there is separation and 
   * the ellipses do not intersect.
   * If the ellipses are to close there is intersection 
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
      SET intersect = TRUE;
    ELSE
      SET intersect = FALSE;
    END IF;
  
  END IF; 
  
  /* RETURN intersect;
   * And here we go further,
   * we will compute the points of intersection of the two ellipses.
   * TODO: check overlap
   * Then we calculate the area integrating from theta_0 to theta_1
   */

  IF intersect = TRUE THEN
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
          WHEN 1 THEN SET x1 = yi_x;
          WHEN 2 THEN SET x2 = yi_x;
          WHEN 3 THEN SET x3 = yi_x;
          WHEN 4 THEN SET x4 = yi_x1;
        END CASE;
        SET i = i + 1;
      END WHILE;
      /* Now that we have the intersection points, we will calculate
       * the area of intersection. 
       * We need two angles for this: theta_0 and theta_1,
       * but how do we now the orientation?
       * Therefore we need to know whether the center of e1 is inside
       * the area of intersection (i.e. inside e2), and vv center
       * of e2 inside e1?
       */
      /* First we order the points from quadrant 1-4*/
      CASE Nroots
        WHEN 2 THEN
          IF ATAN(y1 / x1) > 0 THEN
            IF x1 > 0 THEN
              SET Quad1 = 1;
            ELSE 
              SET Quad1 = 3;
            END IF;
          ELSE
            IF x1 > 0 THEN
              SET Quad1 = 4;
            ELSE 
              SET Quad1 = 2;
            END IF;
          END IF;
          IF ATAN(y2 / x2) > 0 THEN
            IF x2 > 0 THEN
              SET Quad2 = 1;
            ELSE 
              SET Quad2 = 3;
            END IF;
          ELSE
            IF x2 > 0 THEN
              SET Quad2 = 4;
            ELSE 
              SET Quad2 = 2;
            END IF;
          END IF;
          /* Check whether C1=(0,0) is inside e2*/
          IF e2_q3 < 0 THEN
            /* C1 inside e2 */
          ELSE
          END IF;
          SET theta_0 = ATAN(y1 / x1);
          SET theta_1 = ATAN(y2 / x2);
        WHEN 3 THEN
          SET theta_0 = 0;
          SET theta_1 = 0;
        WHEN 4 THEN
          SET theta_0 = 0;
          SET theta_1 = 0;
      END CASE;
    ELSE
      /* intersect AND 0 roots => overlap */
      SET weight = 1;
    END IF;
  ELSE
    SET weight = -1;
  END IF;

  SET ointersect = intersect;
  SET onroots = Nroots;
  SET oalpha4 = alpha4;
  SET oalpha3 = alpha3;
  SET oalpha2 = alpha2;
  SET oalpha1 = alpha1;
  SET oalpha0 = alpha0;
  SET oe2_q3 = e2_q3;
  SET oy1 = y1;
  SET oy2 = y2;
  SET oy3 = y3;
  SET oy4 = y4;
  SET ox1 = x1;
  SET ox2 = x2;
  SET ox3 = x3;
  SET ox4 = x4;
  SET oquad1 = Quad1;
  SET oquad2 = Quad2;
  SET oquad3 = Quad3;
  SET oquad4 = Quad4;
  SET otheta_0 = DEGREES(theta_0);
  SET otheta_1 = DEGREES(theta_1);
  SET oweight = weight;
  /*SET oy1_e1_x1 = y1_e1_x1;
  SET oy1_e1_x2 = y1_e1_x2;
  SET oy1_e2_x1 = y1_e2_x1;
  SET oy1_e2_x2 = y1_e2_x2;
  SET oy2_e1_x1 = y2_e1_x1;
  SET oy2_e1_x2 = y2_e1_x2;
  SET oy2_e2_x1 = y2_e2_x1;
  SET oy2_e2_x2 = y2_e2_x2;
  SET oy3_e1_x1 = y3_e1_x1;
  SET oy3_e1_x2 = y3_e1_x2;
  SET oy3_e2_x1 = y3_e2_x1;
  SET oy3_e2_x2 = y3_e2_x2;
  SET oy4_e1_x1 = y4_e1_x1;
  SET oy4_e1_x2 = y4_e1_x2;
  SET oy4_e2_x1 = y4_e2_x1;
  SET oy4_e2_x2 = y4_e2_x2;*/

END;
//

DELIMITER ;
