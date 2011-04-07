DROP PROCEDURE IF EXISTS Sources2Cartesian;

DELIMITER //

/**
 * This boolean function determines if two (nearby) ellipses intersect.
 * The arguments for the two ellipses i (ei_*) are the centre (ra,decl)
 * and its errors (ra_err,decl_err), and the position angle. 
 * All units are in degrees.
 * It is assumed that a preselection is done so that the two ellipses
 * are close together.
 * No ra-inflation has to be taken into account.
 * INPUT params:
 *  all units in degrees
 *
 * OUTPUT params:
 *  all units in arcsec, oe2_phi in degrees
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
                                  ,OUT ou1 DOUBLE
                                  ,OUT ou2 DOUBLE
                                  ,OUT ou3 DOUBLE
                                  ,OUT ov1 DOUBLE
                                  ,OUT ov2 DOUBLE
                                  ,OUT ov3 DOUBLE
                                  ,OUT ow1 DOUBLE
                                  ,OUT ow2 DOUBLE
                                  ,OUT ow3 DOUBLE
                                  ,OUT ogamma DOUBLE
                                  ,OUT odelta DOUBLE
                                  ,OUT otheta_rot DOUBLE
                                  ,OUT obeta DOUBLE
                                  ,OUT odistance DOUBLE
                                  ,OUT oe1_a DOUBLE
                                  ,OUT oe1_b DOUBLE
                                  ,OUT oe1_phi DOUBLE
                                  ,OUT oe2_h DOUBLE
                                  ,OUT oe2_k DOUBLE
                                  ,OUT oe2_a DOUBLE
                                  ,OUT oe2_b DOUBLE
                                  ,OUT oe2_phi DOUBLE
                                  ) 

BEGIN
  
  DECLARE e1_a, e1_b, e1_phi, e2_h, e2_k, e2_a, e2_b, e2_phi DOUBLE DEFAULT NULL;
  /* u is the vector to Source1, v the vector to Source 2, and
   * w the vector from Source1 in the westward direction 
   */
  DECLARE e1_pa, e2_pa, cos_decl1, cos_decl2, theta_rot, beta DOUBLE DEFAULT NULL;
  DECLARE u1, u2, u3, v1, v2, v3, w1, w2, w3, gamma, delta DOUBLE DEFAULT NULL;
  DECLARE distance DOUBLE DEFAULT NULL;

  SET e1_a = 3600 * GREATEST(ie1_ra_err, ie1_decl_err);
  SET e1_b = 3600 * LEAST(ie1_ra_err, ie1_decl_err);
  IF ie1_ra_err > ie1_decl_err THEN
    SET e1_pa = 90;
  ELSE 
    SET e1_pa = 0;
  END IF;
  SET oe1_a = e1_a;
  SET oe1_b = e1_b;
  SET oe1_phi = e1_phi;
  
  SET e2_a = 3600 * GREATEST(ie2_ra_err, ie2_decl_err);
  SET e2_b = 3600 * LEAST(ie2_ra_err, ie2_decl_err);
  IF ie2_ra_err > ie2_decl_err THEN
    SET e2_pa = 90;
  ELSE 
    SET e2_pa = 0;
  END IF;
  SET oe2_a = e2_a;
  SET oe2_b = e2_b;
  SET oe2_phi = e2_phi;

  SET cos_decl1 = COS(RADIANS(ie1_decl));
  SET u1 = cos_decl1 * COS(RADIANS(ie1_ra));
  SET u2 = cos_decl1 * SIN(RADIANS(ie1_ra));
  SET u3 = SIN(RADIANS(ie1_decl));
  SET ou1 = u1;
  SET ou2 = u2;
  SET ou3 = u3;

  SET cos_decl2 = COS(RADIANS(ie2_decl));
  SET v1 = cos_decl2 * COS(RADIANS(ie2_ra));
  SET v2 = cos_decl2 * SIN(RADIANS(ie2_ra));
  SET v3 = SIN(RADIANS(ie2_decl));
  SET ov1 = v1;
  SET ov2 = v2;
  SET ov3 = v3;

  SET w1 = cos_decl1 * COS(RADIANS(ie2_ra));
  SET w2 = cos_decl1 * SIN(RADIANS(ie2_ra));
  SET w3 = SIN(RADIANS(ie1_decl));
  SET ow1 = w1;
  SET ow2 = w2;
  SET ow3 = w3;

  SET gamma = ACOS(v1 * w1 + v2 * w2 + v3 * w3);
  SET delta = 2 * ASIN(SQRT(POW(w1 - v1, 2) + POW(w2 - v2, 2) + POW(w3 - v3, 2)) / 2);
  SET ogamma = gamma;
  SET odelta = delta;

  SET theta_rot = e1_pa - 90;
  SET otheta_rot = theta_rot;
  SET beta = gamma - theta_rot;
  SET obeta = beta;

  SET distance = 3600 * DEGREES(2 * ASIN(SQRT(POW(v1 - u1, 2) + POW(v2 - u2, 2) + POW(v3 - u3, 2)) / 2));
  SET odistance = distance;

  SET e2_h = distance * COS(RADIANS(beta));
  SET e2_k = distance * SIN(RADIANS(beta));
  SET e2_phi = e2_pa - e1_pa;

  SET oe2_h = e2_h;
  SET oe2_k = e2_k;
  SET oe2_phi = e2_phi;

END;
//

DELIMITER ;
