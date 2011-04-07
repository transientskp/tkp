/*
 * This script tests the carthesian elliptical intersection function
 * 
 * C_i       : center of Ellips i (in (x, y), C1 := (0,0) )
 * a_i       : major axis of Ellipse i
 * b_i       : minor axis of Ellipse i 
 * phi_i     : the position angle of ellipse i (pih_1 := 0), 
 *             going in a positive direction from +x to +y, 
 *             i.e. counterclockwise (in degrees in [0, 180))
 */

/*
CASE 1
The two ellipses:

E1: C1 = (0, 0) 
    a1 = 2.4
    b1 = 1.8
    phi1 := 0
    
E2: C2 = (4.4, 0.5) [i.e. relative to C1]
    a2 = 3.0
    b2 = 1.8
    phi2 = 50

do intersect:
*/    

SET @e1_a = 2.4;
SET @e1_b = 1.8;

SET @e2_x = 4.4;
SET @e2_y = 0.5;
SET @e2_a = 3.0;
SET @e2_b = 1.8;
SET @e2_phi = 50;

SELECT 'E1 - E2 intersect' AS 'case 1'
      ,CASE doEllipsesIntersect(@e1_a, @e1_b, @e2_x, @e2_y, @e2_a, @e2_b, @e2_phi)
            WHEN FALSE THEN 'FAILED'
            ELSE 'pass'
       END AS 'result'
;

/*
CASE 2
The two ellipses:

E1: C1 = (0, 0) 
    a1 = 2.4
    b1 = 1.8
    phi1 = 0
    
E2: C2 = (4.4, -0.5), relative to C1
    a2 = 3.0
    b2 = 1.8
    phi2 = 50

do intersect:
*/    

SET @e1_a = 2.4;
SET @e1_b = 1.8;

SET @e2_x = 4.4;
SET @e2_y = -0.5;
SET @e2_a = 3.0;
SET @e2_b = 1.8;
SET @e2_phi = 50;

SELECT 'E1 - E2 intersect' AS 'case 2'
      ,CASE doEllipsesIntersect(@e1_a, @e1_b, @e2_x, @e2_y, @e2_a, @e2_b, @e2_phi)
            WHEN FALSE THEN 'FAILED'
            ELSE 'pass'
       END AS 'result'
;

/*
CASE 3:
The two ellipses:

E1: C1 = (0, 0) 
    a1 = 2.4
    b1 = 1.8
    phi1 = 0
    
E2: C2 = (4.4, -0.52), relative to C1
    a2 = 3.0
    b2 = 1.8
    phi2 = 50

do not intersect:
*/    

SET @e1_a = 2.4;
SET @e1_b = 1.8;

SET @e2_x = 4.4;
SET @e2_y = -0.52;
SET @e2_a = 3.0;
SET @e2_b = 1.8;
SET @e2_phi = 50;

SELECT 'E1 - E2 do not intersect' AS 'case 3'
      ,CASE doEllipsesIntersect(@e1_a, @e1_b, @e2_x, @e2_y, @e2_a, @e2_b, @e2_phi)
            WHEN TRUE THEN 'FAILED'
            ELSE 'pass'
       END AS 'result'
;

/*
CASE 4:
The two ellipses:

E1: C1 = (0, 0) 
    a1 = 2.4
    b1 = 1.8
    phi1 = 0
    
E2: C2 = (6.4, 0.5), relative to C1
    a2 = 3.0
    b2 = 1.8
    phi2 = 50

do not intersect:
*/    

SET @e1_a = 2.4;
SET @e1_b = 1.8;

SET @e2_x = 6.4;
SET @e2_y = 0.5;
SET @e2_a = 3.0;
SET @e2_b = 1.8;
SET @e2_phi = 50;

SELECT 'E1 - E2 do not intersect' AS 'case 4'
      ,CASE doEllipsesIntersect(@e1_a, @e1_b, @e2_x, @e2_y, @e2_a, @e2_b, @e2_phi)
            WHEN TRUE THEN 'FAILED'
            ELSE 'pass'
       END AS 'result'
;

/*
CASE 5:
The two ellipses:

E1: C1 = (0, 0) 
    a1 = 2.4
    b1 = 1.8
    phi1 = 0
    
E2: C2 = (-5.2, -0.515), relative to C1
    a2 = 3.0
    b2 = 1.8
    phi2 = 30

do not intersect:
*/    

SET @e1_a = 2.4;
SET @e1_b = 1.8;

SET @e2_x = -5.2;
SET @e2_y = -0.515;
SET @e2_a = 3.0;
SET @e2_b = 1.8;
SET @e2_phi = 30;

SELECT 'E1 - E2 do not intersect' AS 'case 5'
      ,CASE doEllipsesIntersect(@e1_a, @e1_b, @e2_x, @e2_y, @e2_a, @e2_b, @e2_phi)
            WHEN TRUE THEN 'FAILED'
            ELSE 'pass'
       END AS 'result'
;

/*
CASE 6:
The two ellipses:

E1: C1 = (0, 0) 
    a1 = 2.4
    b1 = 1.8
    phi1 = 0
    
E2: C2 = (-5.2, -0.515), relative to C1
    a2 = 3.0
    b2 = 1.8
    phi2 = 20

do intersect:
*/    

SET @e1_a = 2.4;
SET @e1_b = 1.8;

SET @e2_x = -5.2;
SET @e2_y = -0.515;
SET @e2_a = 3.0;
SET @e2_b = 1.8;
SET @e2_phi = 20;

SELECT 'E1 - E2 intersect' AS 'case 6'
      ,CASE doEllipsesIntersect(@e1_a, @e1_b, @e2_x, @e2_y, @e2_a, @e2_b, @e2_phi)
            WHEN FALSE THEN 'FAILED'
            ELSE 'pass'
       END AS 'result'
;

