--DROP PROCEDURE AssocXSources2CatByImage;

/*+------------------------------------------------------------------+
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
CREATE PROCEDURE AssocXSources2CatByImage(iimageid INT)

BEGIN

  DECLARE izoneheight, itheta, N_density DOUBLE;
  
  SELECT zoneheight 
    INTO izoneheight
    FROM zoneheight
  ;
  SET itheta = 1;
  SET N_density = 60; /* The NVSS source density per deg^2 */

  /* Here we insert the sources that coud be associated */
  INSERT INTO assoccatsources
    (xtrsrc_id
    ,assoc_catsrc_id
    ,assoc_weight
    ,assoc_distance_arcsec
    ,assoc_r
    ,assoc_lr
    )
    SELECT t.xtrsrc_id
          ,CASE WHEN t.assoc_catsrc_id = 0
                THEN NULL 
                ELSE t.assoc_catsrc_id 
           END
          ,t.assoc_weight
          ,t.assoc_distance_degrees * 3600
          ,t.assoc_r
          ,EXP(-PI() * t.assoc_distance_degrees * t.assoc_distance_degrees * N_density)
      FROM (SELECT x1.xtrsrcid AS xtrsrc_id
                  ,c1.catsrcid AS assoc_catsrc_id
                  ,getWeightRectIntersection(x1.ra,x1.decl,x1.ra_err,x1.decl_err
                                            ,c1.ra,c1.decl,c1.ra_err,c1.decl_err
                                            ) AS assoc_weight
                  ,DEGREES(2 * ASIN(SQRT(POWER(c1.x - x1.x, 2)
                                        + POWER(c1.y - x1.y, 2)
                                        + POWER(c1.z - x1.z, 2)
                                        ) / 2)
                          ) AS assoc_distance_degrees
                  ,SQRT( (x1.ra - c1.ra) * (x1.ra - c1.ra) 
                         / (( (x1.ra - (x1.ra + c1.ra) / 2) * (x1.ra - (x1.ra + c1.ra) / 2) 
                            + (c1.ra - (x1.ra + c1.ra) / 2) * (c1.ra - (x1.ra + c1.ra) / 2) 
                            ) / 2)
                       + (x1.decl - c1.decl) * (x1.decl - c1.decl) 
                         / (( (x1.decl - (x1.decl + c1.decl) / 2) * (x1.decl - (x1.decl + c1.decl) / 2)
                            + (c1.decl - (x1.decl + c1.decl) / 2) * (c1.decl - (x1.decl + c1.decl) / 2)
                            ) / 2)
                       ) AS assoc_r
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

END;

