DROP PROCEDURE IF EXISTS AssocXSourceByImageLT3;

DELIMITER //

/*+------------------------------------------------------------------+
 *| This procedure tries to associate extractedsources in an image   |
 *| (image_id = iimage_id) to previous extractedsources (these are   |
 *| already in the associatedsources.                                |
 *| Sources that could not be associated will be inserted in the     |
 *| associatedsources table as well.                                 |
 *|                                                                  |
 *+------------------------------------------------------------------+
 *| Query is as follows:                                             |
 *| select == assocs ==                                              |
 *| union                                                            |
 *| select == no assocs for sources in current image ==              |
 *| union                                                            |
 *| select == no assocs in case of empty table ==                    |
 *| ;                                                                |
 *|                                                                  |
 *| Select 1:                                                        |
 *| sources with assocs                                              |
 *| Select 2:                                                        |
 *| Query to select new sources in current image i.e. no associations| 
 *| could be found in associatedsources (or: all sources from        |
 *| image_id = iimageid that do NOT intersect with sources from      |
 *| images with the same ds_id as iimageid).                         |
 *| Select 3:                                                        |
 *| Select the sources that could not be associated, because the     |
 *| associatedsources table is empty.                                |
 *|                                                                  |
 *+------------------------------------------------------------------+
 *|                         Bart Scheers                             |
 *|                          2009-10-28                              |
 *|                  University of Amsterdam                         |
 *|                      LOFAR TKP Project                           |
 *+------------------------------------------------------------------+
 *| TODO:                                                            |
 *+------------------------------------------------------------------+
 *| Open questions:                                                  |
 *+------------------------------------------------------------------+
 */
CREATE PROCEDURE AssocXSourceByImageLT3(IN iimageid INT)

BEGIN

  DECLARE izoneheight, itheta DOUBLE;
  
  SELECT zoneheight 
    INTO izoneheight
    FROM zoneheight
  ;
  SET itheta = 1;

  INSERT INTO associatedsources
    (xtrsrc_id
    ,insert_src1
    ,assoc_type
    ,assoc_xtrsrc_id
    ,insert_src2
    ,assoc_weight
    ,assoc_distance_arcsec
    )
    SELECT t.xtrsrc_id
          ,t.insert_src1
          ,t.assoc_type
          ,t.assoc_xtrsrc_id
          ,t.insert_src2
          ,t.assoc_weight
          ,t.assoc_distance_arcsec
      FROM (SELECT x2.xtrsrcid AS xtrsrc_id
                  ,FALSE AS insert_src1
                  ,'X' AS assoc_type
                  ,x1.xtrsrcid AS assoc_xtrsrc_id
                  ,NULL AS insert_src2
                  ,getWeightRectIntersection(x1.ra,x1.decl,x1.ra_err,x1.decl_err
                                            ,x2.ra,x2.decl,x2.ra_err,x2.decl_err
                                            ) AS assoc_weight
                  ,3600 * degrees(2 * ASIN(SQRT(POWER((COS(radians(x2.decl)) * COS(radians(x2.ra))
                                                      - COS(radians(x1.decl)) * COS(radians(x1.ra))
                                                      ), 2)
                                               + POWER((COS(radians(x2.decl)) * SIN(radians(x2.ra))
                                                       - COS(radians(x1.decl)) * SIN(radians(x1.ra))
                                                       ), 2)
                                               + POWER((SIN(radians(x2.decl))
                                                       - SIN(radians(x1.decl))
                                                       ), 2)
                                               ) / 2)) AS assoc_distance_arcsec
              FROM extractedsources x1
                  ,images im1
                  ,associatedsources a1
                  ,extractedsources x2
                  ,images im2
             WHERE x1.image_id = iimageid
               AND x1.image_id = im1.imageid
               AND im1.ds_id = (SELECT im11.ds_id
                                  FROM images im11
                                 WHERE im11.imageid = iimageid
                               )
               AND a1.xtrsrc_id = x2.xtrsrcid
               AND x2.image_id = im2.imageid
               AND im1.ds_id = im2.ds_id
               AND x2.zone BETWEEN FLOOR((x1.decl - itheta) / izoneheight)                    
                               AND FLOOR((x1.decl + itheta) / izoneheight)
               AND x2.ra BETWEEN (x1.ra - alpha(itheta,x1.decl))                  
                             AND (x1.ra + alpha(itheta,x1.decl))    
               AND x2.decl BETWEEN x1.decl - itheta
                               AND x1.decl + itheta 
               AND doSourcesIntersect(x1.ra,x1.decl,x1.ra_err,x1.decl_err
                                     ,x2.ra,x2.decl,x2.ra_err,x2.decl_err)
            UNION ALL 
            SELECT x1.xtrsrcid AS xtrsrc_id
                  ,TRUE AS insert_src1
                  ,'X' AS assoc_type
                  ,x1.xtrsrcid AS assoc_xtrsrc_id
                  ,FALSE AS insert_src2
                  ,2 AS assoc_weight
                  ,0 AS assoc_distance_arcsec
              FROM extractedsources x1
                  ,associatedsources a1
                  ,extractedsources x2
                  ,images im2 
             WHERE x1.image_id = iimageid 
               AND a1.xtrsrc_id = x2.xtrsrcid 
               AND x2.image_id = im2.imageid 
               AND im2.ds_id = (SELECT ds_id 
                                  FROM images im3 
                                 WHERE imageid = iimageid
                               ) 
               AND NOT doSourcesIntersect(x1.ra,x1.decl,x1.ra_err,x1.decl_err
                                         ,x2.ra,x2.decl,x2.ra_err,x2.decl_err)
               AND x1.xtrsrcid NOT IN (SELECT x3.xtrsrcid       
                                         FROM extractedsources x3       
                                             ,images im4       
                                             ,associatedsources a2       
                                             ,extractedsources x4       
                                             ,images im5  
                                        WHERE x3.image_id = iimageid    
                                          AND x3.image_id = im4.imageid    
                                          AND im4.ds_id = (SELECT im6.ds_id                       
                                                             FROM images im6                      
                                                            WHERE im6.imageid = iimageid                    
                                                          )    
                                          AND a2.xtrsrc_id = x4.xtrsrcid    
                                          AND x4.image_id = im5.imageid    
                                          AND im5.ds_id = im4.ds_id    
                                          AND x4.zone BETWEEN FLOOR((x3.decl - itheta) / izoneheight)
                                                          AND FLOOR((x3.decl + itheta) / izoneheight)
                                          AND x4.ra BETWEEN (x3.ra - alpha(itheta,x3.decl))
                                                        AND (x3.ra + alpha(itheta,x3.decl))    
                                          AND x4.decl BETWEEN x3.decl - itheta
                                                          AND x3.decl + itheta 
                                          AND doSourcesIntersect(x3.ra,x3.decl,x3.ra_err,x3.decl_err
                                                                ,x4.ra,x4.decl,x4.ra_err,x4.decl_err)
                                      )
            GROUP BY x1.xtrsrcid
            UNION ALL
            SELECT x1.xtrsrcid AS xtrsrc_id
                  ,TRUE AS insert_src1
                  ,'X' AS assoc_type
                  ,x1.xtrsrcid AS assoc_xtrsrc_id
                  ,FALSE AS insert_src2
                  ,3 AS assoc_weight
                  ,0 AS assoc_distance_arcsec
              FROM extractedsources x1
             WHERE NOT EXISTS (SELECT a2.xtrsrc_id
                                 FROM associatedsources a2
                                     ,extractedsources x2
                                     ,images im2
                                WHERE x2.xtrsrcid = a2.xtrsrc_id
                                  AND x2.image_id = im2.imageid
                                  AND im2.ds_id = (SELECT im10.ds_id
                                                     FROM images im10
                                                    WHERE imageid = iimageid
                                                  )
                              )
               AND x1.image_id = iimageid
           ) t
  ;

END;
//

DELIMITER ;

