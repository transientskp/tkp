DROP FUNCTION IF EXISTS doIntersect;

DELIMITER //

/**
 * This boolean function determines if two (nearby) ellipses intersect.
 * The arguments for the two ellipses i (ei_*) are the centre (ra,decl)
 * and its errors (ra_err,decl_err), and the position angle. 
 * All units are in degrees.
 * It is assumed that a preselection is done so that the two ellipses
 * are close together.
 * No ra-inflation has to be taken into account.
 *
 * TODO: upgrade to ra_err & decl_err in arcsec
 * and to correctly set h & k
 */
CREATE FUNCTION doIntersect(ie1_ra DOUBLE
                           ,ie1_decl DOUBLE
                           ,ie1_ra_err DOUBLE
                           ,ie1_decl_err DOUBLE
                           ,ie1_pa DOUBLE
                           ,ie2_ra DOUBLE
                           ,ie2_decl DOUBLE
                           ,ie2_ra_err DOUBLE
                           ,ie2_decl_err DOUBLE
                           ,ie2_pa DOUBLE
                           ) RETURNS BOOLEAN
DETERMINISTIC

BEGIN
  
  SET e1_a = 3600 * GREATEST(ie1_ra_err, ie1_decl_err);
  SET e1_b = 3600 * LEAST(ie1_ra_err, ie1_decl_err);
  IF ie1_ra_err > ie1_decl_err THEN
    SET e1_pa = 90;
  ELSE 
    SET e1_pa = 0;
  END IF;
  
  SET e2_a = 3600 * GREATEST(ie2_ra_err, ie2_decl_err);
  SET e2_b = 3600 * LEAST(ie2_ra_err, ie2_decl_err);
  IF ie2_ra_err > ie2_decl_err THEN
    SET e2_pa = 90;
  ELSE 
    SET e2_pa = 0;
  END IF;

  /* TODO
   * this need to be set more accurately, using dot procducts
   */
  SET e2_h = 3600 * (ie1_ra - ie2_ra);
  SET e2_k = 3600 * (ie2_decl - ie1_decl);

  SET theta_rot = RADIANS(e1_pa - 90);
  SET e2_phi = RADIANS(e2_pa - e1_pa);

  SET e2_h_acc =  e2_h * COS(theta_rot) + e2_k * SIN(theta_rot);
  SET e2_k_acc = -e2_h * SIN(theta_rot) + e2_k * COS(theta_rot);

  /* We drop the _acc suffix */
  SET e2_h = e2_h_acc;
  SET e2_k = e2_k_acc;

  RETURN doEllipsesIntersect(e1_a, e1_b, e2_h, e2_k, e2_a, e2_b, e2_phi);

END;
//

DELIMITER ;
