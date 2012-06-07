create function getAssocParams(ixtrsrcid1 INT
                              ,ixtrsrcid2 INT
                              ) RETURNS TABLE (assoc_distance_arcsec DOUBLE
                                              ,assoc_r DOUBLE
                                              ,assoc_log_lr DOUBLE
                                              )

begin

  return table (
    select 3600 * DEGREES(2 * ASIN(SQRT( (x1.x - x2.x) * (x1.x - x2.x)
                                   + (x1.y - x2.y) * (x1.y - x2.y)
                                   + (x1.z - x2.z) * (x1.z - x2.z)
                                   )
                               / 2
                              )
                     ) AS assoc_distance_arcsec
          ,SQRT( (x1.ra * COS(RADIANS(x1.decl)) - x2.ra * COS(RADIANS(x2.decl))) * (x1.ra * COS(RADIANS(x1.decl)) - x2.ra * COS(RADIANS(x2.decl)))
                 / (x1.ra_err * x1.ra_err + x2.ra_err * x2.ra_err)
               + (x1.decl - x2.decl) * (x1.decl - x2.decl)  
                 / (x1.decl_err * x1.decl_err + x2.decl_err * x2.decl_err)
               ) AS assoc_r
          ,LOG10(EXP((( (x1.ra * COS(RADIANS(x1.decl)) - x2.ra * COS(RADIANS(x2.decl))) * (x1.ra * COS(RADIANS(x1.decl)) - x2.ra * COS(RADIANS(x2.decl))) 
                        / (x1.ra_err * x1.ra_err + x2.ra_err * x2.ra_err)
                       + (x1.decl - x2.decl) * (x1.decl - x2.decl) 
                        / (x1.decl_err * x1.decl_err + x2.decl_err * x2.decl_err)
                      )
                     ) / 2
                    )
                 /
                 (2 * PI() * SQRT(x1.ra_err * x1.ra_err + x2.ra_err * x2.ra_err) * SQRT(x1.decl_err * x1.decl_err + x2.decl_err * x2.decl_err) * 4.02439375E-06)
                ) AS assoc_log_lr
  from extractedsources x1
      ,extractedsources x2 
 where x1.xtrsrcid = ixtrsrcid1
   and x2.xtrsrcid = ixtrsrcid2
  )
  ;

END
;

