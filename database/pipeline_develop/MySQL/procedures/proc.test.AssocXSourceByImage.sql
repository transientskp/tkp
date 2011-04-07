SET @imageid = 3;
SET @zoneheight = 1;
SET @theta = 1;

SELECT IF(doSourcesIntersect(x1.ra,x1.decl,x1.ra_err,x1.decl_err
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
 WHERE x1.image_id = @imageid
   AND x1.image_id = im1.imageid
   AND im1.ds_id = (SELECT im11.ds_id
                      FROM images im11
                     WHERE im11.imageid = @imageid
                   )
   AND a1.assoc_xtrsrc_id = x2.xtrsrcid
   AND a1.xtrsrc_id = x3.xtrsrcid
   AND x2.image_id = im2.imageid
   AND im1.ds_id = im2.ds_id
   AND x2.zone BETWEEN FLOOR((x1.decl - @theta) / @zoneheight)
                   AND FLOOR((x1.decl + @theta) / @zoneheight)
   AND x2.ra BETWEEN (x1.ra - alpha(@theta,x1.decl))
                 AND (x1.ra + alpha(@theta,x1.decl))
   AND x2.decl BETWEEN x1.decl - @theta
                   AND x1.decl + @theta
   AND doSourcesIntersect(x1.ra,x1.decl,x1.ra_err,x1.decl_err
                         ,x2.ra,x2.decl,x2.ra_err,x2.decl_err) 
   AND x3.zone BETWEEN FLOOR((x1.decl - @theta) / @zoneheight)
                   AND FLOOR((x1.decl + @theta) / @zoneheight) 
   AND x3.ra BETWEEN (x1.ra - alpha(@theta,x1.decl))
                 AND (x1.ra + alpha(@theta,x1.decl))
   AND x3.decl BETWEEN x1.decl - @theta
                   AND x1.decl + @theta
GROUP BY 1
        ,2
;


















    SELECT x2.xtrsrcid AS xtrsrc_id
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
     WHERE x1.image_id = @imageid
       AND x1.image_id = im1.imageid
       AND im1.ds_id = (SELECT im11.ds_id
                          FROM images im11
                         WHERE im11.imageid = @imageid
                       )
       AND a1.xtrsrc_id = x2.xtrsrcid
       AND x2.image_id = im2.imageid
       AND im1.ds_id = im2.ds_id
       AND x2.zone BETWEEN FLOOR((x1.decl - @theta) / @zoneheight)                    
                       AND FLOOR((x1.decl + @theta) / @zoneheight)    
       AND x2.ra BETWEEN (x1.ra - alpha(@theta,x1.decl))                  
                     AND (x1.ra + alpha(@theta,x1.decl))    
       AND x2.decl BETWEEN x1.decl - @theta
                       AND x1.decl + @theta 
       AND doSourcesIntersect(x1.ra,x1.decl,x1.ra_err,x1.decl_err
                             ,x2.ra,x2.decl,x2.ra_err,x2.decl_err)
;

    
    SELECT x1.xtrsrcid
          ,TRUE
          ,'X'
          ,x1.xtrsrcid
          ,FALSE
          ,NULL
          ,NULL
      FROM extractedsources x1
          ,associatedsources a1
          ,extractedsources x2
          ,images im2 
     WHERE x1.image_id = @imageid 
       AND a1.xtrsrc_id = x2.xtrsrcid 
       AND x2.image_id = im2.imageid 
       AND im2.ds_id = (SELECT ds_id 
                          FROM images im3 
                         WHERE imageid = @imageid
                       ) 
       AND NOT doSourcesIntersect(x1.ra,x1.decl,x1.ra_err,x1.decl_err
                                 ,x2.ra,x2.decl,x2.ra_err,x2.decl_err)
       AND x1.xtrsrcid NOT IN (SELECT x3.xtrsrcid       
                                 FROM extractedsources x3       
                                     ,images im4       
                                     ,associatedsources a2       
                                     ,extractedsources x4       
                                     ,images im5  
                                WHERE x3.image_id = @imageid    
                                  AND x3.image_id = im4.imageid    
                                  AND im4.ds_id = (SELECT im6.ds_id                       
                                                     FROM images im6                      
                                                    WHERE im6.imageid = @imageid                    
                                                  )    
                                  AND a2.xtrsrc_id = x4.xtrsrcid    
                                  AND x4.image_id = im5.imageid    
                                  AND im5.ds_id = im4.ds_id    
                                  AND x4.zone BETWEEN FLOOR((x3.decl - @theta) / @zoneheight) 
                                                  AND FLOOR((x3.decl + @theta) / @zoneheight)   
                                  AND x4.ra BETWEEN (x3.ra - alpha(@theta,x3.decl))
                                                AND (x3.ra + alpha(@theta,x3.decl))    
                                  AND x4.decl BETWEEN x3.decl - @theta
                                                  AND x3.decl + @theta 
                                  AND doSourcesIntersect(x3.ra,x3.decl,x3.ra_err,x3.decl_err
                                                        ,x4.ra,x4.decl,x4.ra_err,x4.decl_err)
                              )
    GROUP BY x1.xtrsrcid
;
    
    SELECT x1.xtrsrcid
          ,TRUE 
          ,'X' 
          ,x1.xtrsrcid 
          ,FALSE 
          ,NULL
          ,NULL
      FROM extractedsources x1
     WHERE NOT EXISTS (SELECT a2.xtrsrc_id
                         FROM associatedsources a2
                             ,extractedsources x2
                             ,images im2
                        WHERE x2.xtrsrcid = a2.xtrsrc_id
                          AND x2.image_id = im2.imageid
                          AND im2.ds_id = (SELECT im10.ds_id
                                             FROM images im10
                                            WHERE imageid = @imageid
                                          )
                      )
   AND x1.image_id = @imageid
;



