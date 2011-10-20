--DROP PROCEDURE AssocXSources2XSourcesByImage;

/*+------------------------------------------------------------------+
 *| Here we use doPosErrCirclesIntersect (~4sigma search redius)     |
 *| instead of the itheta=90" that is used in the assoc against cat  |
 *| sources.                                                         |
 *+------------------------------------------------------------------+
 *+------------------------------------------------------------------+
 *|                                                                  |
 *+------------------------------------------------------------------+
 *+------------------------------------------------------------------+
 *+------------------------------------------------------------------+
 *+------------------------------------------------------------------+
 *|                                                                  |
 *+------------------------------------------------------------------+
 */
CREATE PROCEDURE AssocXSources2XSourcesByImage(iimageid INT)

BEGIN

  DECLARE izoneheight, itheta, N_density double precision;
  
  SELECT zoneheight 
    INTO izoneheight
    FROM zoneheight
  ;
  SET itheta = 1;
  /*SET N_density = getSkyDensity_deg2(1400, 0.0021);*/
  SET N_density = 4.02439375E-06; /*NVSS density */

  /* Here we insert the sources that coud be associated */
  INSERT INTO assocxtrsources
    (xtrsrc_id
    ,assoc_xtrsrc_id
    ,assoc_weight
    ,assoc_distance_arcsec
    ,assoc_lr_method
    ,assoc_r
    ,assoc_lr
    )
    SELECT t.xtrsrc_id
          ,CASE WHEN t.assoc_xtrsrc_id = 0
                THEN NULL 
                ELSE t.assoc_xtrsrc_id 
           END
          ,t.assoc_weight
          ,t.assoc_distance_arcsec
          ,t.assoc_lr_method
          ,t.assoc_r
          ,t.assoc_lr
      FROM (SELECT t2.xtrsrc_id
                  ,t2.assoc_xtrsrc_id
                  ,t2.assoc_weight
                  ,t2.assoc_distance_arcsec
                  ,4 AS assoc_lr_method
                  ,t2.assoc_distance_arcsec / SQRT(t2.sigma_ra * t2.sigma_ra + t2.sigma_decl * t2.sigma_decl) AS assoc_r
                  ,LOG10(EXP(-t2.assoc_distance_arcsec * t2.assoc_distance_arcsec
                             / (2 * (t2.sigma_ra * t2.sigma_ra + t2.sigma_decl * t2.sigma_decl))
                             )
                         / (2 * PI() * t2.sigma_ra * t2.sigma_decl * N_density)
                         ) AS assoc_lr
              FROM (SELECT t1.xtrsrc_id
                          ,t1.assoc_xtrsrc_id
                          ,getWeightRectIntersection(xs1.ra,xs1.decl,xs1.ra_err,xs1.decl_err
                                                    ,xs2.ra,xs2.decl,xs2.ra_err,xs2.decl_err
                                                    ) AS assoc_weight
                          ,3600 * DEGREES(2 * ASIN(SQRT((xs2.x - xs1.x) * (xs2.x - xs1.x)
                                                       + (xs2.y - xs1.y) * (xs2.y - xs1.y)
                                                       + (xs2.z - xs1.z) * (xs2.z - xs1.z)
                                                       ) / 2)) AS assoc_distance_arcsec
                          ,SQRT((xs2.ra_err) * (xs2.ra_err) + (xs1.ra_err) * (xs1.ra_err)) AS sigma_ra
                          ,SQRT((xs2.decl_err) * (xs2.decl_err) + (xs1.decl_err) * (xs1.decl_err)) AS sigma_decl
                      FROM (SELECT IFTHENELSE(doPosErrCirclesIntersect(x1.ra,x1.decl,x1.ra_err,x1.decl_err
                                                                      ,x3.ra,x3.decl,x3.ra_err,x3.decl_err)
                                             ,x3.xtrsrcid, x2.xtrsrcid
                                             ) AS xtrsrc_id
                                  ,x1.xtrsrcid AS assoc_xtrsrc_id
                              FROM extractedsources x1
                                  ,images im1
                                  ,assocxtrsources a1
                                  ,extractedsources x2
                                  ,images im2
                                  ,extractedsources x3
                             WHERE x1.image_id = iimageid
                               AND x1.image_id = im1.imageid
                               AND im1.ds_id = (SELECT im11.ds_id
                                                  FROM images im11
                                                 WHERE im11.imageid = iimageid
                                               )
                               AND a1.assoc_xtrsrc_id = x2.xtrsrcid
                               AND a1.xtrsrc_id = x3.xtrsrcid
                               AND x2.image_id = im2.imageid
                               AND im1.ds_id = im2.ds_id
                               AND x2.zone BETWEEN CAST(FLOOR((x1.decl - itheta) / izoneheight) AS INTEGER)
                                               AND CAST(FLOOR((x1.decl + itheta) / izoneheight) AS INTEGER)
                               AND x2.ra BETWEEN x1.ra - alpha(itheta,x1.decl)
                                             AND x1.ra + alpha(itheta,x1.decl)
                               AND x2.decl BETWEEN x1.decl - itheta
                                               AND x1.decl + itheta
                               AND doPosErrCirclesIntersect(x1.ra,x1.decl,x1.ra_err,x1.decl_err
                                                           ,x2.ra,x2.decl,x2.ra_err,x2.decl_err)
                               AND x3.zone BETWEEN CAST(FLOOR((x1.decl - itheta) / izoneheight) AS INTEGER)
                                               AND CAST(FLOOR((x1.decl + itheta) / izoneheight) AS INTEGER)
                               AND x3.ra BETWEEN x1.ra - alpha(itheta,x1.decl)
                                             AND x1.ra + alpha(itheta,x1.decl)
                               AND x3.decl BETWEEN x1.decl - itheta
                                               AND x1.decl + itheta
                           ) t1
                          ,extractedsources xs1
                          ,extractedsources xs2
                     WHERE t1.xtrsrc_id = xs1.xtrsrcid
                       AND t1.assoc_xtrsrc_id = xs2.xtrsrcid
                   ) t2
            UNION
            /* Here we insert the sources in the current image that could not be associated 
             * to any source belonging to the same dataset.
             */
            SELECT x1.xtrsrcid AS xtrsrc_id
                  ,x1.xtrsrcid AS assoc_xtrsrc_id
                  ,2 AS assoc_weight
                  ,0 AS assoc_distance_arcsec
                  ,4 AS assoc_lr_method
                  ,0 AS assoc_r
                  ,0 AS assoc_lr
                  /*TODO:,LOG10(1 / (4 * pi() * x1.ra_err * x1.decl_err * N_density)) AS assoc_lr*/
              FROM extractedsources x1
                  ,assocxtrsources a1
                  ,extractedsources x2
                  ,images im2 
             WHERE x1.image_id = iimageid 
               AND a1.xtrsrc_id = x2.xtrsrcid 
               AND x2.image_id = im2.imageid 
               AND im2.ds_id = (SELECT ds_id 
                                  FROM images im3 
                                 WHERE imageid = iimageid
                               ) 
               AND NOT doPosErrCirclesIntersect(x1.ra,x1.decl,x1.ra_err,x1.decl_err
                                               ,x2.ra,x2.decl,x2.ra_err,x2.decl_err)
               AND x1.xtrsrcid NOT IN (SELECT x3.xtrsrcid       
                                         FROM extractedsources x3       
                                             ,images im4       
                                             ,assocxtrsources a2       
                                             ,extractedsources x4       
                                             ,images im5  
                                        WHERE x3.image_id = iimageid
                                          AND x3.image_id = im4.imageid
                                          AND im4.ds_id = (SELECT im6.ds_id
                                                             FROM images im6
                                                            WHERE im6.imageid = iimageid
                                                          )
                                          AND a2.xtrsrc_id = x4.xtrsrcid
                                          AND x4.image_id = im5.imageid    
                                          AND im5.ds_id = im4.ds_id
                                          AND x4.zone BETWEEN CAST(FLOOR((x3.decl - itheta) / izoneheight) AS INTEGER)
                                                          AND CAST(FLOOR((x3.decl + itheta) / izoneheight) AS INTEGER)
                                          AND x4.ra BETWEEN x3.ra - alpha(itheta,x3.decl)
                                                        AND x3.ra + alpha(itheta,x3.decl)
                                          AND x4.decl BETWEEN x3.decl - itheta
                                                          AND x3.decl + itheta
                                          AND doPosErrCirclesIntersect(x3.ra,x3.decl,x3.ra_err,x3.decl_err
                                                                      ,x4.ra,x4.decl,x4.ra_err,x4.decl_err)
                                      )
            GROUP BY x1.xtrsrcid
            UNION
            /* Here we insert the sources that could not be associated, because
             * the assocxtrsources table is empty
             */
            SELECT x1.xtrsrcid AS xtrsrc_id
                  ,x1.xtrsrcid AS assoc_xtrsrc_id
                  ,3 AS assoc_weight
                  ,0 AS assoc_distance_arcsec
                  ,4 AS assoc_lr_method
                  ,0 AS assoc_r
                  ,0 AS assoc_lr
                  /*TODO:,LOG10(1 / (4 * pi() * x1.ra_err * x1.decl_err * N_density)) AS assoc_lr*/
              FROM extractedsources x1
             WHERE NOT EXISTS (SELECT a2.xtrsrc_id
                                 FROM assocxtrsources a2
                                     ,extractedsources x2
                                     ,images im2
                                WHERE x2.xtrsrcid = a2.xtrsrc_id
                                  AND x2.image_id = im2.imageid
                                  AND im2.ds_id = (SELECT im10.ds_id
                                                     FROM images im10
                                                    WHERE imageid = iimageid
                                                  )
                              )
               AND x1.image_id = iimageid
           ) t
  ;

END;

