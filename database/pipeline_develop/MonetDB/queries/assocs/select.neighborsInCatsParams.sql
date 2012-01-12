    SELECT catsrcid
          ,catname
          ,catsrcname
          /*,band
          ,freq_eff*/
          ,ra
          ,decl
          ,ra_err
          ,decl_err
          ,i_peak_avg
          /*,i_peak_avg_err*/
          ,i_int_avg
          /*,i_int_avg_err*/
          ,3600 * DEGREES(2 * ASIN(SQRT((COS(RADIANS(85.89967)) * COS(RADIANS(153.43996)) - c1.x) * (COS(RADIANS(85.89967)) * COS(RADIANS(153.43996)) - c1.x)
                                    + (COS(RADIANS(85.89967)) * SIN(RADIANS(153.43996)) - c1.y) * (COS(RADIANS(85.89967)) * SIN(RADIANS(153.43996)) - c1.y)
                                    + (SIN(RADIANS(85.89967)) - c1.z) * (SIN(RADIANS(85.89967)) - c1.z)
                                   ) / 2) 
                     ) AS assoc_distance_arcsec
          ,3600* SQRT( (153.43996 * COS(RADIANS(85.89967)) - c1.ra * COS(RADIANS(c1.decl))) * (153.43996 * COS(RADIANS(85.89967)) - c1.ra * COS(RADIANS(c1.decl))) 
                 / (3.3248982967769707 * 3.3248982967769707 + c1.ra_err * c1.ra_err)
                + (85.89967 - c1.decl) * (85.89967 - c1.decl)  
                  / (3.4 * 3.4 + c1.decl_err * c1.decl_err)
               ) AS assoc_r
          /*,LOG10(EXP((( (153.43996 * COS(RADIANS(85.89967)) - c1.ra * COS(RADIANS(c1.decl))) * (153.43996 * COS(RADIANS(85.89967)) - c1.ra * COS(RADIANS(c1.decl))) 
                        / (3.3248982967769707 * 3.3248982967769707 + c1.ra_err * c1.ra_err)
                       + (85.89967 - c1.decl) * (85.89967 - c1.decl)  
                        / (3.4 * 3.4 + c1.decl_err * c1.decl_err)
                      )
                     ) / 2
                    )
                 /
                 (2 * PI() * SQRT(3.3248982967769707 * 3.3248982967769707 + c1.ra_err * c1.ra_err) * SQRT(3.4 * 3.4 + c1.decl_err * c1.decl_err) * 4.02439375E-06)
                ) AS assoc_loglr*/
      FROM catalogedsources c1
          ,catalogs c0
     WHERE c1.cat_id = c0.catid
       AND c1.x * COS(RADIANS(85.89967)) * COS(RADIANS(153.43996)) + c1.y * COS(RADIANS(85.89967)) * SIN(RADIANS(153.43996)) + c1.z * SIN(RADIANS(85.89967)) > COS(RADIANS(1.0))
       AND c1.zone BETWEEN CAST(FLOOR((85.89967 - 1.0) / 1.0) AS INTEGER)
                       AND CAST(FLOOR((85.89967 + 1.0) / 1.0) AS INTEGER)
       AND c1.ra BETWEEN 153.43996 - alpha(1.0, 85.89967)
                     AND 153.43996 + alpha(1.0, 85.89967)
       AND c1.decl BETWEEN 85.89967 - 1.0
                       AND 85.89967 + 1.0
ORDER BY assoc_r
        ,assoc_distance_arcsec
LIMIT 40
;

