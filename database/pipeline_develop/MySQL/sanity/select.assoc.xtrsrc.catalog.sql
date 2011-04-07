/* This query selects all the catalogedsources that
 * that will be taken into account for an association
 * with the extractedsources.
 */

SET @imageid = 1;
SET @zoneheight = 1;
SET @theta = 1;

/* Here we select the sources that could be associated to the sources
 * in the main catalogs
 */
SELECT x1.xtrsrcid AS xtrsrc_id
      ,solidangle_arcsec2(x1.ra - x1.ra_err / 3600, x1.ra + x1.ra_err / 3600
                         ,x1.decl - x1.decl_err / 3600, x1.decl + x1.decl_err / 3600
                         ) AS solidangle_arcsec2
      ,x1.i_int / x1.i_int_err
      ,c1.catsrcid AS assoc_catsrc_id
      ,c1.ra_err
      ,c1.decl_err
      ,c1.i_int_avg / c1.i_int_avg_err
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
      ,doSourcesIntersect(x1.ra,x1.decl,c1.ra_err,c1.decl_err
                         ,c1.ra,c1.decl,c1.ra_err,c1.decl_err
                         ) AS 'cat do_intersect'
      ,(3600 * degrees(2 * ASIN(SQRT(POWER((COS(radians(c1.decl)) * COS(radians(c1.ra))
                                           - COS(radians(x1.decl)) * COS(radians(x1.ra))
                                           ), 2)
                                    + POWER((COS(radians(c1.decl)) * SIN(radians(c1.ra))
                                            - COS(radians(x1.decl)) * SIN(radians(x1.ra))
                                            ), 2)
                                    + POWER((SIN(radians(c1.decl))
                                            - SIN(radians(x1.decl))
                                            ), 2)
                                    ) / 2)
                      )
       ) / GREATEST(x1.ra_err, x1.decl_err) AS dist_in_pos_err
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
ORDER BY 9 
LIMIT 30
;


