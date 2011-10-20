--DROP PROCEDURE AssocWenssSources2Cat;

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
CREATE PROCEDURE AssocWenssSources2Cat(iimageid INT
                                      ,izone_min INT
                                      ,izone_max INT
                                      )

BEGIN

  DECLARE izoneheight, itheta, N_density double precision;

  SELECT zoneheight 
    INTO izoneheight
    FROM zoneheight
  ;
  SET itheta = 0.025; /* = 90" */
  SET N_density = 60; /* The average NVSS source density per deg^2 */

  /* Here we insert the sources that coud be associated */
  INSERT INTO assoccatsources
    (xtrsrc_id
    ,assoc_catsrc_id
    /*,assoc_weight*/
    ,assoc_distance_arcsec
    ,assoc_lr_method
    ,assoc_r
    ,assoc_lr
    )
    SELECT t.xtrsrcid
          /*,t.catname*/
          ,t.catsrcid
          /*,t.assoc_weight*/
          ,t.assoc_distance_arcsec
          ,3 AS assoc_lr_method
          ,t.assoc_r
          /*,t.sigma*/
          ,LOG10(EXP(-t.assoc_r * t.assoc_r / 2) / (2 * PI() * 55 * t.sigma * t.sigma)) AS assoc_lr
      FROM (SELECT x1.xtrsrcid
                  ,c.catname
                  ,lsm1.lsmid AS catsrcid
                  /*,getWeightRectIntersection(x1.ra,x1.decl,x1.ra_err,x1.decl_err
                                            ,lsm1.ra,lsm1.decl,lsm1.ra_err,lsm1.decl_err
                                            ) AS assoc_weight*/
                  ,3600 * DEGREES(2 * ASIN(SQRT(POWER(lsm1.x - x1.x, 2)
                                               + POWER(lsm1.y - x1.y, 2)
                                               + POWER(lsm1.z - x1.z, 2)
                                               ) / 2) ) AS assoc_distance_arcsec
                  ,3600 * SQRT( (alpha((x1.ra - lsm1.ra), x1.decl) * alpha((x1.ra - lsm1.ra), x1.decl))
                                / ((x1.ra_err) * (x1.ra_err) + (lsm1.ra_err) * (lsm1.ra_err))
                              + ((x1.decl - lsm1.decl) * (x1.decl - lsm1.decl))
                                / ((x1.decl_err) * (x1.decl_err) + (lsm1.decl_err) * (lsm1.decl_err))
                              ) AS assoc_r
                  ,SQRT((x1.ra_err) * (x1.ra_err)
                       + (x1.decl_err) * (x1.decl_err)
                       + (lsm1.ra_err) * (lsm1.ra_err)
                       + (lsm1.decl_err) * (lsm1.decl_err)
                       ) AS sigma
              FROM extractedsources x1
                  ,lsm lsm1
                  ,catalogs c
             WHERE image_id = iimageid
               AND x1.zone >= izone_min
               AND x1.zone < izone_max
               AND lsm1.cat_id = c.catid
               AND lsm1.zone BETWEEN CAST(FLOOR((x1.decl - itheta) / izoneheight) AS INTEGER)
                                AND CAST(FLOOR((x1.decl + itheta) / izoneheight) AS INTEGER)
               AND lsm1.ra BETWEEN x1.ra - alpha(itheta,x1.decl)
                              AND x1.ra + alpha(itheta,x1.decl)
               AND lsm1.decl BETWEEN x1.decl - itheta
                                AND x1.decl + itheta
               AND lsm1.x * x1.x + lsm1.y * x1.y + lsm1.z * x1.z > COS(RADIANS(itheta))
           ) t
  ;

END;

