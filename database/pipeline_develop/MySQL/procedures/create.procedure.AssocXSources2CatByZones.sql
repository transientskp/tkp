DROP PROCEDURE IF EXISTS AssocXSources2CatByZones;

DELIMITER //

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
CREATE PROCEDURE AssocXSources2CatByZones(iimageid INT)

BEGIN

  DECLARE izoneheight, itheta, N_density DOUBLE;

  SELECT zoneheight 
    INTO izoneheight
    FROM zoneheight
  ;
  
  /* We set the search radius to 90" */
  SET itheta = 0.025;
  /* The average NVSS source density per arcsec^2 */
  SET N_density = 4.02439375E-06; 

  /* Here we insert the sources that coud be associated */
  INSERT INTO assoccatsources
    (xtrsrc_id
    ,assoc_catsrc_id
    ,assoc_distance_arcsec
    ,assoc_lr_method
    ,assoc_r
    ,assoc_lr
    )
    SELECT t.xtrsrcid
          ,t.catsrcid
          ,t.assoc_distance_arcsec
          ,3 AS assoc_lr_method
          ,t.assoc_distance_arcsec / t.sigma AS assoc_r
          ,LOG10(EXP(-t.assoc_distance_arcsec * t.assoc_distance_arcsec / (2 * t.sigma * t.sigma)
                    + PI() * t.sigma_ra * t.sigma_decl * N_density
                    ) 
                / (2 * PI() * t.sigma_ra * t.sigma_decl * N_density)
                ) AS assoc_lr
      FROM (SELECT x1.xtrsrcid
                  ,c.catname
                  ,lsm1.lsmid AS catsrcid
                  ,3600 * DEGREES(2 * ASIN(SQRT((lsm1.x - x1.x) * (lsm1.x - x1.x)
                                               + (lsm1.y - x1.y) * (lsm1.y - x1.y)
                                               + (lsm1.z - x1.z) * (lsm1.z - x1.z)
                                               ) / 2) ) AS assoc_distance_arcsec
                  ,SQRT((x1.ra_err) * (x1.ra_err) + (lsm1.ra_err) * (lsm1.ra_err)) AS sigma_ra
                  ,SQRT((x1.decl_err) * (x1.decl_err) + (lsm1.decl_err) * (lsm1.decl_err)) AS sigma_decl
                  ,SQRT((x1.ra_err) * (x1.ra_err) + (x1.decl_err) * (x1.decl_err)
                       + (lsm1.ra_err) * (lsm1.ra_err) + (lsm1.decl_err) * (lsm1.decl_err)
                       ) AS sigma
              FROM extractedsources x1
                  ,lsm lsm1
                  ,catalogs c
             WHERE image_id = iimageid
               AND lsm1.cat_id = c.catid
               AND lsm1.zone BETWEEN FLOOR((x1.decl - itheta) / izoneheight)
                                 AND FLOOR((x1.decl + itheta) / izoneheight)
               AND lsm1.ra BETWEEN x1.ra - alpha(itheta,x1.decl)
                               AND x1.ra + alpha(itheta,x1.decl)
               AND lsm1.decl BETWEEN x1.decl - itheta
                                 AND x1.decl + itheta
               AND lsm1.x * x1.x + lsm1.y * x1.y + lsm1.z * x1.z > COS(RADIANS(itheta))
           ) t
  ;

END;
//

DELIMITER ;
