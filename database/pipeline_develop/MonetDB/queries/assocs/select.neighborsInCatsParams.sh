#!/bin/bash

while read ira idecl ira_err idecl_err; do
    query="
    SELECT catsrcid
          ,catname
          ,catsrcname
          ,band
          ,freq_eff
          ,ra
          ,decl
          ,ra_err
          ,decl_err
          ,i_peak_avg
          ,i_peak_avg_err
          ,i_int_avg
          ,i_int_avg_err
          ,3600 * DEGREES(2 * ASIN(SQRT((COS(RADIANS($idecl)) * COS(RADIANS($ira)) - c1.x) * (COS(RADIANS($idecl)) * COS(RADIANS($ira)) - c1.x)
                                    + (COS(RADIANS($idecl)) * SIN(RADIANS($ira)) - c1.y) * (COS(RADIANS($idecl)) * SIN(RADIANS($ira)) - c1.y)
                                    + (SIN(RADIANS($idecl)) - c1.z) * (SIN(RADIANS($idecl)) - c1.z)
                                   ) / 2) 
                     ) AS assoc_distance_arcsec
          ,SQRT( ($ira * COS(RADIANS($idecl)) - c1.ra * COS(RADIANS(c1.decl))) * ($ira * COS(RADIANS($idecl)) - c1.ra * COS(RADIANS(c1.decl))) 
                 / ($ira_err * $ira_err + c1.ra_err * c1.ra_err)
                + ($idecl - c1.decl) * ($idecl - c1.decl)  
                  / ($idecl_err * $idecl_err + c1.decl_err * c1.decl_err)
               ) AS assoc_r
          ,LOG10(EXP((( ($ira * COS(RADIANS($idecl)) - c1.ra * COS(RADIANS(c1.decl))) * ($ira * COS(RADIANS($idecl)) - c1.ra * COS(RADIANS(c1.decl))) 
                        / ($ira_err * $ira_err + c1.ra_err * c1.ra_err)
                       + ($idecl - c1.decl) * ($idecl - c1.decl)  
                        / ($idecl_err * $idecl_err + c1.decl_err * c1.decl_err)
                      )
                     ) / 2
                    )
                 /
                 (2 * PI() * SQRT($ira_err * $ira_err + c1.ra_err * c1.ra_err) * SQRT($idecl_err * $idecl_err + c1.decl_err * c1.decl_err) * 4.02439375E-06)
                ) AS assoc_loglr
      FROM catalogedsources c1
          ,catalogs c0
     WHERE c1.cat_id = c0.catid
       AND c1.x * COS(RADIANS($idecl)) * COS(RADIANS($ira)) + c1.y * COS(RADIANS($idecl)) * SIN(RADIANS($ira)) + c1.z * SIN(RADIANS($idecl)) > COS(RADIANS(1.0))
       AND c1.zone BETWEEN CAST(FLOOR(($idecl - 1.0) / 1.0) AS INTEGER)
                       AND CAST(FLOOR(($idecl + 1.0) / 1.0) AS INTEGER)
       AND c1.ra BETWEEN $ira - alpha(1.0, $idecl)
                     AND $ira + alpha(1.0, $idecl)
       AND c1.decl BETWEEN $idecl - 1.0
                       AND $idecl + 1.0
    ;
    "

    DOTMONETDBFILE=~/.gsm mclient -dgsm -s"$query"
    echo "READY"
done

