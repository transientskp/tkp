--DROP FUNCTION getNearestNeighborInImage;

CREATE FUNCTION getNearestNeighborInImage(iimageid INT 
                                         ,ixtrsrcid INT
                                         ) RETURNS INT as $$
  DECLARE oxtrsrcid INT;
  DECLARE izoneheight double precision;
declare itheta double precision;
  
BEGIN
  
  itheta := 1;
  
  /* TODO 
  SELECT zoneheight
    INTO izoneheight
    FROM zoneheight
  ;*/
  izoneheight := 1;

  SELECT x2.xtrsrcid
    INTO oxtrsrcid
    FROM extractedsources x1
        ,extractedsources x2
   WHERE x1.xtrsrcid = ixtrsrcid
     AND x2.image_id = iimageid 
     AND x2.xtrsrcid <> ixtrsrcid
     AND x2.x * x1.x + x2.y * x1.y + x2.z * x1.z > COS(radians(itheta))
     AND x2.zone BETWEEN CAST(FLOOR((x1.decl - itheta) / izoneheight) AS INTEGER)
                     AND CAST(FLOOR((x1.decl + itheta) / izoneheight) AS INTEGER)
     AND x2.ra BETWEEN x1.ra - alpha(itheta, x1.decl)
                   AND x1.ra + alpha(itheta, x1.decl)
     AND x2.decl BETWEEN x1.decl - itheta
                     AND x1.decl + itheta
     AND POWER((COS(radians(x2.decl)) * COS(radians(x2.ra))
               - COS(radians(x1.decl)) * COS(radians(x1.ra))
               ), 2)
        + POWER((COS(radians(x2.decl)) * SIN(radians(x2.ra))
                - COS(radians(x1.decl)) * SIN(radians(x1.ra))
                ), 2)
        + POWER((SIN(radians(x2.decl))
                - SIN(radians(x1.decl))
                ), 2) = (SELECT MIN(POWER((COS(radians(x2.decl)) * COS(radians(x2.ra))
                                          - COS(radians(x1.decl)) * COS(radians(x1.ra))
                                          ), 2)
                                   + POWER((COS(radians(x2.decl)) * SIN(radians(x2.ra))
                                           - COS(radians(x1.decl)) * SIN(radians(x1.ra))
                                           ), 2)
                                   + POWER((SIN(radians(x2.decl))
                                           - SIN(radians(x1.decl))
                                           ), 2)
                                   )
                           FROM extractedsources x1
                               ,extractedsources x2
                          WHERE x1.xtrsrcid = ixtrsrcid
                            AND x2.image_id = iimageid 
                            AND x2.xtrsrcid <> ixtrsrcid
                            AND x2.x * x1.x + x2.y * x1.y + x2.z * x1.z > COS(radians(itheta))
                            AND x2.zone BETWEEN CAST(FLOOR((x1.decl - itheta) / izoneheight) AS INTEGER)
                                            AND CAST(FLOOR((x1.decl + itheta) / izoneheight) AS INTEGER)
                            AND x2.ra BETWEEN x1.ra - alpha(itheta, x1.decl)
                                          AND x1.ra + alpha(itheta, x1.decl)
                            AND x2.decl BETWEEN x1.decl - itheta
                                            AND x1.decl + itheta
                        )
  ;

  RETURN oxtrsrcid;

END;
$$ language plpgsql;
