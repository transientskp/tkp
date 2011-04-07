SET @catname = 'NVSS';
SET @zoneheight = 1;
SET @xtrsrcid = 4;
SET @theta = 3/60;

SELECT catsrcid
      ,3600 * DEGREES(2*ASIN(SQRT(POWER((COS(radians(c1.decl)) * COS(radians(c1.ra))
               - COS(radians(x1.decl)) * COS(radians(x1.ra))
               ), 2)
        + POWER((COS(radians(c1.decl)) * SIN(radians(c1.ra))
                - COS(radians(x1.decl)) * SIN(radians(x1.ra))
                ), 2)
        + POWER((SIN(radians(c1.decl))
                - SIN(radians(x1.decl))
                ), 2)) / 2)) AS distance_arcsec
  FROM extractedsources x1
      ,catalogedsources c1
      ,catalogs c0
 WHERE c1.cat_id = c0.catid
   AND c0.catname = UPPER(@catname)
   AND x1.xtrsrcid = @xtrsrcid
   AND c1.x * x1.x + c1.y * x1.y + c1.z * x1.z > COS(RADIANS(@theta))
   AND c1.zone BETWEEN FLOOR((x1.decl - @theta) / @zoneheight)
                   AND FLOOR((x1.decl + @theta) / @zoneheight)
   AND c1.ra BETWEEN x1.ra - alpha(@theta, x1.decl)
                 AND x1.ra + alpha(@theta, x1.decl)
   AND c1.decl BETWEEN x1.decl - @theta
                   AND x1.decl + @theta
ORDER BY distance_arcsec
;
