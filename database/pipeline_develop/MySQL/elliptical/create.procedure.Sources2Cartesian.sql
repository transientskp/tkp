DROP PROCEDURE IF EXISTS Sources2Cartesian;

DELIMITER //

/*+--------------------------------------------------------------------+
 *| This procedure converts the spherical coordinates of two close-by  |
 *| sources to 2D-Cartesian coordinates.                               |
 *| The Cartesian coordinates may then be used in other procedures/    |
 *| functions that determine whether these sources can be associated.  |
 *|                                                                    |
 *| Input source 1 determines the orientation of the tangent plane onto|
 *| which source 2 will be projected.                                  |
 *| The tangent plane has a normal vector u, which is a unit vector    |
 *| (u1,u2,u3) pointing in the (ra,decl) direction. The x-axis of the  |
 *| plane is determined by the westward vector, and the y-axis by the  |
 *| northward vector.                                                  |
 *| We do not use PA angles, when that comes into play we need to      |
 *| add another vector along the major axis to determine a rotation    |
 *| angle.                                                             |
 *| (See TKP_DB_source_assoc_ellipse.pdf in repository for details.)   |
 *|                                                                    |
 *+--------------------------------------------------------------------+
 *| INPUT params:                                                      |
 *|     prefix ie1_*      : input params for source/ellipse 1          |
 *|     ra & decl         : centre of source [degrees]                 |
 *|     ra_err & decl_err : errors on ra & decl [arcsec]               |
 *|    (angles            : in degrees)                                |
 *|                                                                    |
 *+--------------------------------------------------------------------+
 *| OUTPUT params:                                                     |
 *|  unitvectors:                                                      |
 *|           u: towards source 1                                      |
 *|           v: towards source 2                                      |
 *|           w: unit vector in westward direction                     |
 *|           n: unit vector in northward direction                    |
 *|       zeta : angle between w and (v - u) [degrees]                 |
 *+--------------------------------------------------------------------+
 *| No need to implement yet:                                          |
 *|  theta_rot : rotation to be performed to go from the ra,decl       |
 *|              system to the Cartesian system (theta_rot is oriented |
 *|              counterclockwise from west to north) [degrees]        |
 *+--------------------------------------------------------------------+
 *|   distance : distance between sources [arcsec]                     |
 *|       a, b : semi-major & -minor axes [arcsec]                     |
 *|      (h, k): centre (Cartesian) coordinates of E2 in tangent plane |
 *|              at E1 [arcsec,arcsec]                                 |
 *|      e2_phi: orientation of E2's major-axis in this system, going  |
 *|              from x-axis to y-axis counterclockwise [degrees]      | 
 *|              (note: this angle is small)                           | 
 *+--------------------------------------------------------------------+
 *| It is assumed that a preselection is done so that the two input    |
 *| sources are close together.                                        |
 *|                                                                    |
 *+--------------------------------------------------------------------+
 *| No ra-inflation has to be taken into account.                      |
 *|                                                                    |
 *+--------------------------------------------------------------------+
 *|                          Bart Scheers                              |
 *|                     University of Amsterdam                        |
 *|                          2009-09-28                                |
 *+--------------------------------------------------------------------+
 */
CREATE PROCEDURE Sources2Cartesian(IN ie1_ra DOUBLE
                                  ,IN ie1_decl DOUBLE
                                  ,IN ie1_ra_err DOUBLE
                                  ,IN ie1_decl_err DOUBLE
                                  /*,IN ie1_pa DOUBLE*/
                                  ,IN ie2_ra DOUBLE
                                  ,IN ie2_decl DOUBLE
                                  ,IN ie2_ra_err DOUBLE
                                  ,IN ie2_decl_err DOUBLE
                                  /*,IN ie2_pa DOUBLE*/
                                  ,OUT oe1_pa DOUBLE
                                  ,OUT oe2_pa DOUBLE
                                  ,OUT ou1 DOUBLE
                                  ,OUT ou2 DOUBLE
                                  ,OUT ou3 DOUBLE
                                  ,OUT os1_w1 DOUBLE
                                  ,OUT os1_w2 DOUBLE
                                  ,OUT os1_w3 DOUBLE
                                  ,OUT os1_n1 DOUBLE
                                  ,OUT os1_n2 DOUBLE
                                  ,OUT os1_n3 DOUBLE
                                  ,OUT ov1 DOUBLE
                                  ,OUT ov2 DOUBLE
                                  ,OUT ov3 DOUBLE
                                  ,OUT os2_w1 DOUBLE
                                  ,OUT os2_w2 DOUBLE
                                  ,OUT os2_w3 DOUBLE
                                  ,OUT os2_n1 DOUBLE
                                  ,OUT os2_n2 DOUBLE
                                  ,OUT os2_n3 DOUBLE
                                  ,OUT ozeta DOUBLE
                                  ,OUT odistance DOUBLE
                                  ,OUT otheta_rot DOUBLE
                                  ,OUT oe1_a DOUBLE
                                  ,OUT oe1_b DOUBLE
                                  ,OUT oe1_phi DOUBLE
                                  ,OUT oe2_h DOUBLE
                                  ,OUT oe2_k DOUBLE
                                  ,OUT oe2_a DOUBLE
                                  ,OUT oe2_b DOUBLE
                                  ,OUT oe2_phi DOUBLE
                                  ,OUT oe2_h_acc DOUBLE
                                  ,OUT oe2_k_acc DOUBLE
                                  ,OUT oe2_phi_acc DOUBLE
                                  ) 

BEGIN
  
  DECLARE e1_a, e1_b, e1_phi, e2_h, e2_k, e2_a, e2_b, e2_phi DOUBLE DEFAULT NULL;
  DECLARE theta_rot, e2_h_acc, e2_k_acc, e2_phi_acc DOUBLE DEFAULT NULL;
  DECLARE e1_pa, e2_pa DOUBLE DEFAULT NULL;
  DECLARE zeta, d_p1, d_p2, d_p3 DOUBLE;
  DECLARE u1, u2, u3, v1, v2, v3 DOUBLE DEFAULT NULL;
  DECLARE s1_w1,s1_w2,s1_w3,s2_w1,s2_w2,s2_w3 DOUBLE DEFAULT NULL;
  DECLARE s1_n1,s1_n2,s1_n3,s2_n1,s2_n2,s2_n3 DOUBLE DEFAULT NULL;
  DECLARE distance DOUBLE DEFAULT NULL;

  SET e1_a = GREATEST(ie1_ra_err, ie1_decl_err);
  SET e1_b = LEAST(ie1_ra_err, ie1_decl_err);
  IF ie1_ra_err > ie1_decl_err THEN
    SET e1_pa = 90;
  ELSE 
    SET e1_pa = 0;
  END IF;
  SET oe1_a = e1_a;
  SET oe1_b = e1_b;
  SET oe1_pa = e1_pa;
  
  SET e2_a = GREATEST(ie2_ra_err, ie2_decl_err);
  SET e2_b = LEAST(ie2_ra_err, ie2_decl_err);
  IF ie2_ra_err > ie2_decl_err THEN
    SET e2_pa = 90;
  ELSE 
    SET e2_pa = 0;
  END IF;
  SET oe2_a = e2_a;
  SET oe2_b = e2_b;
  SET oe2_pa = e2_pa;

  /* Reference source 1 vector */
  SET u1 = COS(RADIANS(ie1_decl)) * COS(RADIANS(ie1_ra));
  SET u2 = COS(RADIANS(ie1_decl)) * SIN(RADIANS(ie1_ra));
  SET u3 = SIN(RADIANS(ie1_decl));
  SET ou1 = u1;
  SET ou2 = u2;
  SET ou3 = u3;

  /* Westward vector at source 1 */
  SET s1_w1 = SIN(RADIANS(ie1_ra));
  SET s1_w2 = -COS(RADIANS(ie1_ra));
  SET s1_w3 = 0;
  SET os1_w1 = s1_w1;
  SET os1_w2 = s1_w2;
  SET os1_w3 = s1_w3;
  
  /* Northward vector at source 1 */
  SET s1_n1 = -SIN(RADIANS(ie1_decl)) * COS(RADIANS(ie1_ra));
  SET s1_n2 = -SIN(RADIANS(ie1_decl)) * SIN(RADIANS(ie1_ra));
  SET s1_n3 = COS(RADIANS(ie1_decl));
  SET os1_n1 = s1_n1;
  SET os1_n2 = s1_n2;
  SET os1_n3 = s1_n3;
  
  /* Unit vector pointing to source 2 */
  SET v1 = COS(RADIANS(ie2_decl)) * COS(RADIANS(ie2_ra));
  SET v2 = COS(RADIANS(ie2_decl)) * SIN(RADIANS(ie2_ra));
  SET v3 = SIN(RADIANS(ie2_decl));
  SET ov1 = v1;
  SET ov2 = v2;
  SET ov3 = v3;

  /* Westward vector at source 2 */
  SET s2_w1 = SIN(RADIANS(ie2_ra));
  SET s2_w2 = -COS(RADIANS(ie2_ra));
  SET s2_w3 = 0;
  SET os2_w1 = s2_w1;
  SET os2_w2 = s2_w2;
  SET os2_w3 = s2_w3;
  
  /* Northward vector at source 1 */
  SET s2_n1 = -SIN(RADIANS(ie2_decl)) * COS(RADIANS(ie2_ra));
  SET s2_n2 = -SIN(RADIANS(ie2_decl)) * SIN(RADIANS(ie2_ra));
  SET s2_n3 = COS(RADIANS(ie2_decl));
  SET os2_n1 = s2_n1;
  SET os2_n2 = s2_n2;
  SET os2_n3 = s2_n3;
  
  SET distance = 3600 * DEGREES(2 * ASIN(getVectorLength(v1 - u1, v2 - u2, v3 - u3) / 2));
  SET odistance = distance;
  
  /* d_p is the vector v - u */
  SET d_p1 = v1 - u1;
  SET d_p2 = v2 - u2;
  SET d_p3 = v3 - u3;
  /* angle between d_p and s1_w is used for determining h and k */
  SET zeta = ACOS(dotProduct(d_p1,d_p2,d_p3,s1_w1,s1_w2,s1_w3)/getVectorLength(d_p1,d_p2,d_p3));
  SET ozeta = DEGREES(zeta);

  SET e2_h = distance * COS(zeta); 
  SET e2_k = distance * SIN(zeta);
  SET oe2_h = e2_h;
  SET oe2_k = e2_k;

  SET e2_phi = DEGREES(ACOS(dotProduct(s1_n1,s1_n2,s1_n3,s2_n1,s2_n2,s2_n3))) + 90 - e2_pa;
  SET oe2_phi = e2_phi;

  /* now we have these guys, we need to take into account rotation */
  SET theta_rot = e1_pa - 90;
  SET otheta_rot = theta_rot;

  SET e2_h_acc =  e2_h * COS(RADIANS(theta_rot)) + e2_k * SIN(RADIANS(theta_rot));
  SET e2_k_acc = -e2_h * SIN(RADIANS(theta_rot)) + e2_k * COS(RADIANS(theta_rot));
  SET e2_phi_acc = e2_phi + theta_rot;

  SET oe2_h_acc = e2_h_acc;
  SET oe2_k_acc = e2_k_acc;
  SET oe2_phi_acc = e2_phi_acc;

END;
//

DELIMITER ;
