create function getAssocParams(id1 INT
                              ,id2 INT
                              ) RETURNS TABLE (distance_arcsec DOUBLE
                                              ,r DOUBLE
                                              ,loglr DOUBLE
                                              )

begin

  return table (
    select 3600 * DEGREES(2 * ASIN(SQRT( (x1.x - x2.x) * (x1.x - x2.x)
                                       + (x1.y - x2.y) * (x1.y - x2.y)
                                       + (x1.z - x2.z) * (x1.z - x2.z)
                                       )
                                  / 2
                                  )
                         ) AS distance_arcsec
          ,3600 * SQRT( (x1.ra * COS(RADIANS(x1.decl)) - x2.ra * COS(RADIANS(x2.decl))) 
                      * (x1.ra * COS(RADIANS(x1.decl)) - x2.ra * COS(RADIANS(x2.decl)))
                        / (x1.ra_err * x1.ra_err + x2.ra_err * x2.ra_err)
                      + (x1.decl - x2.decl) * (x1.decl - x2.decl)  
                        / (x1.decl_err * x1.decl_err + x2.decl_err * x2.decl_err)
                      ) AS r
          ,LOG10(EXP((( (x1.ra * COS(RADIANS(x1.decl)) - x2.ra * COS(RADIANS(x2.decl))) 
                      * (x1.ra * COS(RADIANS(x1.decl)) - x2.ra * COS(RADIANS(x2.decl))) 
                        / (x1.ra_err * x1.ra_err + x2.ra_err * x2.ra_err)
                      + (x1.decl - x2.decl) * (x1.decl - x2.decl) 
                        / (x1.decl_err * x1.decl_err + x2.decl_err * x2.decl_err)
                      )
                     ) / 2
                    )
                /
                (2 * PI() * SQRT(x1.ra_err * x1.ra_err + x2.ra_err * x2.ra_err) 
                          * SQRT(x1.decl_err * x1.decl_err + x2.decl_err * x2.decl_err) 
                          * 4.02439375E-06)
                ) AS loglr
  from extractedsource x1
      ,extractedsource x2 
 where x1.id = id1
   and x2.id = id2
  )
  ;

END
;

