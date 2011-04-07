DROP PROCEDURE IF EXISTS AssocXSourceByImage;

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
CREATE PROCEDURE AssocXSourceByImage(IN iimageid INT)

BEGIN

  DECLARE izoneheight, itheta DOUBLE;
  
  SELECT zoneheight 
    INTO izoneheight
    FROM zoneheight
  ;
  SET itheta = 1;

  INSERT INTO associatedsources
    (xtrsrc_id
    ,assoc_type
    ,assoc_xtrsrc_id
    ,assoc_catsrc_id
    ,assoc_weight
    ,assoc_distance_arcsec
    )
    SELECT t.xtrsrc_id
          ,t.assoc_type
          ,CASE WHEN t.assoc_xtrsrc_id = 0 
                THEN NULL
                ELSE t.assoc_xtrsrc_id
           END
          ,CASE WHEN t.assoc_catsrc_id = 0
                THEN NULL
                ELSE t.assoc_catsrc_id
           END
          ,t.assoc_weight
          ,t.assoc_distance_arcsec
      FROM (SELECT t1.xtrsrc_id
                  ,'X' AS assoc_type
                  ,t1.assoc_xtrsrc_id
                  ,0 AS assoc_catsrc_id
                  ,getWeightRectIntersection(xs1.ra,xs1.decl,xs1.ra_err,xs1.decl_err
                                            ,xs2.ra,xs2.decl,xs2.ra_err,xs2.decl_err
                                            ) AS assoc_weight
                  ,3600 * degrees(2 * ASIN(SQRT(POWER((COS(radians(xs2.decl)) * COS(radians(xs2.ra))
                                                      - COS(radians(xs1.decl)) * COS(radians(xs1.ra))
                                                      ), 2)
                                               + POWER((COS(radians(xs2.decl)) * SIN(radians(xs2.ra))
                                                       - COS(radians(xs1.decl)) * SIN(radians(xs1.ra))
                                                       ), 2)
                                               + POWER((SIN(radians(xs2.decl))
                                                       - SIN(radians(xs1.decl))
                                                       ), 2)
                                               ) / 2)) AS assoc_distance_arcsec
              /*FROM (SELECT IF(doSourcesIntersect(x1.ra,x1.decl,x1.ra_err,x1.decl_err
                                                ,x3.ra,x3.decl,x3.ra_err,x3.decl_err)*/
              FROM (SELECT IF(doPosErrCirclesIntersect(x1.ra,x1.decl,x1.ra_err,x1.decl_err
                                                      ,x3.ra,x3.decl,x3.ra_err,x3.decl_err)
                             ,x3.xtrsrcid, x2.xtrsrcid
                             ) AS xtrsrc_id
                          ,x1.xtrsrcid AS assoc_xtrsrc_id
                      FROM extractedsources x1
                          ,images im1
                          ,associatedsources a1
                          ,extractedsources x2
                          ,images im2
                          ,extractedsources x3
                     WHERE x1.image_id = iimageid
                       AND x1.image_id = im1.imageid
                       AND im1.ds_id = (SELECT im11.ds_id
                                          FROM images im11
                                         WHERE im11.imageid = iimageid
                                       )
                       AND a1.assoc_xtrsrc_id = x2.xtrsrcid
                       AND a1.xtrsrc_id = x3.xtrsrcid
                       AND x2.image_id = im2.imageid
                       AND im1.ds_id = im2.ds_id
                       AND x2.zone BETWEEN FLOOR((x1.decl - itheta) / izoneheight)
                                       AND FLOOR((x1.decl + itheta) / izoneheight)
                       AND x2.ra BETWEEN x1.ra - alpha(itheta,x1.decl)
                                     AND x1.ra + alpha(itheta,x1.decl)
                       AND x2.decl BETWEEN x1.decl - itheta
                                       AND x1.decl + itheta
                       /*AND doSourcesIntersect(x1.ra,x1.decl,x1.ra_err,x1.decl_err
                                             ,x2.ra,x2.decl,x2.ra_err,x2.decl_err)*/
                       AND doPosErrCirclesIntersect(x1.ra,x1.decl,x1.ra_err,x1.decl_err
                                                   ,x2.ra,x2.decl,x2.ra_err,x2.decl_err)
                       AND x3.zone BETWEEN FLOOR((x1.decl - itheta) / izoneheight)
                                       AND FLOOR((x1.decl + itheta) / izoneheight)
                       AND x3.ra BETWEEN x1.ra - alpha(itheta,x1.decl)
                                     AND x1.ra + alpha(itheta,x1.decl)
                       AND x3.decl BETWEEN x1.decl - itheta
                                       AND x1.decl + itheta
                   ) t1
                  ,extractedsources xs1
                  ,extractedsources xs2
             WHERE t1.xtrsrc_id = xs1.xtrsrcid
               AND t1.assoc_xtrsrc_id = xs2.xtrsrcid
            UNION 
            /* Here we insert the sources in the current image that could not be associated
             * to any of the extracted sources belonging to this same dataset.
             */
            SELECT x1.xtrsrcid AS xtrsrc_id
                  ,'X' AS assoc_type
                  ,x1.xtrsrcid AS assoc_xtrsrc_id
                  ,0 AS assoc_catsrc_id
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
               /*AND NOT doSourcesIntersect(x1.ra,x1.decl,x1.ra_err,x1.decl_err
                                         ,x2.ra,x2.decl,x2.ra_err,x2.decl_err)*/
               AND NOT doPosErrCirclesIntersect(x1.ra,x1.decl,x1.ra_err,x1.decl_err
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
                                          AND x4.ra BETWEEN x3.ra - alpha(itheta,x3.decl)
                                                        AND x3.ra + alpha(itheta,x3.decl)
                                          AND x4.decl BETWEEN x3.decl - itheta
                                                          AND x3.decl + itheta 
                                          /*AND doSourcesIntersect(x3.ra,x3.decl,x3.ra_err,x3.decl_err
                                                                ,x4.ra,x4.decl,x4.ra_err,x4.decl_err)*/
                                          AND doPosErrCirclesIntersect(x3.ra,x3.decl,x3.ra_err,x3.decl_err
                                                                     ,x4.ra,x4.decl,x4.ra_err,x4.decl_err)
                                      )
            GROUP BY x1.xtrsrcid
            UNION
            /* Here we insert the sources that could not be associated, because
             * the associatedsources table is empty
             */
            SELECT x1.xtrsrcid AS xtrsrc_id
                  ,'X' AS assoc_type
                  ,x1.xtrsrcid AS assoc_xtrsrc_id
                  ,0 AS assoc_catsrc_id
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
            UNION
            /* Here we select the sources that could be associated to the sources
             * in the main catalogs
             */
            SELECT x1.xtrsrcid AS xtrsrc_id
                  ,'C' AS assoc_type
                  ,0 AS assoc_xtrsrc_id
                  ,c1.catsrcid AS assoc_catsrc_id
                  ,getWeightRectIntersection(x1.ra,x1.decl,x1.ra_err,x1.decl_err
                                            ,c1.ra,c1.decl,c1.ra_err,c1.decl_err
                                            ) AS assoc_weight
                  ,3600 * degrees(2 * ASIN(SQRT(POWER((COS(radians(c1.decl)) * COS(radians(c1.ra))
                                                      - COS(radians(x1.decl)) * COS(radians(x1.ra))
                                                      ), 2)
                                               + POWER((COS(radians(c1.decl)) * SIN(radians(c1.ra))
                                                       - COS(radians(x1.decl)) * SIN(radians(x1.ra))
                                                       ), 2)
                                               + POWER((SIN(radians(c1.decl))
                                                       - SIN(radians(x1.decl))
                                                       ), 2)
                                               ) / 2)
                                 ) AS assoc_distance_arcsec   
              FROM extractedsources x1
                  ,catalogedsources c1
                  ,catalogs c
             WHERE x1.image_id = iimageid
               AND c1.cat_id = c.catid
               AND c1.zone BETWEEN FLOOR((x1.decl - itheta) / izoneheight)
                               AND FLOOR((x1.decl + itheta) / izoneheight)
               AND c1.ra BETWEEN x1.ra - alpha(itheta,x1.decl)
                             AND x1.ra + alpha(itheta,x1.decl)
               AND c1.decl BETWEEN x1.decl - itheta
                               AND x1.decl + itheta
               /*AND doSourcesIntersect(x1.ra,x1.decl,x1.ra_err,x1.decl_err
                                     ,c1.ra,c1.decl,c1.ra_err,c1.decl_err)*/
               AND doPosErrCirclesIntersect(x1.ra,x1.decl,x1.ra_err,x1.decl_err
                                          ,c1.ra,c1.decl,c1.ra_err,c1.decl_err)
           ) t
  ;

END;
//

DELIMITER ;

