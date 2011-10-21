create function getAssocParamsRunCat(ixtrsrc_id INT
                                    ,ixtrsrcid INT
                                    ) RETURNS TABLE (assoc_distance_arcsec DOUBLE
                                                    ,assoc_r DOUBLE
                                                    ,assoc_log_lr DOUBLE
                                                    )

begin

  return table (
    select 3600 * DEGREES(2 * ASIN(SQRT( (r1.x - x2.x) * (r1.x - x2.x)
                                       + (r1.y - x2.y) * (r1.y - x2.y)
                                       + (r1.z - x2.z) * (r1.z - x2.z)
                                       )
                                  / 2
                                  )
                         ) AS assoc_distance_arcsec
          ,SQRT( (r1.wm_ra * COS(RADIANS(r1.wm_decl)) - x2.ra * COS(RADIANS(x2.decl))) * (r1.wm_ra * COS(RADIANS(r1.wm_decl)) - x2.ra * COS(RADIANS(x2.decl))) 
                / (r1.wm_ra_err * r1.wm_ra_err + x2.ra_err * x2.ra_err)
               + (r1.wm_decl - x2.decl) * (r1.wm_decl - x2.decl)  
                / (r1.wm_decl_err * r1.wm_decl_err + x2.decl_err * x2.decl_err)
               ) AS assoc_r
          ,LOG10(EXP((( (r1.wm_ra * COS(RADIANS(r1.wm_decl)) - x2.ra * COS(RADIANS(x2.decl))) * (r1.wm_ra * COS(RADIANS(r1.wm_decl)) - x2.ra * COS(RADIANS(x2.decl))) 
                       / (r1.wm_ra_err * r1.wm_ra_err + x2.ra_err * x2.ra_err)
                      + (r1.wm_decl - x2.decl) * (r1.wm_decl - x2.decl)  
                       / (r1.wm_decl_err * r1.wm_decl_err + x2.decl_err * x2.decl_err)
                      )
                     ) / 2
                    )
                 /
                 (2 * PI() * SQRT(r1.wm_ra_err * r1.wm_ra_err + x2.ra_err * x2.ra_err) * SQRT(r1.wm_decl_err * r1.wm_decl_err + x2.decl_err * x2.decl_err) * 4.02439375E-06)
                ) AS assoc_log_lr
  from runningcatalog r1
      ,extractedsources x2 
 where r1.xtrsrc_id = ixtrsrc_id
   and x2.xtrsrcid = ixtrsrcid
  )
  ;

END
;

