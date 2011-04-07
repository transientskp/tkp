/*
 *
 */

SET @theta = 1;
SET @zoneheight = 1;
SET @sin_itheta = SIN(RADIANS(@theta));

SELECT NOW() AS '';

SELECT '';

SELECT c1.catsrcid
      ,c2.catsrcid
      ,DEGREES(2 * ASIN(SQRT(POW(c2.x - c1.x, 2) + 
                             POW(c2.y - c1.y, 2) + 
                             POW(c2.z - c1.z, 2)) / 2)) AS distance
  FROM catalogedsources c1
      ,catalogedsources c2
 WHERE c1.cat_id = 3
   AND c2.cat_id = 4
   AND c1.ra BETWEEN 104 AND 105
   AND c2.ra BETWEEN 104 AND 105
   /*
   AND c2.zone BETWEEN FLOOR((c1.decl - @theta)/@zoneheight)
                   AND FLOOR((c1.decl + @theta)/@zoneheight)
   AND c2.ra BETWEEN c1.ra - alpha(@theta, c1.decl)
                 AND c1.ra + alpha(@theta, c1.decl)
   AND c2.decl BETWEEN c1.decl - @theta
                   AND c1.decl + @theta
   AND 4 * POW(SIN(RADIANS(itheta / 2)), 2) > 
       POW(x - ix, 2) + POW(y - iy, 2) + POW(z - iz, 2)
   
   AND @sin_itheta > SIN(2 * ASIN(SQRT(POW(c2.x - c1.x, 2) + 
                                       POW(c2.y - c1.y, 2) + 
                                       POW(c2.z - c1.z, 2)) / 2))
   AND doIntersectElls(c1.ra,c1.decl,c1.ra_err,c1.decl_err
                      ,c2.ra,c2.decl,c2.ra_err,c2.decl_err)
   */
;


/*
SELECT NOW() AS '';

SELECT '';

SELECT COUNT(*)
  FROM catalogedsources c1
      ,catalogedsources c2
 WHERE c2.cat_id > c1.cat_id
   AND c1.cat_id = 3
   AND c1.ra BETWEEN 104 AND 105
   AND c2.zone BETWEEN FLOOR((c1.decl - @theta)/@zoneheight)
                  AND FLOOR((c1.decl + @theta)/@zoneheight)
   AND c2.ra BETWEEN c1.ra - alpha(@theta, c1.decl)
                 AND c1.ra + alpha(@theta, c1.decl)
   AND c2.decl BETWEEN c1.decl - @theta
                   AND c1.decl + @theta
   AND 4 * POW(SIN(RADIANS(itheta / 2)), 2) > 
       POW(x - ix, 2) + POW(y - iy, 2) + POW(z - iz, 2)
   AND @sin_itheta > SIN(2 * ASIN(SQRT(POW(c2.x - c1.x, 2) + 
                                      POW(c2.y - c1.y, 2) + 
                                      POW(c2.z - c1.z, 2)) / 2))
   AND doIntersectElls(c1.ra,c1.decl,c1.ra_err,c1.decl_err
                      ,c2.ra,c2.decl,c2.ra_err,c2.decl_err)
   */
;

SELECT NOW() AS '';

