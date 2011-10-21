--DROP FUNCTION getNeighborBrightestInCat;
/*
CREATE FUNCTION testReturnTable(catname VARCHAR(50)
                               ,ira DOUBLE
                               ,idecl DOUBLE) 
RETURNS TABLE (ocatsrcid INT
              ,ozoneheight DOUBLE
              )
BEGIN
  
  RETURN TABLE 
    (SELECT 1
           ,2
    )
  ;

END;
*/


CREATE FUNCTION getNeighborBrightestInCat(icatname VARCHAR(50)
                                         ,itheta DOUBLE
                                         ,ira DOUBLE
                                         ,idecl DOUBLE
                                         ) RETURNS TABLE (catsrcid INT
                                                         ,ra DOUBLE
                                                         ,decl DOUBLE
                                                         ,freq_eff DOUBLE
                                                         ,i_int_avg DOUBLE
                                                         ,i_int_avg_err DOUBLE
                                                         ,dist_arcsec DOUBLE
                                                         )
BEGIN
  
  DECLARE izoneheight DOUBLE;

  /*SELECT zoneheight 
    INTO izoneheight
    FROM zoneheight
  ;
  */

  SET izoneheight = 1.0;

  RETURN TABLE 
    (
    SELECT catsrcid
          ,ra
          ,decl
          ,c1.freq_eff
          ,c1.i_int_avg
          ,c1.i_int_avg_err
          ,3600 * DEGREES(2 * ASIN(SQRT( (c1.x - COS(RADIANS(idecl)) * COS(RADIANS(ira))) 
                                         * (c1.x - COS(RADIANS(idecl)) * COS(RADIANS(ira))) 
                                       + (c1.y - COS(RADIANS(idecl)) * SIN(RADIANS(ira)))
                                         * (c1.y - COS(RADIANS(idecl)) * SIN(RADIANS(ira)))
                                       + (c1.z - SIN(RADIANS(idecl))) 
                                         * (c1.z - SIN(RADIANS(idecl)))
                                       ) 
                                  / 2
                                  )
                         ) as dist_arcsec
      FROM catalogedsources c1
          ,catalogs c0
       WHERE c1.cat_id = c0.catid
         AND c0.catname = UPPER(icatname)
         AND c1.x * COS(RADIANS(idecl)) * COS(RADIANS(ira)) 
             + c1.y * COS(RADIANS(idecl)) * SIN(RADIANS(ira)) 
             + c1.z * SIN(RADIANS(idecl)) > COS(RADIANS(itheta))
         AND c1.zone BETWEEN CAST(FLOOR((idecl - itheta) / izoneheight) AS INTEGER)
                         AND CAST(FLOOR((idecl + itheta) / izoneheight) AS INTEGER)
         AND c1.ra BETWEEN ira - alpha(itheta, idecl)
                       AND ira + alpha(itheta, idecl)
         AND c1.decl BETWEEN idecl - itheta
                         AND idecl + itheta
         AND c1.i_int_avg = (SELECT MAX(c1.i_int_avg)
                               FROM catalogedsources c1
                                   ,catalogs c0
                              WHERE c1.cat_id = c0.catid
                                AND c0.catname = icatname
                                AND c1.x * COS(RADIANS(idecl)) * COS(RADIANS(ira)) 
                                    + c1.y * COS(RADIANS(idecl)) * SIN(RADIANS(ira)) 
                                    + c1.z * SIN(RADIANS(idecl)) > COS(RADIANS(itheta))
                                AND c1.zone BETWEEN CAST(FLOOR((idecl - itheta) / izoneheight) AS INTEGER)
                                                AND CAST(FLOOR((idecl + itheta) / izoneheight) AS INTEGER)
                                AND c1.ra BETWEEN ira - alpha(itheta, idecl)
                                              AND ira + alpha(itheta, idecl)
                                AND c1.decl BETWEEN idecl - itheta
                                                AND idecl + itheta
                            )
    )
    ;

END;
