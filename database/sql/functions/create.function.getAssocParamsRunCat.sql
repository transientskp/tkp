create function getAssocParamsRunCat(runcat_id INT
                                    ,xtrsrc_id INT
                                    ) RETURNS TABLE (distance_arcsec DOUBLE
                                                    ,r DOUBLE
                                                    ,loglr DOUBLE
                                                    )

begin

  return table (
    select 3600 * DEGREES(2 * ASIN(SQRT( (r.x - x.x) * (r.x - x.x)
                                       + (r.y - x.y) * (r.y - x.y)
                                       + (r.z - x.z) * (r.z - x.z)
                                       )
                                  / 2
                                  )
                         ) AS distance_arcsec
          ,3600 * SQRT( (r.wm_ra * COS(RADIANS(r.wm_decl)) - x.ra * COS(RADIANS(x.decl))) 
                      * (r.wm_ra * COS(RADIANS(r.wm_decl)) - x.ra * COS(RADIANS(x.decl))) 
                        / (r.wm_ra_err * r.wm_ra_err + x.ra_err * x.ra_err)
                      + (r.wm_decl - x.decl) * (r.wm_decl - x.decl)  
                        / (r.wm_decl_err * r.wm_decl_err + x.decl_err * x.decl_err)
                      ) AS r
          ,LOG10(EXP((( (r.wm_ra * COS(RADIANS(r.wm_decl)) - x.ra * COS(RADIANS(x.decl))) 
                      * (r.wm_ra * COS(RADIANS(r.wm_decl)) - x.ra * COS(RADIANS(x.decl))) 
                        / (r.wm_ra_err * r.wm_ra_err + x.ra_err * x.ra_err)
                      + (r.wm_decl - x.decl) * (r.wm_decl - x.decl)  
                        / (r.wm_decl_err * r.wm_decl_err + x.decl_err * x.decl_err)
                      )
                     ) / 2
                    )
                 /
                 (2 * PI() * SQRT(r.wm_ra_err * r.wm_ra_err + x.ra_err * x.ra_err) 
                           * SQRT(r.wm_decl_err * r.wm_decl_err + x.decl_err * x.decl_err) 
                           * 4.02439375E-06)
                ) AS loglr
  from runningcatalog r
      ,extractedsource x
 where r.id = runcat_id
   and x.id = xtrsrc_id
  )
  ;

END
;

