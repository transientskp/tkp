DROP PROCEDURE IF EXISTS MultipleCatMatchingInit;

DELIMITER //

/*+--------------------------------------------------------------------+
 *| (1) We load the multiplecatalogsources table, with NVSS, WENSS,    |
 *|     VLSS, 8C data (decl > 30, gives a total of ~ 800,000 sources). |
 *|                                                                    |
 *| (2) Create initial list of associated sources by cursoring through |
 *|     multiplecatalogsources table, weighting the association by     |
 *|     function getWeightRectIntersection().                          |
 *| (3)                                                                |
 *|                                                                    |
 *|                                                                    |
 *|                                                                    |
 *+--------------------------------------------------------------------+
 *|                                                                    |
 *+--------------------------------------------------------------------+
 */
CREATE PROCEDURE MultipleCatMatchingInit()

BEGIN

  DECLARE icat_id INT;
  DECLARE done INT DEFAULT 0;
  DECLARE izoneheight, ira_min, ira_max, idecl_min, idecl_max DOUBLE;

  DECLARE imultcatsrcid, imultcatsrcid1, imultcatsrcid2 INT;
  DECLARE imultcatassocid INT;
  DECLARE ira, idecl, ira_err, idecl_err DOUBLE;
  DECLARE ira1, idecl1, ira1_err, idecl1_err DOUBLE;
  DECLARE ira2, idecl2, ira2_err, idecl2_err DOUBLE;
  DECLARE inew_ra, inew_decl, inew_ra_err, inew_decl_err DOUBLE;
  DECLARE inew_zone INT;
  DECLARE isrc1_id, isrc2_id, inew_src_id, iother_src_id INT;
  DECLARE iweight DOUBLE;

  SELECT zoneheight
    INTO izoneheight
    FROM zoneheight;

  SET ira_min = 40;
  SET ira_max = 42;
  SET idecl_min = 69;
  SET idecl_max = 71;
  SET icat_id = 3;
  WHILE (icat_id <= 6) DO
    INSERT INTO multiplecatalogsources
      (zone
      ,ra
      ,decl
      ,ra_err
      ,decl_err
      ,cat_id
      ,orig_catsrcid
      ,active
      )
      SELECT FLOOR(decl / izoneheight)
            ,ra
            ,decl
            ,ra_err
            ,decl_err
            ,icat_id
            ,orig_catsrcid
            ,TRUE
        FROM catalogedsources
       WHERE cat_id = icat_id
         AND zone >= 30
         AND ra BETWEEN ira_min AND ira_max
         AND decl BETWEEN idecl_min AND idecl_max
      GROUP BY orig_catsrcid
    ;
    SET icat_id = icat_id + 1;
  END WHILE;
  
  /* here we intially fill the multiplecatalogassocs table */
  /* NOTE: for some reason it does not work when we put the 
   * getWeight function in the where clause directly. In that case
   * only the last assoc is return instead of all. --> Bug ?
   */
  /*INSERT INTO multiplecatalogassocs
    (src1_id
    ,src2_id
    ,weight
    ,distance
    ,active
    )
    SELECT src1_id
          ,src2_id
          ,weight
          ,distance
          ,active 
      FROM (SELECT s1.multcatsrcid AS src1_id
                  ,s2.multcatsrcid AS src2_id
                  ,getWeightRectIntersection(s1.ra,s1.decl,s1.ra_err,s1.decl_err,s2.ra,s2.decl,s2.ra_err,s2.decl_err) AS weight
                  ,getDistance_arcsec(s1.ra,s1.decl,s2.ra,s2.decl) AS distance
                  ,TRUE AS active 
              FROM multiplecatalogsources s1
                  ,multiplecatalogsources s2 
             WHERE s1.multcatsrcid < s2.multcatsrcid 
               AND s1.cat_id < s2.cat_id 
           ) AS t 
     WHERE t.weight > 0 
    ORDER BY weight DESC
            ,distance
  ;
*/
END;
//

DELIMITER ;
