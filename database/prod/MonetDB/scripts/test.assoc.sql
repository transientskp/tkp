/*
 * This script test the assoc procedure
 */

/* NOTE: BE SURE THIS IS dsid = 1 
 * SELECT fromfunction() INTO var;
 * does not work in MonetDB
 */
SELECT insertdataset('assoc test I');

/* image 1 */
SELECT insertimage(1, '/this/is/fake/data');
CALL assocsrc(1,1.28,1.25,0.1,0.1, 10,1,10,1,10);
--CALL assocsrc(1,1.19,0.97,0.1,0.1, 10,1,10,1,10);
--CALL assocsrc(1,0.96,0.85,0.1,0.1, 10,1,10,1,10);
--CALL assocsrc(1,0.96,1.15,0.1,0.1, 10,1,10,1,10);

/* image 2 */
--SELECT insertimage(1, '/this/is/fake/dataalso');
--CALL assocsrc(2,1.21,1.07,0.135,0.135, 10,1,10,1,10);
--CALL assocsrc(2,0.865,1.1,0.135,0.135, 10,1,10,1,10);

/* image 3 */
--SELECT insertimage(1,'/this/is/fake/dataalso');
--CALL assocsrc(3,1.0,1.0,.15,.125, 10,1,10,1,10);
