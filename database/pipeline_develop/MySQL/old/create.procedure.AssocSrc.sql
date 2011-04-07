DROP PROCEDURE IF EXISTS AssocSrc;

DELIMITER //

/*+------------------------------------------------------------------+
 *| This procedure                                                   |
 *| (1) adds an extracted source to the extractedsources table.      |
 *| (2) tries to associate the source with sources previously        |
 *|     detected for this data set (same ds_id)                      |
 *| (3) also tries to associate the source with cataloged sources    |
 *| (4) If found, an association will be added to the                |
 *|     associatedsources table.                                     |
 *+------------------------------------------------------------------+
 *| Input params:                                                    |
 *|   iimage_id  : the image_id from which this source was extracted |
 *|   ira        : RA of extracted source (in degrees)               |
 *|   idecl      : dec of extracted source (in degrees)              |
 *|   ira_err    : 1 sigma error on RA (in degrees)                  |
 *|   idecl_err  : 1 sigma error on dec (in degrees)                 |
 *|   iI_peak    : Peak flux of extracted source (in Jansky)         |
 *|   iI_peak_err: Error on peak flux of extracted source (in Jansky)|
 *|   iI_int     : Integrated flux of extracted source (in Jansky)   |
 *|   iI_int_err : Error on int. flux of extracted source (in Jansky)|
 *|   idet_sigma : The detection level of the extracted source       |
 *|                (in sigma)                                        |
 *+------------------------------------------------------------------+
 *| Used variables:                                                  |
 *| itheta: this is the radius (in degrees) of the circular area     |
 *|         centered at (ra,decl) of the current (input) source. All |
 *|         sources found within this area will be inspected for     |
 *|         association.                                             |
 *|         The difficult part is how to determine what is the best  |
 *|         value for itheta. Will it depend on the source density,  |
 *|         which depends on int.time, freq, or is it sufficient to  |
 *|         simply set it to a default value of f.ex. 1 (degree)?    |
 *|         For now, we default it to 1 (degree).                    |
 *|                                                                  |
 *+------------------------------------------------------------------+
 *| TODO: Also insert margin records                                 |
 *+------------------------------------------------------------------+
 *|                       Bart Scheers                               |
 *|                        2009-02-18                                |
 *+------------------------------------------------------------------+
 *| 2009-02-18                                                       |
 *| Based on AssociateSource() from create.database.sql              |
 *+------------------------------------------------------------------+
 *| Open Questions:                                                  |
 *|                                                                  |
 *+------------------------------------------------------------------+
 */
CREATE PROCEDURE AssocSrc(IN iimage_id INT
                         ,IN ira DOUBLE
                         ,IN idecl DOUBLE
                         ,IN ira_err DOUBLE
                         ,IN idecl_err DOUBLE
                         ,IN iI_peak DOUBLE
                         ,IN iI_peak_err DOUBLE
                         ,IN iI_int DOUBLE
                         ,IN iI_int_err DOUBLE
                         ,IN idet_sigma DOUBLE
                         )
BEGIN

  DECLARE izone INT;
  DECLARE ix DOUBLE;
  DECLARE iy DOUBLE;
  DECLARE iz DOUBLE;
  DECLARE ixy DOUBLE;

  DECLARE izoneheight DOUBLE;
  DECLARE itheta DOUBLE;
  DECLARE sin_itheta DOUBLE;
  DECLARE ialpha DOUBLE;

  DECLARE ixtrsrcid INT;
  DECLARE nassoc_xtrsrcid INT;
  DECLARE nassoc_catsrcid INT;

  DECLARE iinsert_src1 BOOLEAN;
  DECLARE iinsert_src2 BOOLEAN;

  DECLARE found BOOLEAN;

  SELECT zoneheight
    INTO izoneheight
    FROM zoneheight
  ;

  SET itheta = 1;
  SET izone = FLOOR(idecl/izoneheight);
  SET ixy = COS(RADIANS(idecl));
  SET ix = ixy * COS(RADIANS(ira));
  SET iy = ixy * SIN(RADIANS(ira));
  SET iz = SIN(RADIANS(idecl));

  INSERT INTO extractedsources
    (image_id
    ,zone
    ,ra
    ,decl
    ,ra_err
    ,decl_err
    ,x
    ,y
    ,z
    ,det_sigma
    ,I_peak
    ,I_peak_err
    ,I_int
    ,I_int_err
    ) 
  VALUES
    (iimage_id
    ,izone
    ,ira
    ,idecl
    ,ira_err
    ,idecl_err
    ,ix
    ,iy
    ,iz
    ,idet_sigma
    ,iI_peak
    ,iI_peak_err
    ,iI_int
    ,iI_int_err
    )
  ;
 
  SET ixtrsrcid = LAST_INSERT_ID();

  /* We use the default value, instead of
   * SELECT GREATEST(ira_err, idecl_err) INTO itheta;
   */
  SET ialpha = alpha(itheta, idecl);
  SET sin_itheta = SIN(RADIANS(itheta));

  /* Here we create a temporary in-memory table that contains
   * all the ids of associated sources
   */
  DELETE FROM assocxtrsrcids;

  /* Here we insert the associated ids into the temporary table. 
   * The SELECT query selects all the extractedsources in all the 
   * images that belong to the same dataset as to which the 
   * current image belongs to.
   */
  INSERT INTO assocxtrsrcids
    SELECT xtrsrcid AS assocxtrsrcid
           /*
           ,DEGREES(2 * ASIN(SQRT(POW(x - @x, 2) + 
                                  POW(y - @y, 2) + 
                                  POW(z - @z, 2)) / 2)) AS distance
           */
      FROM extractedsources
          ,images
     WHERE imageid = image_id
       AND ds_id = (SELECT ds_id 
                      FROM images 
                     WHERE imageid = iimage_id
                   )
       AND image_id < iimage_id
       AND zone BETWEEN FLOOR((idecl - itheta) / izoneheight)
                    AND FLOOR((idecl + itheta) / izoneheight)
       AND ra BETWEEN ira - ialpha
                  AND ira + ialpha
       AND decl BETWEEN idecl - itheta
                    AND idecl + itheta
       /*
       AND 4 * POW(SIN(RADIANS(itheta / 2)), 2) > 
           POW(x - ix, 2) + POW(y - iy, 2) + POW(z - iz, 2)
       */
       AND sin_itheta > SIN(2 * ASIN(SQRT(POW(x - ix, 2) + 
                                          POW(y - iy, 2) + 
                                          POW(z - iz, 2)) / 2))
       AND doIntersectElls(ira,idecl,ira_err,idecl_err
                          ,ra,decl,ra_err,decl_err)
  ;

  /* Here we select the previous associations of the associated sources 
   * of the current source.
   * It is necessary to do, because we want prevent the associations 
   * from wandering away. Therefore we further have to check if these 
   * can also be associated to the current source.
   */
  SELECT COUNT(*) 
    INTO nassoc_xtrsrcid
    FROM assocxtrsrcids
  ;

  IF nassoc_xtrsrcid > 0 THEN
    SET iinsert_src1 = FALSE;
    /* TODO:
     * It would be better if row_number() worked here
     */
    SET @cnt = 0;
    INSERT INTO associatedsources
      (xtrsrc_id
      ,insert_src1
      ,src_type
      ,assoc_xtrsrcid
      ,insert_src2
      )
      SELECT xtrsrc_id
            ,iinsert_src1
            ,'X'
            ,ixtrsrcid
            ,CASE WHEN (@cnt := @cnt + 1) = 1 
                  THEN TRUE
                  ELSE FALSE
             END
        FROM associatedsources
            ,assocxtrsrcids
            ,extractedsources 
       WHERE xtrsrc_id = xtrsrcid 
         AND assocxtrsrcid = assoc_xtrsrcid 
         AND zone BETWEEN FLOOR((idecl - itheta) / izoneheight)
                      AND FLOOR((idecl + itheta) / izoneheight)
         AND ra BETWEEN ira - ialpha
                    AND ira + ialpha
         AND decl BETWEEN idecl - itheta
                      AND idecl + itheta
         /*
         AND 4 * POW(SIN(RADIANS(itheta / 2)), 2) > 
                 POW(x - ix, 2) + POW(y - iy, 2) + POW(z - iz, 2)
         */
         AND sin_itheta > SIN(2 * ASIN(SQRT(POW(x - ix, 2) + 
                                            POW(y - iy, 2) + 
                                            POW(z - iz, 2)) / 2))
         AND doIntersectElls(ira,idecl,ira_err,idecl_err
                            ,ra,decl,ra_err,decl_err)
      GROUP BY xtrsrc_id
    ;
  ELSE
    SET iinsert_src1 = TRUE;
    SET iinsert_src2 = FALSE;
    INSERT INTO associatedsources
      (xtrsrc_id
      ,insert_src1
      ,src_type
      ,assoc_xtrsrcid
      ,insert_src2
      )
    VALUES 
      (ixtrsrcid
      ,iinsert_src1
      ,'X'
      ,ixtrsrcid
      ,iinsert_src2
      )
    ;
  END IF;

  DELETE FROM assocxtrsrcids;
  
  /*+----------------------------------------------------------------+
   *|               Associate with cataloged sources                 |
   *+----------------------------------------------------------------+

  /* Here we create a temporary in-memory table that contains
   * all the ids of associated sources
   */
  DELETE FROM assoccatsrcids;

  /* Here we insert the associated ids into the temporary table. 
   * The SELECT query selects all the extractedsources in all the 
   * images that belong to the same dataset as to which the 
   * current image belongs to.
   */
  INSERT INTO assoccatsrcids
    SELECT catsrcid AS assoccatsrcid
      FROM catalogedsources
     WHERE zone BETWEEN FLOOR((idecl - itheta)/izoneheight)
                    AND FLOOR((idecl + itheta)/izoneheight)
       AND ra BETWEEN ira - ialpha
                  AND ira + ialpha
       AND decl BETWEEN idecl - itheta
                    AND idecl + itheta
       AND 4 * POW(sin_itheta, 2) > 
           POW(x - ix, 2) + POW(y - iy, 2) + POW(z - iz, 2)
       AND doIntersectElls(ira,idecl,ira_err,idecl_err
                          ,ra,decl,ra_err,decl_err)
  ;

  /* Here we select the previous associations of the associated sources 
   * of the current source.
   * It is necessary to do, because we want prevent the associations 
   * from wandering away. Therefore we further have to check if these 
   * can also be associated to the current source.
   */
  SELECT COUNT(*) 
    INTO nassoc_catsrcid
    FROM assoccatsrcids
  ;

  IF nassoc_catsrcid > 0 THEN
    INSERT INTO associatedsources
      (xtrsrc_id
      ,src_type
      ,assoc_catsrcid
      )
      SELECT ixtrsrcid
            ,'C'
            ,assoccatsrcid
        FROM assoccatsrcids
    ;
  ELSE 
    INSERT INTO associatedsources
      (xtrsrc_id
      ,src_type
      )
    VALUES 
      (ixtrsrcid
      ,'C'
      )
    ;
  END IF;

  DELETE FROM assoccatsrcids;

END;
//

DELIMITER ;

