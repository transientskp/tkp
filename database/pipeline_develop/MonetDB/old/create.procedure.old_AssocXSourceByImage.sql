--DROP PROCEDURE AssocXSourceByImage;

/*+------------------------------------------------------------------+
 *+------------------------------------------------------------------+
 *+------------------------------------------------------------------+
 *|                                                                  |
 *+------------------------------------------------------------------+
 *+------------------------------------------------------------------+
 *+------------------------------------------------------------------+
 *+------------------------------------------------------------------+
 *|                                                                  |
 *+------------------------------------------------------------------+
 */
CREATE PROCEDURE AssocXSourceByImage(iimageid INT)

BEGIN

  INSERT INTO associatedsources 
    (xtrsrc_id
    ,assoc_type
    ,assoc_xtrsrc_id
    ,assoc_weight
    ,assoc_distance_arcsec
    ) 
    SELECT x1.xtrsrcid AS xtrsrc_id
          ,'X' AS assoc_type
          ,x2.xtrsrcid AS assoc_xtrsrc_id
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
          ,images
          ,datasets
          ,extractedsources x2 
     WHERE x1.image_id = imageid 
       AND ds_id = dsid 
       AND dsid = (SELECT ds_id 
                     FROM images 
                    WHERE imageid = iimageid
                  ) 
       AND x1.image_id <> iimageid
       AND x2.image_id = iimageid
       AND dosourcesintersect(x1.ra,x1.decl,x1.ra_err,x1.decl_err
                             ,x2.ra,x2.decl,x2.ra_err,x2.decl_err)
    ORDER BY assoc_weight DESC
            ,assoc_distance_arcsec
  ;

END;

