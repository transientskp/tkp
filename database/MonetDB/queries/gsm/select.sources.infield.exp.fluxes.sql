DECLARE ira, idecl, itheta, iradius DOUBLE;

SET ira = 287.80216666666666;
--SET ira = 286.87425;
--SET ira = 70.0;
--SET ira = 53.316208333333336;
--SET ira = 289.89258333333333;

SET idecl = 9.096861111111112;
--SET idecl = 7.1466111111111115;
--SET idecl = 33.0;
--SET idecl = 20.0;
--SET idecl = 8.8555277777777786;
--SET idecl = 0.0017444444444444445;
SET itheta = 0.025;
SET iradius = 5.0;

SELECT t0.v_catsrcid
      ,t0.catsrcname
      ,t1.wm_catsrcid
      ,t2.wp_catsrcid
      ,t3.n_catsrcid
      ,t0.v_flux
      ,t1.wm_flux
      ,t2.wp_flux
      ,t3.n_flux
      /*,t0.v_flux_err
      ,t1.wm_flux_err
      ,t2.wp_flux_err
      ,t3.n_flux_err
      ,t1.wm_assoc_distance_arcsec
      ,t1.wm_assoc_r
      ,t2.wp_assoc_distance_arcsec
      ,t2.wp_assoc_r
      ,t3.n_assoc_distance_arcsec
      ,t3.n_assoc_r
      ,t0.pa
      ,t0.major
      ,t0.minor*/
      ,t0.ra
      ,t0.decl
  FROM (SELECT c1.catsrcid AS v_catsrcid
              ,c1.catsrcname
              ,c1.ra
              ,c1.decl
              ,c1.i_int_avg AS v_flux
              ,c1.i_int_avg_err AS v_flux_err
              ,c1.pa
              ,c1.major
              ,c1.minor
          FROM (SELECT catsrcid
                      ,catsrcname
                      ,ra
                      ,decl
                      ,pa
                      ,major
                      ,minor
                      ,i_int_avg
                      ,i_int_avg_err
                  FROM catalogedsources 
                 WHERE cat_id = 4
                   AND zone BETWEEN CAST(FLOOR(idecl - iradius) AS INTEGER)
                                AND CAST(FLOOR(idecl + iradius) AS INTEGER)
                   AND decl BETWEEN idecl - iradius
                                AND idecl + iradius
                   AND ra BETWEEN ira - alpha(iradius, idecl)
                              AND ira + alpha(iradius, idecl)
                   AND x * COS(RADIANS(idecl)) * COS(RADIANS(ira))
                      + y * COS(RADIANS(idecl)) * SIN(RADIANS(ira))
                      + z * SIN(RADIANS(idecl)) > COS(RADIANS(iradius))
               ) c1
       ) t0
       FULL OUTER JOIN 
       (SELECT c1.catsrcid AS v_catsrcid
              ,c2.catsrcid AS wm_catsrcid
              ,c2.i_int_avg AS wm_flux
              ,c2.i_int_avg_err AS wm_flux_err
              ,3600 * DEGREES(2 * ASIN(SQRT( (c1.x - c2.x) * (c1.x - c2.x)
                                           + (c1.y - c2.y) * (c1.y - c2.y)
                                           + (c1.z - c2.z) * (c1.z - c2.z)
                                           ) / 2) 
                             ) AS wm_assoc_distance_arcsec
              ,SQRT(((c1.ra * COS(RADIANS(c1.decl)) - c2.ra * COS(RADIANS(c2.decl)))
                * (c1.ra * COS(RADIANS(c1.decl)) - c2.ra * COS(RADIANS(c2.decl)))
                / (c1.ra_err * c1.ra_err + c2.ra_err * c2.ra_err))
               + ((c1.decl - c2.decl) * (c1.decl - c2.decl) 
                / (c1.decl_err * c1.decl_err + c2.decl_err * c2.decl_err))
               ) AS wm_assoc_r
          FROM (SELECT catsrcid
                      ,ra
                      ,decl
                      ,ra_err
                      ,decl_err
                      ,x
                      ,y
                      ,z
                  FROM catalogedsources 
                 WHERE cat_id = 4
                   AND zone BETWEEN CAST(FLOOR(idecl - iradius) AS INTEGER)
                                AND CAST(FLOOR(idecl + iradius) AS INTEGER)
                   AND decl BETWEEN idecl - iradius
                                AND idecl + iradius
                   AND ra BETWEEN ira - alpha(iradius, idecl)
                              AND ira + alpha(iradius, idecl)
                   AND x * COS(RADIANS(idecl)) * COS(RADIANS(ira))
                      + y * COS(RADIANS(idecl)) * SIN(RADIANS(ira))
                      + z * SIN(RADIANS(idecl)) > COS(RADIANS(iradius))
               ) c1
              ,(SELECT catsrcid
                      ,ra
                      ,decl
                      ,ra_err
                      ,decl_err
                      ,x
                      ,y
                      ,z
                      ,i_int_avg
                      ,i_int_avg_err
                  FROM catalogedsources 
                 WHERE cat_id = 5
                   AND zone BETWEEN CAST(FLOOR(idecl - iradius) AS INTEGER)
                                AND CAST(FLOOR(idecl + iradius) AS INTEGER)
                   AND decl BETWEEN idecl - iradius
                                AND idecl + iradius
                   AND ra BETWEEN ira - alpha(iradius, idecl)
                              AND ira + alpha(iradius, idecl)
                   AND x * COS(RADIANS(idecl)) * COS(RADIANS(ira))
                      + y * COS(RADIANS(idecl)) * SIN(RADIANS(ira))
                      + z * SIN(RADIANS(idecl)) > COS(RADIANS(iradius))
               ) c2
         WHERE c1.x * c2.x + c1.y * c2.y + c1.z * c2.z > COS(RADIANS(itheta))
           AND SQRT(((c1.ra * COS(RADIANS(c1.decl)) - c2.ra * COS(RADIANS(c2.decl)))
                * (c1.ra * COS(RADIANS(c1.decl)) - c2.ra * COS(RADIANS(c2.decl)))
                / (c1.ra_err * c1.ra_err + c2.ra_err * c2.ra_err))
               + ((c1.decl - c2.decl) * (c1.decl - c2.decl) 
                / (c1.decl_err * c1.decl_err + c2.decl_err * c2.decl_err))) < 0.0010325
       ) t1
    ON t0.v_catsrcid = t1.v_catsrcid
       FULL OUTER JOIN 
       (SELECT c1.catsrcid AS v_catsrcid
              ,c2.catsrcid AS wp_catsrcid
              ,c2.i_int_avg AS wp_flux
              ,c2.i_int_avg_err AS wp_flux_err
              ,3600 * DEGREES(2 * ASIN(SQRT( (c1.x - c2.x) * (c1.x - c2.x)
                                           + (c1.y - c2.y) * (c1.y - c2.y)
                                           + (c1.z - c2.z) * (c1.z - c2.z)
                                           ) / 2) 
                             ) AS wp_assoc_distance_arcsec
              ,SQRT(((c1.ra * COS(RADIANS(c1.decl)) - c2.ra * COS(RADIANS(c2.decl)))
                * (c1.ra * COS(RADIANS(c1.decl)) - c2.ra * COS(RADIANS(c2.decl)))
                / (c1.ra_err * c1.ra_err + c2.ra_err * c2.ra_err))
               + ((c1.decl - c2.decl) * (c1.decl - c2.decl) 
                / (c1.decl_err * c1.decl_err + c2.decl_err * c2.decl_err))
               ) AS wp_assoc_r
          FROM (SELECT catsrcid
                      ,ra
                      ,decl
                      ,ra_err
                      ,decl_err
                      ,x
                      ,y
                      ,z
                  FROM catalogedsources 
                 WHERE cat_id = 4
                   AND zone BETWEEN CAST(FLOOR(idecl - iradius) AS INTEGER)
                                AND CAST(FLOOR(idecl + iradius) AS INTEGER)
                   AND decl BETWEEN idecl - iradius
                                AND idecl + iradius
                   AND ra BETWEEN ira - alpha(iradius, idecl)
                              AND ira + alpha(iradius, idecl)
                   AND x * COS(RADIANS(idecl)) * COS(RADIANS(ira))
                      + y * COS(RADIANS(idecl)) * SIN(RADIANS(ira))
                      + z * SIN(RADIANS(idecl)) > COS(RADIANS(iradius))
               ) c1
              ,(SELECT catsrcid
                      ,ra
                      ,decl
                      ,ra_err
                      ,decl_err
                      ,x
                      ,y
                      ,z
                      ,i_int_avg
                      ,i_int_avg_err
                  FROM catalogedsources 
                 WHERE cat_id = 6
                   AND zone BETWEEN CAST(FLOOR(idecl - iradius) AS INTEGER)
                                AND CAST(FLOOR(idecl + iradius) AS INTEGER)
                   AND decl BETWEEN idecl - iradius
                                AND idecl + iradius
                   AND ra BETWEEN ira - alpha(iradius, idecl)
                              AND ira + alpha(iradius, idecl)
                   AND x * COS(RADIANS(idecl)) * COS(RADIANS(ira))
                      + y * COS(RADIANS(idecl)) * SIN(RADIANS(ira))
                      + z * SIN(RADIANS(idecl)) > COS(RADIANS(iradius))
               ) c2
         WHERE c1.x * c2.x + c1.y * c2.y + c1.z * c2.z > COS(RADIANS(itheta))
           AND SQRT(((c1.ra * COS(RADIANS(c1.decl)) - c2.ra * COS(RADIANS(c2.decl)))
                * (c1.ra * COS(RADIANS(c1.decl)) - c2.ra * COS(RADIANS(c2.decl)))
                / (c1.ra_err * c1.ra_err + c2.ra_err * c2.ra_err))
               + ((c1.decl - c2.decl) * (c1.decl - c2.decl) 
                / (c1.decl_err * c1.decl_err + c2.decl_err * c2.decl_err))) < 0.0010325
       ) t2
    ON t0.v_catsrcid = t2.v_catsrcid
       FULL OUTER JOIN 
       (SELECT c1.catsrcid AS v_catsrcid
              ,c2.catsrcid AS n_catsrcid
              ,c2.i_int_avg AS n_flux
              ,c2.i_int_avg_err AS n_flux_err
              ,3600 * DEGREES(2 * ASIN(SQRT( (c1.x - c2.x) * (c1.x - c2.x)
                                           + (c1.y - c2.y) * (c1.y - c2.y)
                                           + (c1.z - c2.z) * (c1.z - c2.z)
                                           ) / 2) 
                             ) AS n_assoc_distance_arcsec
              ,SQRT(((c1.ra * COS(RADIANS(c1.decl)) - c2.ra * COS(RADIANS(c2.decl)))
                * (c1.ra * COS(RADIANS(c1.decl)) - c2.ra * COS(RADIANS(c2.decl)))
                / (c1.ra_err * c1.ra_err + c2.ra_err * c2.ra_err))
               + ((c1.decl - c2.decl) * (c1.decl - c2.decl) 
                / (c1.decl_err * c1.decl_err + c2.decl_err * c2.decl_err))
               ) AS n_assoc_r
          FROM (SELECT catsrcid
                      ,ra
                      ,decl
                      ,ra_err
                      ,decl_err
                      ,x
                      ,y
                      ,z
                  FROM catalogedsources 
                 WHERE cat_id = 4
                   AND zone BETWEEN CAST(FLOOR(idecl - iradius) AS INTEGER)
                                AND CAST(FLOOR(idecl + iradius) AS INTEGER)
                   AND decl BETWEEN idecl - iradius
                                AND idecl + iradius
                   AND ra BETWEEN ira - alpha(iradius, idecl)
                              AND ira + alpha(iradius, idecl)
                   AND x * COS(RADIANS(idecl)) * COS(RADIANS(ira))
                      + y * COS(RADIANS(idecl)) * SIN(RADIANS(ira))
                      + z * SIN(RADIANS(idecl)) > COS(RADIANS(iradius))
               ) c1
              ,(SELECT catsrcid
                      ,ra
                      ,decl
                      ,ra_err
                      ,decl_err
                      ,x
                      ,y
                      ,z
                      ,i_int_avg
                      ,i_int_avg_err
                  FROM catalogedsources 
                 WHERE cat_id = 3
                   AND zone BETWEEN CAST(FLOOR(idecl - iradius) AS INTEGER)
                                AND CAST(FLOOR(idecl + iradius) AS INTEGER)
                   AND decl BETWEEN idecl - iradius
                                AND idecl + iradius
                   AND ra BETWEEN ira - alpha(iradius, idecl)
                              AND ira + alpha(iradius, idecl)
                   AND x * COS(RADIANS(idecl)) * COS(RADIANS(ira))
                      + y * COS(RADIANS(idecl)) * SIN(RADIANS(ira))
                      + z * SIN(RADIANS(idecl)) > COS(RADIANS(iradius))
               ) c2
         WHERE c1.x * c2.x + c1.y * c2.y + c1.z * c2.z > COS(RADIANS(itheta))
           AND SQRT(((c1.ra * COS(RADIANS(c1.decl)) - c2.ra * COS(RADIANS(c2.decl)))
                * (c1.ra * COS(RADIANS(c1.decl)) - c2.ra * COS(RADIANS(c2.decl)))
                / (c1.ra_err * c1.ra_err + c2.ra_err * c2.ra_err))
               + ((c1.decl - c2.decl) * (c1.decl - c2.decl) 
                / (c1.decl_err * c1.decl_err + c2.decl_err * c2.decl_err))) < 0.0010325
         ) t3
    ON t0.v_catsrcid = t3.v_catsrcid
ORDER BY t0.ra
;

