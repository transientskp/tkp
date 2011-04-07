/* this corresponds with wenss source:
 * orig_catsrcid = 61434, catsrcid = 1834918 */
SET @ie1_ra = 104.03946; 
SET @ie1_decl = 52.0945; 
SET @ie1_ra_err = 0.0075;
SET @ie1_decl_err = 0.00950540086293765; 
SET @ie1_pa = 21;

/* this corresponds with nvss source:
 * orig_catsrcid = 512955, catsrcid = 512955 */
SET @ie2_ra = 104.04021;
SET @ie2_decl = 52.09564;
SET @ie2_ra_err = 0.000208333333333333;
SET @ie2_decl_err =  0.000166666666666667;
SET @ie2_phi = 33.9;

CALL pTestDoIntersect(@ie1_ra
                     ,@ie1_decl
                     ,@ie1_ra_err
                     ,@ie1_decl_err
                     ,@ie1_pa
                     ,@ie2_ra
                     ,@ie2_decl
                     ,@ie2_ra_err
                     ,@ie2_decl_err
                     ,@ie2_pa
                     ,@e1_x
                     ,@e1_y
                     ,@e1_z
                     ,@e2_x
                     ,@e2_y
                     ,@e2_z
                     ,@e1_a
                     ,@e1_b
                     ,@e2_h
                     ,@e2_k
                     ,@e2_a
                     ,@e2_b
                     ,@e2_phi
                     ,@distance
                     ); 

SELECT @e1_x
      ,@e1_y
      ,@e1_z
;

SELECT @e2_x
      ,@e2_y
      ,@e2_z
;

SELECT @e1_a
      ,@e1_b
;

SELECT @e2_h
      ,@e2_k
      ,@e2_a
      ,@e2_b
      ,@e2_phi
;

SELECT @distance
;
