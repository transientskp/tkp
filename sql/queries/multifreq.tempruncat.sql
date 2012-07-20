SELECT rc.id
  FROM runningcatalog rc
      ,extractedsource x0
      ,image 
 WHERE image.id = 45
   AND x0.image = image.id
   AND image.dataset = rc.dataset
   AND rc.zone BETWEEN CAST(FLOOR(x0.decl - 0.025) as INTEGER)
                   AND CAST(FLOOR(x0.decl + 0.025) as INTEGER)
   AND rc.wm_decl BETWEEN x0.decl - 0.025
                      AND x0.decl + 0.025
   AND rc.wm_ra BETWEEN x0.ra - alpha(0.025, x0.decl)
                    AND x0.ra + alpha(0.025, x0.decl)
   AND SQRT(  (x0.ra * COS(RADIANS(x0.decl)) - rc.wm_ra * COS(RADIANS(rc.wm_decl)))
            * (x0.ra * COS(RADIANS(x0.decl)) - rc.wm_ra * COS(RADIANS(rc.wm_decl)))
             / (x0.ra_err * x0.ra_err + rc.wm_ra_err * rc.wm_ra_err)
           + (x0.decl - rc.wm_decl) * (x0.decl - rc.wm_decl)
             / (x0.decl_err * x0.decl_err + rc.wm_decl_err * rc.wm_decl_err)
           ) < 5./3600.
