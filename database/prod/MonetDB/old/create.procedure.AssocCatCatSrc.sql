USE pipeline_test;

DROP PROCEDURE IF EXISTS AssocCatCatSrc;

DELIMITER //

CREATE PROCEDURE AssocCatCatSrc(IN icatsrcid INT
                               ,IN icat_id INT
                               ,IN ira DOUBLE
                               ,IN idecl DOUBLE
                               ,IN ira_err DOUBLE
                               ,IN idecl_err DOUBLE
                               )
BEGIN

  DECLARE izoneheight DOUBLE DEFAULT 1;
  DECLARE itheta DOUBLE;
  DECLARE ialpha DOUBLE;
  DECLARE cat_forth INT DEFAULT 1;
  DECLARE cat_ref INT DEFAULT 1;

  DECLARE iassoc_catsrcid INT DEFAULT NULL;
  DECLARE nassoc_catsrcid INT DEFAULT 0;

  DECLARE found BOOLEAN DEFAULT FALSE;
  DECLARE sigma INT DEFAULT 1;

  SELECT GREATEST(ira_err, idecl_err) INTO itheta;
  SET ialpha = alpha(itheta, idecl);

  SELECT GREATEST(ira_err, idecl_err) INTO itheta;
  SET cat_forth = 1;
  WHILE (cat_ref < 4) DO
    SET cat_ref = icat_id + cat_forth;
    SET found = FALSE;
    SET sigma = 1;
    SET iassoc_catsrcid = NULL;
    WHILE (found = FALSE AND sigma < 4) DO
      SELECT COUNT(*)
        INTO nassoc_catsrcid
        FROM cataloguedsources
       WHERE cat_id = cat_ref
         AND zone BETWEEN FLOOR((idecl - itheta)/izoneheight) 
                      AND FLOOR((idecl + itheta)/izoneheight)
         AND ra BETWEEN ira - ialpha 
                    AND ira + ialpha
         AND decl BETWEEN idecl - itheta 
                      AND idecl + itheta
         AND doIntersectElls(@ra,@decl,@ra_err,@decl_err
                            ,ra,decl,ra_err,decl_err)
      ;
      /* TODO: We might find more than one association */
      IF nassoc_catsrcid > 0 THEN
        SELECT catsrcid
          INTO iassoc_catsrcid
          FROM cataloguedsources
         WHERE cat_id = cat_ref
           AND zone BETWEEN FLOOR((idecl - itheta)/izoneheight) 
                        AND FLOOR((idecl + itheta)/izoneheight)
           AND ra BETWEEN ira - ialpha 
                      AND ira + ialpha
           AND decl BETWEEN idecl - itheta 
                        AND idecl + itheta
           AND doIntersectElls(@ra,@decl,@ra_err,@decl_err
                              ,ra,decl,ra_err,decl_err)
        ;
        SET found = TRUE;
      ELSE
        SET sigma = sigma + 1;
        SET itheta = sigma * itheta / (sigma - 1);
        SET ialpha = alpha(itheta, idecl);
      END IF;
    END WHILE;
    /* Insert and continue searching other catalogues*/
    INSERT INTO associatedcatsources
      (catsrc_id
      ,assoc_catsrcid
      )
    VALUES
      (icatsrcid
      ,iassoc_catsrcid
      )
    ;
    SET cat_forth = cat_forth + 1;
  END WHILE;


END;
//

DELIMITER ;

