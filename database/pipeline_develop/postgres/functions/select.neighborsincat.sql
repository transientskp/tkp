DECLARE ixtrsrcid INT;
DECLARE izoneheight,itheta double precision;
DECLARE icatname VARCHAR(50);

icatname := 'NVSS';
izoneheight := 1;
ixtrsrcid := 670383;
/* three times the search radius */
itheta := 0.075;

SELECT obscatsrcid
      ,3600 * DEGREES(2 * ASIN(SQRT((x1.x - lsm1.x) * (x1.x - lsm1.x)
                                   + (x1.y - lsm1.y) * (x1.y - lsm1.y)
                                   + (x1.z - lsm1.z) * (x1.z - lsm1.z)
                                   ) / 2)) AS distance_arcsec
  FROM extractedsources x1
      ,lsm lsm1
      ,catalogs c0
 WHERE lsm1.cat_id = c0.catid
   AND c0.catname = UPPER(icatname)
   AND x1.xtrsrcid = ixtrsrcid
   AND lsm1.x * x1.x + lsm1.y * x1.y + lsm1.z * x1.z > COS(RADIANS(itheta))
   AND lsm1.zone BETWEEN CAST(FLOOR((x1.decl - itheta) / izoneheight) AS INTEGER)
                   AND CAST(FLOOR((x1.decl + itheta) / izoneheight) AS INTEGER)
   AND lsm1.ra BETWEEN x1.ra - alpha(itheta, x1.decl)
                 AND x1.ra + alpha(itheta, x1.decl)
   AND lsm1.decl BETWEEN x1.decl - itheta
                   AND x1.decl + itheta
ORDER BY distance_arcsec
;
