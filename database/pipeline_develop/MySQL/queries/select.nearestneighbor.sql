/* Select the Nearest Neighbor in the specified catalog 
 * with the specified search radius (theta [degrees])
 * of the specified extracted source (xtrsrcid)
 */
SET @catname = 'VLSS';
SET @xtrsrcid = 2;
SET @theta = 1;
SET @zoneheight = 1;

SELECT catsrcid
  FROM extractedsources x1
      ,catalogedsources c1
      ,catalogs c0
 WHERE c1.cat_id = c0.catid
   AND c0.catname = @catname
   AND x1.xtrsrcid = @xtrsrcid
   AND c1.x * x1.x + c1.y * x1.y + c1.z * x1.z > COS(RADIANS(@theta))
   AND c1.zone BETWEEN FLOOR((x1.decl - @theta) / @zoneheight)
                   AND FLOOR((x1.decl + @theta) / @zoneheight)
   AND c1.ra BETWEEN x1.ra - alpha(@theta, x1.decl)
                 AND x1.ra + alpha(@theta, x1.decl)
   AND c1.decl BETWEEN x1.decl - @theta
                   AND x1.decl + @theta
   AND getDistanceArcsec(x1.ra, x1.decl, c1.ra, c1.decl) = (SELECT MIN(getDistanceArcsec(x1.ra, x1.decl, c1.ra, c1.decl))
                                                              FROM extractedsources x1
                                                                  ,catalogedsources c1
                                                                  ,catalogs c0
                                                             WHERE c1.cat_id = c0.catid
                                                               AND c0.catname = @catname
                                                               AND x1.xtrsrcid = @xtrsrcid
                                                               AND c1.x * x1.x + c1.y * x1.y + c1.z * x1.z > COS(RADIANS(@theta))
                                                               AND c1.zone BETWEEN FLOOR((x1.decl - @theta) / @zoneheight)
                                                                               AND FLOOR((x1.decl + @theta) / @zoneheight)
                                                               AND c1.ra BETWEEN x1.ra - alpha(@theta, x1.decl)
                                                                             AND x1.ra + alpha(@theta, x1.decl)
                                                               AND c1.decl BETWEEN x1.decl - @theta
                                                                               AND x1.decl + @theta
                                                           )
;

/* Select the Nearest Neighbors in the specified catalog 
 * for the specified search radius (theta [degrees])
 * of the specified extracted source (xtrsrcid)
 */
SET @catname = 'VLSS';
SET @xtrsrcid = 2;
SET @theta = 1;
SET @zoneheight = 1;

SELECT catsrcid
      ,getDistanceArcsec(x1.ra, x1.decl, c1.ra, c1.decl) AS dist_arcsec
  FROM extractedsources x1
      ,catalogedsources c1
      ,catalogs c0
 WHERE c1.cat_id = c0.catid
   AND c0.catname = @catname
   AND x1.xtrsrcid = @xtrsrcid
   AND c1.x * x1.x + c1.y * x1.y + c1.z * x1.z > COS(RADIANS(@theta))
   AND c1.zone BETWEEN FLOOR((x1.decl - @theta) / @zoneheight)
                   AND FLOOR((x1.decl + @theta) / @zoneheight)
   AND c1.ra BETWEEN x1.ra - alpha(@theta, x1.decl)
                 AND x1.ra + alpha(@theta, x1.decl)
   AND c1.decl BETWEEN x1.decl - @theta
                   AND x1.decl + @theta
ORDER BY 2
;

