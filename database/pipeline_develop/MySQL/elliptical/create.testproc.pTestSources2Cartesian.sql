DROP PROCEDURE IF EXISTS pTestSources2Cartesian;

DELIMITER //

/**
 *
 *
 */

CREATE PROCEDURE pTestSources2Cartesian()

BEGIN
  DECLARE iter INT;
  DECLARE ie2_decl_incr DOUBLE;
  DECLARE ie1_ra, ie1_decl, ie1_ra_err, ie1_decl_err DOUBLE;
  DECLARE ie2_ra, ie2_decl, ie2_ra_err, ie2_decl_err DOUBLE;

  DECLARE oe1_pa, oe2_pa, ou1, ou2, ou3, ov1, ov2, ov3, ow1, ow2, ow3 DOUBLE;
  DECLARE ogamma, otheta_rot, obeta, odistance DOUBLE;
  DECLARE oe1_a, oe1_b, oe1_phi, oe2_h, oe2_k, oe2_a, oe2_b, oe2_phi, oweight DOUBLE;
  
  DROP TABLE IF EXISTS tmp_weight_ells_intersect;

  CREATE TABLE tmp_weight_ells_intersect (
    iter INT,
    e1_ra DOUBLE,
    e1_decl DOUBLE,
    e1_ra_err DOUBLE,
    e1_decl_err DOUBLE,
    e2_ra DOUBLE,
    e2_decl DOUBLE,
    e2_ra_err DOUBLE,
    e2_decl_err DOUBLE,
    e1_a DOUBLE,
    e1_b DOUBLE,
    e2_h DOUBLE,
    e2_k DOUBLE,
    e2_a DOUBLE,
    e2_b DOUBLE,
    e2_phi DOUBLE,
    weight DOUBLE
  ) ENGINE=InnoDB
  ;

  /* We keep source 1 fixed */
  SET ie1_ra = 100.0; 
  SET ie1_decl = 0;
  SET ie1_ra_err = 4; 
  SET ie1_decl_err = 3;
  /*SET ie1_pa = 70;*/

  /* We will move source 2 up north */
  SET ie2_ra = 99.998; 
  SET ie2_decl = 0;
  SET ie2_ra_err = 5; 
  SET ie2_decl_err = 2.5;
  /*SET ie2_pa = 120;*/

  SET iter = 1;
  SET ie2_decl_incr = 0.1;
  WHILE ie2_decl < 1 DO
    CALL Sources2Cartesian(ie1_ra
                          ,ie1_decl
                          ,ie1_ra_err
                          ,ie1_decl_err
                          /*,ie1_pa*/
                          ,ie2_ra
                          ,ie2_decl
                          ,ie2_ra_err
                          ,ie2_decl_err
                          /*,ie2_pa*/
                          ,oe1_pa
                          ,oe2_pa
                          ,ou1
                          ,ou2
                          ,ou3
                          ,ov1
                          ,ov2
                          ,ov3
                          ,ow1
                          ,ow2
                          ,ow3
                          ,ogamma
                          ,otheta_rot
                          ,obeta
                          ,odistance
                          ,oe1_a
                          ,oe1_b
                          ,oe1_phi
                          ,oe2_h
                          ,oe2_k
                          ,oe2_a
                          ,oe2_b
                          ,oe2_phi
                          )
    ;

    /*SET oweight = getWeightEllipticalIntersection2(oe1_a,oe1_b,oe2_h,oe2_k,oe2_a,oe2_b,oe2_phi);*/
    SET oweight = -100;

    INSERT INTO tmp_weight_ells_intersect
      (iter
      ,e1_ra
      ,e1_decl
      ,e1_ra_err
      ,e1_decl_err
      ,e2_ra
      ,e2_decl
      ,e2_ra_err
      ,e2_decl_err
      ,e1_a
      ,e1_b
      ,e2_h
      ,e2_k
      ,e2_a
      ,e2_b
      ,e2_phi
      ,weight
      )
    VALUES
      (iter
      ,ie1_ra
      ,ie1_decl
      ,ie1_ra_err
      ,ie1_decl_err
      ,ie2_ra
      ,ie2_decl
      ,ie2_ra_err
      ,ie2_decl_err
      ,oe1_a
      ,oe1_b
      ,oe2_h
      ,oe2_k
      ,oe2_a
      ,oe2_b
      ,oe2_phi
      ,oweight
      )
    ;
    SET iter = iter + 1;
    SET ie2_decl = ie2_decl + ie2_decl_incr;
  END WHILE;

END;
//

DELIMITER ;
