SELECT "";

/* this corresponds to the wenss source:
 * orig_catsrcid = 61434, catsrcid = 1834918
 */
SET @ie1_ra = 104.03946; 
SET @ie1_decl = 52.0945;
SET @ie1_ra_err = 0.0075; 
SET @ie1_decl_err = 0.00950540086293765;

/* this corresponds to the nvss source:
 * orig_catsrcid = 512955, catsrcid = 512955
 */
SET @ie2_ra = 104.04021; 
SET @ie2_decl = 52.09564;
SET @ie2_ra_err = 0.000208333333333333; 
SET @ie2_decl_err = 0.0001666666666666667;

CALL Sources2Cartesian(@ie1_ra
                      ,@ie1_decl
                      ,@ie1_ra_err
                      ,@ie1_decl_err
                      /*,@ie1_pa*/
                      ,@ie2_ra
                      ,@ie2_decl
                      ,@ie2_ra_err
                      ,@ie2_decl_err
                      /*,@ie2_pa*/
                      ,@oe1_pa
                      ,@oe2_pa
                      ,@ou1
                      ,@ou2
                      ,@ou3
                      ,@ov1
                      ,@ov2
                      ,@ov3
                      ,@ow1
                      ,@ow2
                      ,@ow3
                      ,@ogamma
                      ,@ogamma_alt
                      ,@otheta_rot
                      ,@obeta
                      ,@odistance
                      ,@oe1_a
                      ,@oe1_b
                      ,@oe1_phi
                      ,@oe2_h
                      ,@oe2_k
                      ,@oe2_a
                      ,@oe2_b
                      ,@oe2_phi
                      )
;

SELECT @ie1_ra
      ,@ie1_decl
      ,@ie1_ra_err
      ,@ie1_decl_err
      /*,@ie1_pa*/
;

SELECT @ie2_ra
      ,@ie2_decl
      ,@ie2_ra_err
      ,@ie2_decl_err
      /*,@ie2_pa*/
;

SELECT "";

SELECT @oe1_pa
      ,@oe2_pa
;

SELECT @ou1
      ,@ou2
      ,@ou3
;

SELECT @ov1
      ,@ov2
      ,@ov3
;

SELECT @ow1
      ,@ow2
      ,@ow3
;

SELECT DEGREES(@ogamma) AS 'gamma [degrees]'
      ,DEGREES(@ogamma_alt) AS 'gamma_alt [degrees]'
      ,@otheta_rot
      ,@obeta
      ,@odistance AS 'distance [arcsec]'
;

SELECT "";

SELECT @oe1_a
      ,@oe1_b
      ,@oe1_phi
;

SELECT @oe2_h
      ,@oe2_k
      ,@oe2_a
      ,@oe2_b
      ,@oe2_phi
;

SELECT "";

