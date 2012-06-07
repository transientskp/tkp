--DROP FUNCTION getNearestNeighborInImage;

CREATE FUNCTION getNearestNeighborInImage(iimageid INT 
                                         ,ixtrsrcid INT
                                         ) RETURNS INT
BEGIN
  
  DECLARE oxtrsrcid INT;
  DECLARE izoneheight, itheta DOUBLE;
  
  SET itheta = 1;
  
  /* TODO 
  SELECT zoneheight
    INTO izoneheight
    FROM zoneheight
  ;*/
  SET izoneheight = 1;

  SELECT x2.xtrsrcid
    INTO oxtrsrcid
    FROM extractedsources x1
        ,extractedsources x2
   WHERE x1.xtrsrcid = ixtrsrcid
     AND x2.image_id = iimageid 
     AND x2.xtrsrcid <> ixtrsrcid
     AND x2.x * x1.x + x2.y * x1.y + x2.z * x1.z > COS(RADIANS(itheta))
     AND x2.zone BETWEEN CAST(FLOOR((x1.decl - itheta) / izoneheight) AS INTEGER)
                     AND CAST(FLOOR((x1.decl + itheta) / izoneheight) AS INTEGER)
     AND x2.ra BETWEEN x1.ra - alpha(itheta, x1.decl)
                   AND x1.ra + alpha(itheta, x1.decl)
     AND x2.decl BETWEEN x1.decl - itheta
                     AND x1.decl + itheta
     AND POWER((COS(RADIANS(x2.decl)) * COS(RADIANS(x2.ra))
               - COS(RADIANS(x1.decl)) * COS(RADIANS(x1.ra))
               ), 2)
        + POWER((COS(RADIANS(x2.decl)) * SIN(RADIANS(x2.ra))
                - COS(RADIANS(x1.decl)) * SIN(RADIANS(x1.ra))
                ), 2)
        + POWER((SIN(RADIANS(x2.decl))
                - SIN(RADIANS(x1.decl))
                ), 2) = (SELECT MIN(POWER((COS(RADIANS(x2.decl)) * COS(RADIANS(x2.ra))
                                          - COS(RADIANS(x1.decl)) * COS(RADIANS(x1.ra))
                                          ), 2)
                                   + POWER((COS(RADIANS(x2.decl)) * SIN(RADIANS(x2.ra))
                                           - COS(RADIANS(x1.decl)) * SIN(RADIANS(x1.ra))
                                           ), 2)
                                   + POWER((SIN(RADIANS(x2.decl))
                                           - SIN(RADIANS(x1.decl))
                                           ), 2)
                                   )
                           FROM extractedsources x1
                               ,extractedsources x2
                          WHERE x1.xtrsrcid = ixtrsrcid
                            AND x2.image_id = iimageid 
                            AND x2.xtrsrcid <> ixtrsrcid
                            AND x2.x * x1.x + x2.y * x1.y + x2.z * x1.z > COS(RADIANS(itheta))
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

