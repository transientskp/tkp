DROP FUNCTION IF EXISTS getNearestNeighborInCat;

DELIMITER //

/*
 *
 */
CREATE FUNCTION getNearestNeighborInCat(icatname VARCHAR(50)
                                       ,itheta DOUBLE
                                       ,ixtrsrcid INT
                                       ) RETURNS INT
DETERMINISTIC
BEGIN
  
  DECLARE icatsrcid INT DEFAULT NULL;
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
     AND c1.zone BETWEEN FLOOR((x1.decl - itheta) / izoneheight)
                        AND FLOOR((x1.decl + itheta) / izoneheight)
     AND c1.ra BETWEEN x1.ra - alpha(itheta, x1.decl)
                   AND x1.ra + alpha(itheta, x1.decl)
     AND c1.decl BETWEEN x1.decl - itheta
                     AND x1.decl + itheta
     AND getDistanceArcsec(x1.ra, x1.decl, c1.ra, c1.decl) = (SELECT MIN(getDistanceArcsec(x1.ra, x1.decl, c1.ra, c1.decl))
                                                                FROM extractedsources x1
                                                                    ,catalogedsources c1
                                                                    ,catalogs c0
                                                               WHERE c1.cat_id = c0.catid
                                                                 AND c0.catname = icatname
                                                                 AND x1.xtrsrcid = ixtrsrcid
                                                                 AND c1.x * x1.x + c1.y * x1.y + c1.z * x1.z > COS(RADIANS(itheta))
                                                                 AND c1.zone BETWEEN FLOOR((x1.decl - itheta) / izoneheight)
                                                                                 AND FLOOR((x1.decl + itheta) / izoneheight)
                                                                 AND c1.ra BETWEEN x1.ra - alpha(itheta, x1.decl)
                                                                               AND x1.ra + alpha(itheta, x1.decl)
                                                                 AND c1.decl BETWEEN x1.decl - itheta
                                                                                 AND x1.decl + itheta
                                                             )
  ;

  RETURN icatsrcid;

END;
//

DELIMITER ;
