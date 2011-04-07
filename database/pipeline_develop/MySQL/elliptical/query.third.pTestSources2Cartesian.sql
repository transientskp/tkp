/*
 *
 */

CALL pTestSources2Cartesian();

SELECT iter
      ,e1_ra
      ,e1_decl
      ,e1_ra_err
      ,e1_decl_err
      ,e2_ra
      ,e2_decl
      ,e2_ra_err
      ,e2_decl_err
  FROM tmp_weight_ells_intersect;
;

SELECT "";

SELECT iter 
      ,e1_a
      ,e1_b
      ,e2_h
      ,e2_k
      ,e2_a
      ,e2_b
      ,e2_phi
      ,weight
  FROM tmp_weight_ells_intersect;

