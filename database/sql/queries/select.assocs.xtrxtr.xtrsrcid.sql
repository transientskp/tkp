SELECT ax1.assoc_xtrsrc_id 
      ,CAST(im1.taustart_ts AS TIMESTAMP) 
      ,CAST('2002-09-30' AS TIMESTAMP) 
      ,x1.ra
      ,x1.decl
      ,x1.ra_err/3600
      ,x1.decl_err/3600
  FROM (SELECT xtrsrc_id 
          FROM assocxtrsources 
         WHERE assoc_xtrsrc_id = 7954
       ) t
      ,assocxtrsources ax1 
      ,extractedsources x1
      ,images im1
 WHERE ax1.xtrsrc_id = t.xtrsrc_id
   AND ax1.assoc_xtrsrc_id = x1.xtrsrcid
   AND x1.image_id = im1.imageid
;


/**/
SELECT assoc_xtrsrc_id 
      ,image_id 
      ,CAST(taustart_ts AS TIMESTAMP) 
      ,CAST('2002-09-30' AS TIMESTAMP) 
  FROM assocxtrsources 
      ,extractedsources  
      ,images            
 WHERE xtrsrcid = assoc_xtrsrc_id 
   AND imageid = image_id         
   AND xtrsrc_id = 7331
;

