DROP PROCEDURE IF EXISTS AssocCatSrcs;

DELIMITER //

CREATE PROCEDURE AssocCatSrcs()
BEGIN

  DECLARE izoneheight DOUBLE;
  DECLARE itheta DOUBLE DEFAULT 1;
  DECLARE sin_itheta DOUBLE;

  DECLARE icat_id INT;
  DECLARE cat_ref INT;

  SELECT zoneheight 
    INTO izoneheight
    FROM zoneheight
  ;
  SET sin_itheta = SIN(RADIANS(itheta));

  SET icat_id = 3;
  WHILE (icat_id < 4) DO
    SET cat_ref = 6;
    /*SET cat_ref = icat_id + 1;
    WHILE (cat_ref < 6) DO*/
      INSERT INTO associatedcatsources
        (catsrc_id
        ,assoc_catsrcid
        )
        SELECT c1.catsrcid
              ,c2.catsrcid
          FROM catalogedsources c1
              ,catalogedsources c2
         WHERE c1.cat_id = icat_id
           AND c2.cat_id > icat_id
           AND c2.zone BETWEEN FLOOR((c1.decl - itheta) / izoneheight)
                           AND FLOOR((c1.decl + itheta) / izoneheight)
           AND c2.ra BETWEEN c1.ra - alpha(itheta, c1.decl)
                         AND c1.ra + alpha(itheta, c1.decl)
           AND c2.decl BETWEEN c1.decl - itheta
                           AND c1.decl + itheta
           AND sin_itheta > SIN(2 * ASIN(SQRT(POW(c2.x - c1.x, 2) +
                                              POW(c2.y - c1.y, 2) +
                                              POW(c2.z - c1.z, 2)
                                             ) / 2))
           AND doIntersectElls(c1.ra,c1.decl,c1.ra_err,c1.decl_err
                              ,c2.ra,c2.decl,c2.ra_err,c2.decl_err)
      ;
      /*SET cat_ref = cat_ref + 1;
    END WHILE;*/
    SET icat_id = icat_id + 1;
  END WHILE;

END;
//

DELIMITER ;

