--DROP FUNCTION getNearestNeighborInCat;

CREATE FUNCTION getNearestNeighborInCat(icatname VARCHAR(50)
                                       ,itheta DOUBLE
                                       ,ixtrsrcid INT
                                       ) RETURNS INT
BEGIN
  
  DECLARE icatsrcid INT;
  DECLARE izoneheight DOUBLE;

  SELECT zoneheight
    INTO izoneheight
    FROM zoneheight
  ;

  SELECT catsrcid
    INTO icatsrcid
    FROM extractedsources x1
        ,catalogedsources c1
        ,catalogs c0
   WHERE c1.cat_id = c0.catid
     AND c0.catname = icatname
     AND x1.xtrsrcid = ixtrsrcid
     AND c1.x * x1.x + c1.y * x1.y + c1.z * x1.z > COS(RADIANS(itheta))
     AND c1.zone BETWEEN CAST(FLOOR((x1.decl - itheta) / izoneheight) AS INTEGER)
                     AND CAST(FLOOR((x1.decl + itheta) / izoneheight) AS INTEGER)
     AND c1.ra BETWEEN x1.ra - alpha(itheta, x1.decl)
                   AND x1.ra + alpha(itheta, x1.decl)
     AND c1.decl BETWEEN x1.decl - itheta
                     AND x1.decl + itheta
     AND POWER((COS(radians(c1.decl)) * COS(radians(c1.ra))
               - COS(radians(x1.decl)) * COS(radians(x1.ra))
               ), 2)
        + POWER((COS(radians(c1.decl)) * SIN(radians(c1.ra))
                - COS(radians(x1.decl)) * SIN(radians(x1.ra))
                ), 2)
        + POWER((SIN(radians(c1.decl))
                - SIN(radians(x1.decl))
                ), 2) = (SELECT MIN(POWER((COS(radians(c1.decl)) * COS(radians(c1.ra))
                                          - COS(radians(x1.decl)) * COS(radians(x1.ra))
                                          ), 2)
                                   + POWER((COS(radians(c1.decl)) * SIN(radians(c1.ra))
                                           - COS(radians(x1.decl)) * SIN(radians(x1.ra))
                                           ), 2)
                                   + POWER((SIN(radians(c1.decl))
                                           - SIN(radians(x1.decl))
                                           ), 2)
                                   )
                           FROM extractedsources x1
                               ,catalogedsources c1
                               ,catalogs c0
                          WHERE c1.cat_id = c0.catid
                            AND c0.catname = icatname
                            AND x1.xtrsrcid = ixtrsrcid
                            AND c1.x * x1.x + c1.y * x1.y + c1.z * x1.z > COS(RADIANS(itheta))
                            AND c1.zone BETWEEN CAST(FLOOR((x1.decl - itheta) / izoneheight) AS INTEGER)
                                            AND CAST(FLOOR((x1.decl + itheta) / izoneheight) AS INTEGER)
                            AND c1.ra BETWEEN x1.ra - alpha(itheta, x1.decl)
                                          AND x1.ra + alpha(itheta, x1.decl)
                            AND c1.decl BETWEEN x1.decl - itheta
                                            AND x1.decl + itheta
                        )
  ;

  RETURN icatsrcid;

END;

