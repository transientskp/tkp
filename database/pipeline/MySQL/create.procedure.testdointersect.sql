USE pipeline;

DROP PROCEDURE IF EXISTS testIntersect;
DROP PROCEDURE IF EXISTS testdointersect;

DELIMITER //

/**
 * To test procedure:
 * This takes two ellipses as input:
 * E1: a = 4, b = 3, PA = 70 degrees, (we locate it at the origin)
 * E2: a = 5, b = 3, PA = 120 degrees, Centre at -7.25, -1.7 wrt E1
 * These ellipses intersect.
 * From the quartic polynomial R(t) follow two real roots
 * t1 = 0.791566537067,
 * t2 = -1.498920695821
 * these represent the y-coordinates of the intersection points,
 * (to know the x we have to insert the y in the E1 or E2 eqn.)
 * and two imaginary roots
 * t3/4 = -7.433023206969 ± 7.510878568308i
 *

call testintersect(0,0,90,5,3.5,-7.25,-1.7,0,4.5,3.5,@distance,@otheta_rot,@oe2_phi,@oe1_q1,@oe1_q3,@oe1_q6,@oe2_h,@oe2_k,@oe2_q1,@oe2_q2,@oe2_q3,@oe2_q4,@oe2_q5,@oe2_q6,@alpha0,@alpha1,@alpha2,@alpha3,@alpha4,@delta0,@delta1,@delta2,@eta0,@eta1,@vartheta0,@s_nf0,@s_nf1,@s_nf2,@s_nf3,@s_nf4,@s_pf0,@s_pf1,@s_pf2,@s_pf3,@s_pf4,@sign_change_neg,@sign_change_pos,@tofar,@intersect);

 * watch the values

select @distance,@otheta_rot,@oe2_phi,@oe1_q1,@oe1_q3,@oe1_q6;
select @oe2_h,@oe2_k,@oe2_q1,@oe2_q2,@oe2_q3,@oe2_q4,@oe2_q5,@oe2_q6;
select @alpha0,@alpha1,@alpha2,@alpha3,@alpha4;
select @gamma0, @gamma1,@gamma2,@gamma3,@delta0,@delta1,@delta2;
select @varepsilon0,@varepsilon1,@varepsilon2,@zeta0,@zeta1,@eta0,@eta1,@vartheta0;
select @s_nf0,@s_nf1,@s_nf2,@s_nf3,@s_nf4,@s_pf0,@s_pf1,@s_pf2,@s_pf3,@s_pf4,@sign_change_neg,@sign_change_pos,@tofar,@intersect;

 *
 */

CREATE PROCEDURE testdointersect(IN ie1_ra DOUBLE
                              ,IN ie1_decl DOUBLE
                              ,IN ie1_pa DOUBLE
                              ,IN ie1_a DOUBLE
                              ,IN ie1_b DOUBLE
                              ,IN ie2_ra DOUBLE
                              ,IN ie2_decl DOUBLE
                              ,IN ie2_pa DOUBLE
                              ,IN ie2_a DOUBLE
                              ,IN ie2_b DOUBLE
                              ,OUT odistance DOUBLE
                              ,OUT otheta_rot DOUBLE
                              ,OUT oe2_phi DOUBLE
                              ,OUT oe1_q1 DOUBLE
                              ,OUT oe1_q3 DOUBLE
                              ,OUT oe1_q6 DOUBLE
                              ,OUT oe2_h DOUBLE
                              ,OUT oe2_k DOUBLE
                              ,OUT oe2_q1 DOUBLE
                              ,OUT oe2_q2 DOUBLE
                              ,OUT oe2_q3 DOUBLE
                              ,OUT oe2_q4 DOUBLE
                              ,OUT oe2_q5 DOUBLE
                              ,OUT oe2_q6 DOUBLE
                              ,OUT oalpha0 DOUBLE
                              ,OUT oalpha1 DOUBLE
                              ,OUT oalpha2 DOUBLE
                              ,OUT oalpha3 DOUBLE
                              ,OUT oalpha4 DOUBLE
                              ,OUT odelta0 DOUBLE
                              ,OUT odelta1 DOUBLE
                              ,OUT odelta2 DOUBLE
                              ,OUT oeta0 DOUBLE
                              ,OUT oeta1 DOUBLE
                              ,OUT ovartheta0 DOUBLE
                              ,OUT os_nf0 INT
                              ,OUT os_nf1 INT
                              ,OUT os_nf2 INT
                              ,OUT os_nf3 INT
                              ,OUT os_nf4 INT
                              ,OUT os_pf0 INT
                              ,OUT os_pf1 INT
                              ,OUT os_pf2 INT
                              ,OUT os_pf3 INT
                              ,OUT os_pf4 INT
                              ,OUT osign_change_neg INT
                              ,OUT osign_change_pos INT
                              ,OUT otofar BOOLEAN
                              ,OUT ointersect BOOLEAN
                              )

BEGIN
  DECLARE tofar BOOLEAN DEFAULT FALSE;
  DECLARE intersect BOOLEAN DEFAULT FALSE;

  DECLARE theta_rot DOUBLE DEFAULT NULL;
  DECLARE e2_phi DOUBLE DEFAULT NULL;

  DECLARE e1_q1 DOUBLE DEFAULT NULL;
  DECLARE e1_q3 DOUBLE DEFAULT NULL;
  DECLARE e1_q6 DOUBLE DEFAULT NULL;

  DECLARE distance DOUBLE DEFAULT NULL;
  DECLARE e2_h DOUBLE DEFAULT NULL;
  DECLARE e2_k DOUBLE DEFAULT NULL;
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
  
  DECLARE s_nf0 INT DEFAULT NULL;
  DECLARE s_nf1 INT DEFAULT NULL;
  DECLARE s_nf2 INT DEFAULT NULL;
  DECLARE s_nf3 INT DEFAULT NULL;
  DECLARE s_nf4 INT DEFAULT NULL;
  DECLARE s_pf0 INT DEFAULT NULL;
  DECLARE s_pf1 INT DEFAULT NULL;
  DECLARE s_pf2 INT DEFAULT NULL;
  DECLARE s_pf3 INT DEFAULT NULL;
  DECLARE s_pf4 INT DEFAULT NULL;

  DECLARE sign_change_neg INT DEFAULT NULL;
  DECLARE sign_change_pos INT DEFAULT NULL;
  DECLARE Nroots INT DEFAULT NULL;

  DECLARE i1xy DOUBLE DEFAULT NULL;
  DECLARE i1x DOUBLE DEFAULT NULL;
  DECLARE i1y DOUBLE DEFAULT NULL;
  DECLARE i1z DOUBLE DEFAULT NULL;
  DECLARE i2xy DOUBLE DEFAULT NULL;
  DECLARE i2x DOUBLE DEFAULT NULL;
  DECLARE i2y DOUBLE DEFAULT NULL;
  DECLARE i2z DOUBLE DEFAULT NULL;

  /** 
   * This test can be executed immediately, to know
   * whether one is containing the other.
   */
  SET distance = SQRT((ie2_ra - ie1_ra) * (ie2_ra - ie1_ra) 
                    + (ie2_decl - ie1_decl) * (ie2_decl - ie1_decl));
  IF distance > (ie1_a + ie2_a) THEN
    SET tofar = TRUE;
  ELSE 
    SET tofar = FALSE;
  END IF;

  /*IF tofar = FALSE THEN*/

  /**
   * We rotate in order to align the coordinate system to 
   * the orientation of the major axis.
   */
  SET theta_rot = ie1_pa - 90;
  SET e2_phi = ie2_pa - ie1_pa;

  /**
   * TODO: Handle this in declare statements
   */
  SET e1_q1 = ie1_a * ie1_a;
  SET e1_q6 = ie1_b * ie1_b;
  SET e1_q3 = -e1_q1 * e1_q6;

  SET e2_h = (ie1_ra - ie2_ra) * COS(RADIANS(theta_rot)) 
             + (ie2_decl - ie1_decl) * SIN(RADIANS(theta_rot));
  SET e2_k = -(ie1_ra - ie2_ra) * SIN(RADIANS(theta_rot)) 
             + (ie2_decl - ie1_decl) * COS(RADIANS(theta_rot));

  SET e2_q1 = ie2_a * ie2_a * COS(RADIANS(e2_phi)) * COS(RADIANS(e2_phi))
              + ie2_b * ie2_b * SIN(RADIANS(e2_phi)) * SIN(RADIANS(e2_phi));
  SET e2_q6 = ie2_a * ie2_a * SIN(RADIANS(e2_phi)) * SIN(RADIANS(e2_phi))
              + ie2_b * ie2_b * COS(RADIANS(e2_phi)) * COS(RADIANS(e2_phi));
  SET e2_q4 = (ie2_b * ie2_b - ie2_a * ie2_a) * SIN(2 * RADIANS(e2_phi));
  SET e2_q2 = -2 * e2_k * e2_q1 - e2_h * e2_q4;
  SET e2_q3 = e2_h * e2_h * e2_q6 + e2_k * e2_k * e2_q1 
              + e2_h * e2_k * e2_q4 - ie2_a * ie2_a * ie2_b * ie2_b;
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

  /*IF alpha4 < 0 THEN
    SET alpha4 = -1 * alpha4;
    SET alpha3 = -1 * alpha3;
    SET alpha2 = -1 * alpha2;
    SET alpha1 = -1 * alpha1;
    SET alpha0 = -1 * alpha0;
  END IF;*/

  SET alpha0 = alpha0 / alpha4;
  SET alpha1 = alpha1 / alpha4;
  SET alpha2 = alpha2 / alpha4;
  SET alpha3 = alpha3 / alpha4;
  SET alpha4 = 1;

  SET delta2 = ((3 * alpha3 * alpha3) / (16 * alpha4)) - (alpha2/2);
  SET delta1 = ((alpha2 * alpha3) / (8 * alpha4)) - ((3 * alpha1)/4);
  SET delta0 = (alpha1 * alpha3 / (16 * alpha4)) - alpha0;
  SET eta1 = (delta1/delta2) * (3 * alpha3 - (4 * (alpha4 * delta1 / delta2))) - (2 * alpha2 - (4 * (alpha4 * delta0 / delta2))); 
  SET eta0 = (delta0/delta2) * (3 * alpha3 - (4 * (alpha4 * delta1 / delta2))) - (3 * alpha3);
  SET vartheta0 = (eta0/eta1) * (delta1 - (eta0 * delta2 / eta1)) - delta0; 

  /**
   * Determine sign for -infty
   */
  SET s_nf0 = SIGN(alpha4);
  SET s_nf1 = SIGN((-4*alpha4));
  SET s_nf2 = SIGN(delta2);
  SET s_nf3 = SIGN(-eta1);
  SET s_nf4 = SIGN(vartheta0);

  SET sign_change_neg = 0;
  
  IF s_nf0 * s_nf1 < 0 THEN
    SET sign_change_neg = sign_change_neg + 1;
  END IF;
  IF s_nf1 * s_nf2 < 0 THEN
    SET sign_change_neg = sign_change_neg + 1;
  END IF;
  IF s_nf2 * s_nf3 < 0 THEN
    SET sign_change_neg = sign_change_neg + 1;
  END IF;
  IF s_nf3 * s_nf4 < 0 THEN
    SET sign_change_neg = sign_change_neg + 1;
  END IF;

  /**
   * Determine sign for +infty
   */
  SET s_pf0 = SIGN(alpha4);
  SET s_pf1 = SIGN((4*alpha4));
  SET s_pf2 = SIGN(delta2);
  SET s_pf3 = SIGN(eta1);
  SET s_pf4 = SIGN(vartheta0);

  SET sign_change_pos = 0;
  
  IF s_pf0 * s_pf1 < 0 THEN
    SET sign_change_pos = sign_change_pos + 1;
  END IF;
  IF s_pf1 * s_pf2 < 0 THEN
    SET sign_change_pos = sign_change_pos + 1;
  END IF;
  IF s_pf2 * s_pf3 < 0 THEN
    SET sign_change_pos = sign_change_pos + 1;
  END IF;
  IF s_pf3 * s_pf4 < 0 THEN
    SET sign_change_pos = sign_change_pos + 1;
  END IF;

  SET Nroots = sign_change_neg - sign_change_pos;
  IF Nroots > 0 THEN
    SET intersect = TRUE;
  ELSE
    SET intersect = FALSE;
  END IF;
  
  /*END IF; RETURN intersect1;*/

  SET odistance = distance;
  SET otheta_rot = theta_rot;
  SET oe2_phi = e2_phi;
  SET oe1_q1 = e1_q1;
  SET oe1_q3 = e1_q3;
  SET oe1_q6 = e1_q6;
  SET oe2_h = e2_h;
  SET oe2_k = e2_k;
  SET oe2_q1 = e2_q1;
  SET oe2_q2 = e2_q2;
  SET oe2_q3 = e2_q3;
  SET oe2_q4 = e2_q4;
  SET oe2_q5 = e2_q5;
  SET oe2_q6 = e2_q6;
  SET oalpha0 = alpha0;
  SET oalpha1 = alpha1;
  SET oalpha2 = alpha2;
  SET oalpha3 = alpha3;
  SET oalpha4 = alpha4;
  SET odelta0 = delta0;
  SET odelta1 = delta1;
  SET odelta2 = delta2;
  SET oeta0 = eta0;
  SET oeta1 = eta1;
  SET ovartheta0 = vartheta0;
  SET os_nf0 = s_nf0;
  SET os_nf1 = s_nf1;
  SET os_nf2 = s_nf2;
  SET os_nf3 = s_nf3;
  SET os_nf4 = s_nf4;
  SET os_pf0 = s_pf0;
  SET os_pf1 = s_pf1;
  SET os_pf2 = s_pf2;
  SET os_pf3 = s_pf3;
  SET os_pf4 = s_pf4;
  SET osign_change_neg = sign_change_neg;
  SET osign_change_pos = sign_change_pos;
  SET otofar = tofar;
  SET ointersect = intersect;

END;
//

