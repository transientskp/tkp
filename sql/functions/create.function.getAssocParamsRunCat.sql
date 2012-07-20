create function getAssocParamsRunCat(runcat_id INT
                                    ,xtrsrc_id INT
                                    ) RETURNS TABLE (distance_arcsec DOUBLE
                                                    ,r DOUBLE
                                                    ,loglr DOUBLE
                                                    )

begin

  return table (
    select 3600 * DEGREES(2 * ASIN(SQRT( (r1.x - x2.x) * (r1.x - x2.x)
                                       + (r1.y - x2.y) * (r1.y - x2.y)
                                       + (r1.z - x2.z) * (r1.z - x2.z)
                                       )
                                  / 2
                                  )
                         ) AS distance_arcsec
          ,3600 * SQRT( (r1.wm_ra * COS(RADIANS(r1.wm_decl)) - x2.ra * COS(RADIANS(x2.decl))) 
                      * (r1.wm_ra * COS(RADIANS(r1.wm_decl)) - x2.ra * COS(RADIANS(x2.decl))) 
                        / (r1.wm_ra_err * r1.wm_ra_err + x2.ra_err * x2.ra_err)
                      + (r1.wm_decl - x2.decl) * (r1.wm_decl - x2.decl)  
                        / (r1.wm_decl_err * r1.wm_decl_err + x2.decl_err * x2.decl_err)
                      ) AS r
          ,LOG10(EXP((( (r1.wm_ra * COS(RADIANS(r1.wm_decl)) - x2.ra * COS(RADIANS(x2.decl))) 
                      * (r1.wm_ra * COS(RADIANS(r1.wm_decl)) - x2.ra * COS(RADIANS(x2.decl))) 
                        / (r1.wm_ra_err * r1.wm_ra_err + x2.ra_err * x2.ra_err)
                      + (r1.wm_decl - x2.decl) * (r1.wm_decl - x2.decl)  
                        / (r1.wm_decl_err * r1.wm_decl_err + x2.decl_err * x2.decl_err)
                      )
                     ) / 2
                    )
                 /
                 (2 * PI() * SQRT(r1.wm_ra_err * r1.wm_ra_err + x2.ra_err * x2.ra_err) 
                           * SQRT(r1.wm_decl_err * r1.wm_decl_err + x2.decl_err * x2.decl_err) 
                           * 4.02439375E-06)
                ) AS loglr
  from runningcatalog r1
      ,extractedsources x1
 where r1.id = runcat_id
   and x1.id = xtrsrc_id
  )
  ;

END
;

