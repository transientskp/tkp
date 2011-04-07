/*
 * This script test the assoc procedure
 */
SELECT insertdataset('assoc test I') INTO @dsid;
SELECT @dsid;
/* image 1 */
SELECT insertimage(@dsid, '/this/is/fake/data') INTO @image_id;
/* 4 sources in image 1 */
/*x(k)*/
CALL assocsrc(@image_id,1.28,1.25,0.1,0.1, 10,1,10,1,10);
/*x(k+1)*/
CALL assocsrc(@image_id,1.19,0.97,0.1,0.1, 10,1,10,1,10);
/*x(l)*/
CALL assocsrc(@image_id,0.96,0.85,0.1,0.1, 10,1,10,1,10);
/*x(k+2)*/
CALL assocsrc(@image_id,0.96,1.15,0.1,0.1, 10,1,10,1,10);

/* image 2 */
SELECT insertimage(@dsid, '/this/is/fake/dataalso') INTO @image_id;
/* 2 sources in image 2 */
/*x(j)*/
CALL assocsrc(@image_id,1.21,1.07,0.135,0.135, 10,1,10,1,10);
/*x(j+1)*/
CALL assocsrc(@image_id,0.865,1.1,0.135,0.135, 10,1,10,1,10);

/* image 3 */
SELECT insertimage(@dsid, '/this/is/also/fake/data') INTO @image_id;
/* 1 sources in image 3 */
/*x(0)*/
CALL assocsrc(@image_id,1.0,1.0,.15,.125, 10,1,10,1,10);

