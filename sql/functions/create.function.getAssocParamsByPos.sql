--DROP FUNCTION getAssocParamsByPos;

CREATE FUNCTION getAssocParamsByPos(ira1 DOUBLE
                                   ,idecl1 DOUBLE
                                   ,ira_err1 DOUBLE
                                   ,idecl_err1 DOUBLE
                                   ,ira2 DOUBLE
                                   ,idecl2 DOUBLE
                                   ,ira_err2 DOUBLE
                                   ,idecl_err2 DOUBLE
                                   ) RETURNS TABLE (assoc_distance_arcsec DOUBLE
                                                   ,assoc_r DOUBLE
                                                   ,assoc_log_lr DOUBLE
                                                   )

BEGIN

  DECLARE x1, y1, z1, x2, y2, z2, ixy DOUBLE;
  
  SET ixy = COS(RADIANS(idecl1));
  SET x1 = ixy * COS(RADIANS(ira1));
  SET y1 = ixy * SIN(RADIANS(ira1));
  SET z1 = SIN(RADIANS(idecl1));
  
  SET ixy = COS(RADIANS(idecl2));
  SET x2 = ixy * COS(RADIANS(ira2));
  SET y2 = ixy * SIN(RADIANS(ira2));
  SET z2 = SIN(RADIANS(idecl2));

  RETURN TABLE (
    select 3600 * DEGREES(2 * ASIN(SQRT( (x1 - x2) * (x1 - x2)
                                       + (y1 - y2) * (y1 - y2)
                                       + (z1 - z2) * (z1 - z2)
                                       )
                                  / 2
                                  )
                         ) AS assoc_distance_arcsec
          ,3600 * SQRT(  (ira1 * COS(RADIANS(idecl1)) - ira2 * COS(RADIANS(idecl2))) 
                       * (ira1 * COS(RADIANS(idecl1)) - ira2 * COS(RADIANS(idecl2)))
                       / (ira_err1 * ira_err1 + ira_err2 * ira_err2)
                      + (idecl1 - idecl2) * (idecl1 - idecl2)  
                       / (idecl_err1 * idecl_err1 + idecl_err2 * idecl_err2)
                      ) AS assoc_r
          ,LOG10(EXP(((  (ira1 * COS(RADIANS(idecl1)) - ira2 * COS(RADIANS(idecl2))) 
                       * (ira1 * COS(RADIANS(idecl1)) - ira2 * COS(RADIANS(idecl2))) 
                       / (ira_err1 * ira_err1 + ira_err2 * ira_err2)
                      + (idecl1 - idecl2) * (idecl1 - idecl2)  
                       / (idecl_err1 * idecl_err1 + idecl_err2 * idecl_err2)
                      )
                     ) / 2
                    )
                 /
                 (2 * PI() * SQRT(ira_err1 * ira_err1 + ira_err2 * ira_err2)    
                           * SQRT(idecl_err1 * idecl_err1 + idecl_err2 * idecl_err2) * 4.02439375E-06
                 )
                ) AS assoc_log_lr
  )
  ;

END
;

