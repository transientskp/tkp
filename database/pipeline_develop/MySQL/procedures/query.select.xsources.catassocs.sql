SET @imageid = 1;
SET @zoneheight = 1;
SET @theta = 1;

SELECT x1.xtrsrcid
      ,c1.catsrcid
      ,c.catname
      ,doSourcesIntersect(x1.ra,x1.decl,x1.ra_err,x1.decl_err
                         ,c1.ra,c1.decl,c1.ra_err,c1.decl_err
                         ) AS do_intersect
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
                                   ) / 2)) AS assoc_distance_arcsec
  FROM extractedsources x1
      ,catalogedsources c1
      ,catalogs c
 WHERE x1.image_id = @imageid
   AND c1.cat_id = c.catid
   AND c1.zone BETWEEN FLOOR((x1.decl - @theta) / @zoneheight)
                   AND FLOOR((x1.decl + @theta) / @zoneheight)
   AND c1.ra BETWEEN x1.ra - alpha(@theta,x1.decl)
                 AND x1.ra + alpha(@theta,x1.decl)
   AND c1.decl BETWEEN x1.decl - @theta
                   AND x1.decl + @theta
   AND doSourcesIntersect(x1.ra,x1.decl,x1.ra_err,x1.decl_err
                         ,c1.ra,c1.decl,c1.ra_err,c1.decl_err)
;

/*
      SELECT t1.xtrsrc_id
                  ,FALSE AS insert_src1
                  ,'X' AS assoc_type
                  ,t1.assoc_xtrsrc_id
                  ,NULL AS insert_src2
                  ,getWeightRectIntersection(xs1.ra,xs1.decl,xs1.ra_err,xs1.decl_err
                                            ,xs2.ra,xs2.decl,xs2.ra_err,xs2.decl_err
                                            ) AS assoc_weight
                  ,3600 * degrees(2 * ASIN(SQRT(POWER((COS(radians(xs2.decl)) * COS(radians(xs2.ra))
                                                      - COS(radians(xs1.decl)) * COS(radians(xs1.ra))
                                                      ), 2)
                                               + POWER((COS(radians(xs2.decl)) * SIN(radians(xs2.ra))
                                                       - COS(radians(xs1.decl)) * SIN(radians(xs1.ra))
                                                       ), 2)
                                               + POWER((SIN(radians(xs2.decl))
                                                       - SIN(radians(xs1.decl))
                                                       ), 2)
                                               ) / 2)) AS assoc_distance_arcsec
              FROM (SELECT IF(doSourcesIntersect(x1.ra,x1.decl,x1.ra_err,x1.decl_err
                                                ,x3.ra,x3.decl,x3.ra_err,x3.decl_err)
                             ,x3.xtrsrcid, x2.xtrsrcid
                             ) AS xtrsrc_id
                          ,x1.xtrsrcid AS assoc_xtrsrc_id
                      FROM extractedsources x1
                          ,images im1
                          ,associatedsources a1
                          ,extractedsources x2
                          ,images im2
                          ,extractedsources x3
                     WHERE x1.image_id = @imageid
                       AND x1.image_id = im1.imageid
                       AND im1.ds_id = (SELECT im11.ds_id
                                          FROM images im11
                                         WHERE im11.imageid = @imageid
                                       )
                       AND a1.assoc_xtrsrc_id = x2.xtrsrcid
                       AND a1.xtrsrc_id = x3.xtrsrcid
                       AND x2.image_id = im2.imageid
                       AND im1.ds_id = im2.ds_id
                       AND x2.zone BETWEEN FLOOR((x1.decl - @theta) / @zoneheight)
                                       AND FLOOR((x1.decl + @theta) / @zoneheight)
                       AND x2.ra BETWEEN x1.ra - alpha(@theta,x1.decl)
                                     AND x1.ra + alpha(@theta,x1.decl)
                       AND x2.decl BETWEEN x1.decl - @theta
                                       AND x1.decl + @theta
                       AND doSourcesIntersect(x1.ra,x1.decl,x1.ra_err,x1.decl_err
                                             ,x2.ra,x2.decl,x2.ra_err,x2.decl_err)
                       AND x3.zone BETWEEN FLOOR((x1.decl - @theta) / @zoneheight)
                                       AND FLOOR((x1.decl + @theta) / @zoneheight)
                       AND x3.ra BETWEEN x1.ra - alpha(@theta,x1.decl)
                                     AND x1.ra + alpha(@theta,x1.decl)
                       AND x3.decl BETWEEN x1.decl - @theta
                                       AND x1.decl + @theta
                   ) t1
                  ,extractedsources xs1
                  ,extractedsources xs2
             WHERE t1.xtrsrc_id = xs1.xtrsrcid
               AND t1.assoc_xtrsrc_id = xs2.xtrsrcid
  ;

*/

