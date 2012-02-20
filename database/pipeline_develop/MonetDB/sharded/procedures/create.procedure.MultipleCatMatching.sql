--DROP PROCEDURE MultipleCatMatching;

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
CREATE PROCEDURE MultipleCatMatching()

BEGIN

  DECLARE icat_id INT;
  DECLARE izoneheight, ira_min, ira_max, idecl_min, idecl_max DOUBLE;

  DECLARE imultcatsrcid, imultcatsrcid1, imultcatsrcid2 INT;
  DECLARE imultcatassocid INT;
  DECLARE active_srcs INT;
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

  /* create new source */
  
  /* first, we select the maximum weight that has 
   * been given to the associations, and then we
   * select the minimum multcatassocid for these (in the
   * cases we have more than one assoc of the same max weight.)
   */
  /*SELECT MIN(multcatassocid)
    INTO imultcatassocid
    FROM multiplecatalogassocs
   WHERE weight = (SELECT MAX(weight)
                     FROM multiplecatalogassocs
                    WHERE active IS TRUE
                  )
  ;
  */

  /* LOOP1: BEGIN -------- */
  SELECT COUNT(*)
    INTO active_srcs
    FROM multiplecatalogassocs
   WHERE active = 1
     AND weight >= 0
  ;

  WHILE (active_srcs > 0) DO
    SELECT multcatassocid
      INTO imultcatassocid
      FROM multiplecatalogassocs
     WHERE active = 1
       AND weight >= 0
    /*ORDER BY weight DESC
            ,distance*/
    LIMIT 1
    ;
    
    /* we select the two sources with the max weight */
    SELECT a.src1_id
          ,s1.ra
          ,s1.decl
          ,s1.ra_err
          ,s1.decl_err
          ,a.src2_id
          ,s2.ra
          ,s2.decl
          ,s2.ra_err
          ,s2.decl_err
      INTO isrc1_id
          ,ira1
          ,idecl1
          ,ira1_err
          ,idecl1_err
          ,isrc2_id
          ,ira2
          ,idecl2
          ,ira2_err
          ,idecl2_err
      FROM multiplecatalogassocs a
          ,multiplecatalogsources s1
          ,multiplecatalogsources s2
     WHERE multcatassocid = imultcatassocid
       AND a.src1_id = s1.multcatsrcid
       AND a.src2_id = s2.multcatsrcid
    ;

    /* from these two we create an weighted average source,
     * and insert it as a new one into the multiplecatalogsources table
     */
    SELECT SUM(ra / POWER(ra_err, 2)) / SUM(1 / POWER(ra_err, 2))
          ,SUM(decl/ POWER(decl_err, 2)) / SUM(1 / POWER(decl_err, 2))
          ,SQRT(1 / SUM(1 / POWER(ra_err, 2)))
          ,SQRT(1 / SUM(1 / POWER(decl_err, 2)))
      INTO inew_ra
          ,inew_decl
          ,inew_ra_err
          ,inew_decl_err
      FROM multiplecatalogsources
     WHERE multcatsrcid = isrc1_id
        OR multcatsrcid = isrc2_id
    ;
    
    SET inew_zone = CAST(FLOOR(inew_decl / izoneheight) AS INTEGER);

    SELECT NEXT VALUE FOR seq_multiplecatalogsources INTO inew_src_id;

    INSERT INTO multiplecatalogsources
      (multcatsrcid
      ,zone
      ,ra
      ,decl
      ,ra_err
      ,decl_err
      ,orig_src1_id
      ,orig_src2_id
      ,active
      )
    VALUES
      (inew_src_id
      ,inew_zone
      ,inew_ra
      ,inew_decl
      ,inew_ra_err
      ,inew_decl_err
      ,isrc1_id
      ,isrc2_id
      ,TRUE
      )
    ;

    /* we set the sources that were used for the average inactive */
    UPDATE multiplecatalogsources
       SET active = 0
     WHERE multcatsrcid = isrc1_id
        OR multcatsrcid = isrc2_id
    ;
    
    /* we set the last used association to inactive */
    UPDATE multiplecatalogassocs
       SET active = FALSE
     WHERE multcatassocid = imultcatassocid
    ;
    
    /* we update sources with the same id to the new source id,
     * that was just added to multiplecatalogsources table,
     * and calculate the weight with the new source again.
     */
    UPDATE multiplecatalogassocs a
          ,multiplecatalogsources s
       SET a.src1_id = inew_src_id
          ,a.weight = getWeightRectIntersection(inew_ra, inew_decl, inew_ra_err, inew_decl_err
                                               ,ra, decl, ra_err, decl_err)
          ,a.distance = getDistance_arcsec(inew_ra, inew_decl, ra, decl)
          ,a.active = IF(getWeightRectIntersection(inew_ra, inew_decl, inew_ra_err, inew_decl_err
                                                  ,ra, decl, ra_err, decl_err) < 0
                        ,0
                        ,1)
     WHERE (a.src1_id = isrc1_id
            AND a.active = 1
            AND a.src2_id = s.multcatsrcid
           )
        OR (a.src1_id = isrc2_id
            AND a.active = 1
            AND a.src2_id = s.multcatsrcid
           )
    ;


    UPDATE multiplecatalogassocs a
          ,multiplecatalogsources s
       SET a.src2_id = inew_src_id
          ,a.weight = getWeightRectIntersection(ra, decl, ra_err, decl_err
                                               ,inew_ra, inew_decl, inew_ra_err, inew_decl_err)
          ,a.distance = getDistance_arcsec(ra, decl, inew_ra, inew_decl)
          ,a.active = IF(getWeightRectIntersection(ra, decl, ra_err, decl_err
                                                  ,inew_ra, inew_decl, inew_ra_err, inew_decl_err) < 0
                        ,0
                        ,1)
     WHERE (a.src2_id = isrc1_id
            AND a.active = 1
            AND a.src1_id = s.multcatsrcid
           )
        OR (a.src2_id = isrc2_id
            AND a.active = 1
            AND a.src1_id = s.multcatsrcid
           )

    ;
    
    /* TODO: Sanity check to see if multiplecatalogassocs contains  
     * rows with the same src1_id and src2_id 
     */
    UPDATE multiplecatalogassocs
       SET active = 0
     WHERE multcatassocid IN (SELECT t.multcatassocid
                                FROM (SELECT a2.multcatassocid
                                        FROM multiplecatalogassocs a1
                                            ,multiplecatalogassocs a2 
                                       WHERE a1.src1_id = a2.src2_id 
                                         AND a1.src1_id = inew_src_id
                                     ) t
                             )
    ;
    
    UPDATE multiplecatalogassocs
       SET active = 0
     WHERE multcatassocid IN (SELECT t.multcatassocid
                                FROM (SELECT multcatassocid
                                        FROM multiplecatalogassocs 
                                       WHERE src1_id = inew_src_id
                                      GROUP BY src2_id
                                      HAVING COUNT(*) > 1
                                     ) t
                             )
    ;

    SELECT COUNT(*)
      INTO active_srcs
      FROM multiplecatalogassocs
     WHERE active = 1
       AND weight >= 0
    ;

  END WHILE;
  /* LOOP1: END -------- */

  
END;
