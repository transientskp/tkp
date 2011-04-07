SELECT "";

SET @ie1_ra = 20; 
SET @ie1_decl = 0;
SET @ie1_ra_err = 4; 
SET @ie1_decl_err = 3;

SET @ie2_ra = @ie1_ra - (3 / 3600); 
SET @ie2_decl = @ie1_decl + (4 / 3600);
SET @ie2_ra_err = 5; 
SET @ie2_decl_err = 2.5;

CALL Sources2Cartesian(@ie1_ra,@ie1_decl,@ie1_ra_err,@ie1_decl_err /*,@ie1_pa*/,@ie2_ra,@ie2_decl,@ie2_ra_err,@ie2_decl_err /*,@ie2_pa*/,@oe1_pa,@oe2_pa,@ou1,@ou2,@ou3,@os1_w1,@os1_w2,@os1_w3,@os1_n1,@os1_n2,@os1_n3,@ov1,@ov2,@ov3,@os2_w1,@os2_w2,@os2_w3,@os2_n1,@os2_n2,@os2_n3,@ozeta,@odistance,@otheta_rot,@oe1_a,@oe1_b,@oe1_phi,@oe2_h,@oe2_k,@oe2_a,@oe2_b,@oe2_phi,@oe2_h_acc,@oe2_k_acc,@oe2_phi_acc);

SELECT @ie1_ra,ra2hms(@ie1_ra),@ie1_decl,decl2dms(@ie1_decl),@ie1_ra_err,@ie1_decl_err/*,@ie1_pa*/;

SELECT @ie2_ra,ra2hms(@ie2_ra),@ie2_decl,decl2dms(@ie2_decl),@ie2_ra_err,@ie2_decl_err/*,@ie2_pa*/;

SELECT @oe1_pa,@oe2_pa;

SELECT @ou1,@ou2, @ou3;

SELECT @os1_n1, @os1_n2, @os1_n3;

SELECT @os1_w1, @os1_w2, @os1_w3;

SELECT @ov1, @ov2, @ov3;

SELECT @os2_n1, @os2_n2, @os2_n3;

SELECT @os2_w1, @os2_w2, @os2_w3;

SELECT @ozeta, @odistance AS 'distance [arcsec]',@otheta_rot;

SELECT "";

SELECT @oe1_a,@oe1_b,@oe1_phi;

SELECT @oe2_h,@oe2_k,@oe2_a,@oe2_b,@oe2_phi;

SELECT @oe2_h_acc,@oe2_k_acc,@oe2_phi_acc;

SELECT getWeightEllipticalIntersection2(@oe1_a,@oe1_b,@oe2_h_acc,@oe2_k_acc,@oe2_a,@oe2_b,@oe2_phi_acc) as weight;

SELECT "";

