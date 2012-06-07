DECLARE ixtrsrcid INT;
DECLARE itheta,izoneheight DOUBLE;

SET ixtrsrcid = 4;
SET itheta = 1;
SET izoneheight = 1;

SELECT SUM(ra / (ra_err * ra_err)) / SUM(1 / (ra_err * ra_err)) AS avg_ra
      ,SUM(decl / (decl_err * decl_err)) / SUM(1 / (decl_err * decl_err)) AS avg_decl
      ,SQRT(SUM(1 / (ra_err * ra_err))) AS avg_ra_err
      ,SQRT(SUM(1 / (decl_err * decl_err)))  AS avg_decl_err
      ,SQRT(SUM(1 / (ra_err * ra_err)) + SUM(1 / (decl_err * decl_err))) 
  FROM (SELECT x1.ra AS ra
              ,x1.decl AS decl
              ,x1.ra_err AS ra_err
              ,x1.decl_err AS decl_err
          FROM extractedsources x1
         WHERE x1.xtrsrcid = ixtrsrcid
         UNION
        SELECT c1.ra AS ra
              ,c1.decl AS decl
              ,c1.ra_err AS ra_err
              ,c1.decl_err AS decl_err
          FROM catalogedsources c1
         WHERE c1.catsrcid = getNearestNeighborInCat('NVSS', 1, ixtrsrcid)
       ) t
;



/*
SELECT t.xtrsrc_id
      ,CASE WHEN t.assoc_catsrc_id = 0
            THEN NULL 
            ELSE t.assoc_catsrc_id 
       END
      ,t.assoc_weight
      ,t.assoc_distance_arcsec
  FROM (SELECT x1.xtrsrcid AS xtrsrc_id
              ,c1.catsrcid AS assoc_catsrc_id
              ,getWeightRectIntersection(x1.ra,x1.decl,x1.ra_err,x1.decl_err
                                        ,c1.ra,c1.decl,c1.ra_err,c1.decl_err
                                        ) AS assoc_weight
              ,3600 * degrees(2 * ASIN(SQRT(POWER((COS(radians(c1.decl)) * COS(radians(c1.ra))
                                                  - COS(radians(x1.decl)) * COS(radians(x1.ra))
                                                  ), 2)
                                           + POWER((COS(radians(c1.decl)) * SIN(radians(c1.ra))
                                                   - COS(radians(x1.decl)) * SIN(radians(x1.ra))
                                                   ), 2)
                                           + POWER((SIN(radians(c1.decl))
                                                   - SIN(radians(x1.decl))
                                                   ), 2)
                                           ) / 2)
                             ) AS assoc_distance_arcsec
          FROM extractedsources x1
              ,catalogedsources c1
              ,catalogs c
         WHERE x1.image_id = iimageid
           AND c1.cat_id = c.catid
           AND c1.zone BETWEEN CAST(FLOOR((x1.decl - itheta) / izoneheight) AS INTEGER)
                           AND CAST(FLOOR((x1.decl + itheta) / izoneheight) AS INTEGER)
           AND c1.ra BETWEEN x1.ra - alpha(itheta,x1.decl)
                         AND x1.ra + alpha(itheta,x1.decl)
           AND c1.decl BETWEEN x1.decl - itheta
                           AND x1.decl + itheta
           AND doPosErrCirclesIntersect(x1.ra,x1.decl,x1.ra_err,x1.decl_err
                                       ,c1.ra,c1.decl,c1.ra_err,c1.decl_err)
       ) t
;
*/

