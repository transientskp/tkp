--DROP PROCEDURE AssocWenssSources2CatByZones;

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
CREATE PROCEDURE AssocWenssSources2CatByZones(iimageid INT
                                             )

BEGIN

  DECLARE izoneheight, itheta, N_density DOUBLE;
  DECLARE izone_min, izone_max INT;

  SELECT zoneheight 
    INTO izoneheight
    FROM zoneheight
  ;
  SET itheta = 0.025; /* = 90" */
  SET N_density = 4.02439375E-06; /* The average NVSS source density per arcsec^2 */

  /* Here we insert the sources that coud be associated */
  SET izone_min = 28;
  SET izone_max = izone_min + 1;
  WHILE izone_max <= 90 DO
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
            ,t.catsrcid
            /*,t.assoc_weight*/
            ,t.assoc_distance_arcsec
            /* method = 4: Sutherland&Saunders (1992) */
            ,4 AS assoc_lr_method
            ,t.assoc_distance_arcsec / SQRT(t.sigma_ra * t.sigma_ra + t.sigma_decl * t.sigma_decl) AS assoc_r
            ,LOG10(EXP(-t.assoc_distance_arcsec * t.assoc_distance_arcsec 
                      / (2 * (t.sigma_ra * t.sigma_ra + t.sigma_decl * t.sigma_decl))
                      ) 
                  / (2 * PI() * t.sigma_ra * t.sigma_decl * N_density)
                  ) AS assoc_lr
        FROM (SELECT x1.xtrsrcid
                    ,c.catname
                    ,lsm1.lsmid AS catsrcid
                    /*,localsourcedensityincat_deg2(c.catname,itheta,x1.xtrsrcid) AS assoc_weight*/
                    ,3600 * DEGREES(2 * ASIN(SQRT((lsm1.x - x1.x) * (lsm1.x - x1.x)
                                                 + (lsm1.y - x1.y) * (lsm1.y - x1.y)
                                                 + (lsm1.z - x1.z) * (lsm1.z - x1.z)
                                                 ) / 2) ) AS assoc_distance_arcsec
                    ,SQRT((x1.ra_err) * (x1.ra_err) + (lsm1.ra_err) * (lsm1.ra_err)) AS sigma_ra
                    ,SQRT((x1.decl_err) * (x1.decl_err) + (lsm1.decl_err) * (lsm1.decl_err)) AS sigma_decl
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
    SET izone_min = izone_min + 1;
    SET izone_max = izone_min + 1;
  END WHILE;
END;

