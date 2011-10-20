DROP FUNCTION getNeighborBrightestInCat;
/*
CREATE FUNCTION testReturnTable(catname VARCHAR(50)
                               ,ira double precision
                               ,idecl double precision) 
RETURNS TABLE (ocatsrcid INT
              ,ozoneheight double precision
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
                                         ,itheta double precision
                                         ,ira double precision
                                         ,idecl double precision
                                         ) RETURNS TABLE (catsrcid INT
                                                         ,ra double precision
                                                         ,decl double precision
                                                         ,freq_eff double precision
                                                         ,i_int_avg double precision
                                                         ,i_int_avg_err double precision
                                                         ,dist_arcsec double precision
                                                         ) as $$
BEGIN
  
  DECLARE izoneheight double precision;

  SELECT zoneheight 
    INTO izoneheight
    FROM zoneheight
  ;

  RETURN TABLE 
    (
    SELECT catsrcid
          ,ra
          ,decl
          ,c1.freq_eff
          ,c1.i_int_avg
          ,c1.i_int_avg_err
          ,3600 * DEGREES(2 * ASIN(SQRT( (c1.x - COS(radians(idecl)) * COS(radians(ira))) 
                                         * (c1.x - COS(radians(idecl)) * COS(radians(ira))) 
                                       + (c1.y - COS(radians(idecl)) * SIN(radians(ira)))
                                         * (c1.y - COS(radians(idecl)) * SIN(radians(ira)))
                                       + (c1.z - SIN(radians(idecl))) 
                                         * (c1.z - SIN(radians(idecl)))
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
$$ language plpgsql;
