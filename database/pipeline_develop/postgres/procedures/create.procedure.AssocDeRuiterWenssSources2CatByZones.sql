--DROP PROCEDURE AssocDeRuiterWenssSources2CatByZones;

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
CREATE PROCEDURE AssocDeRuiterWenssSources2CatByZones(iimageid INT)

BEGIN

  DECLARE izoneheight, itheta, N_density double precision;
  DECLARE izone_min, izone_max INT;

  /*SELECT zoneheight 
    INTO izoneheight
    FROM zoneheight
  ;*/
  SET izoneheight = 1;
  SET itheta = 0.025; /* := 90" */
  /* The average NVSS source density per arcsec^2 in the decl strip 44 - 64 deg */
  SET N_density = 4.017E-06; 

  /* Here we insert the sources that coud be associated */
  SET izone_min = 40;
  SET izone_max = 70;
  SET izone_max = izone_min + 1;
  WHILE izone_max <= 70 DO
    INSERT INTO assoccatsources
      (xtrsrc_id
      ,assoc_catsrc_id
      ,assoc_distance_arcsec
      ,assoc_lr_method
      ,assoc_r
      ,assoc_lr
      )
      SELECT x1.xtrsrcid AS xtrsrc_id
            ,c1.catsrcid AS assoc_catsrc_id
            ,3600 * DEGREES(2 * ASIN(SQRT((c1.x - x1.x) * (c1.x - x1.x)
                                         + (c1.y - x1.y) * (c1.y - x1.y)
                                         + (c1.z - x1.z) * (c1.z - x1.z)
                                         ) / 2) ) AS assoc_distance_arcsec
            ,6 AS assoc_lr_method
            ,3600 * SQRT((c1.ra - x1.ra) * COS(RADIANS(x1.decl))
                         *(c1.ra - x1.ra) * COS(RADIANS(x1.decl))
                         /(x1.ra_err * x1.ra_err + c1.ra_err * c1.ra_err)
                        +(c1.decl - x1.decl) * (c1.decl - x1.decl)
                         /(x1.decl_err * x1.decl_err + c1.decl_err * c1.decl_err)
                        ) AS assoc_r
            ,LOG10(EXP(-6480000 
                        * (((c1.ra - x1.ra) * COS(RADIANS(x1.decl))
                            *(c1.ra - x1.ra) * COS(RADIANS(x1.decl))
                            /(x1.ra_err * x1.ra_err + c1.ra_err * c1.ra_err)
                           +(c1.decl - x1.decl) * (c1.decl - x1.decl)
                            /(x1.decl_err * x1.decl_err + c1.decl_err * c1.decl_err)
                           )
                          )
                      )
                   / (2 * PI() 
                     * SQRT(x1.ra_err * x1.ra_err + c1.ra_err * c1.ra_err)
                     * SQRT(x1.decl_err * x1.decl_err + c1.decl_err * c1.decl_err)
                     * N_density)
                  ) AS assoc_lr
        FROM extractedsources x1
            ,catalogedsources c1
       WHERE image_id = iimageid
         AND x1.zone >= izone_min
         AND x1.zone < izone_max
         /* Only catalogues loaded at set-up are WENSS and NVSS */
         AND (c1.src_type IS NULL
              OR c1.src_type = 'S'
             )
         AND c1.fit_probl IS NULL
         AND c1.zone BETWEEN CAST(FLOOR((x1.decl - itheta) / izoneheight) AS INTEGER)
                           AND CAST(FLOOR((x1.decl + itheta) / izoneheight) AS INTEGER)
         AND c1.ra BETWEEN x1.ra - alpha(itheta,x1.decl)
                         AND x1.ra + alpha(itheta,x1.decl)
         AND c1.decl BETWEEN x1.decl - itheta
                           AND x1.decl + itheta
         AND c1.x * x1.x + c1.y * x1.y + c1.z * x1.z > COS(RADIANS(itheta))
    ;
    SET izone_min = izone_min + 1;
    SET izone_max = izone_min + 1;
  END WHILE;

END;

