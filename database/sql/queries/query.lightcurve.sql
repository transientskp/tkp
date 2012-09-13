SELECT assoc_xtrsrc_id 
      ,image_id 
      ,CAST(taustart_ts AS TIMESTAMP) 
      ,CAST('2002-09-30' AS TIMESTAMP) 
  FROM assocxtrsources 
      ,extractedsources  
      ,images            
 WHERE xtrsrcid = assoc_xtrsrc_id 
   AND imageid = image_id         
   AND xtrsrc_id = 838
;

SELECT assoc_xtrsrc_id 
      ,image_id 
      ,CAST(taustart_ts AS DATE) 
      ,CAST('2002-09-30' AS DATE) 
      ,ra 
      ,decl 
      ,ra_err 
      ,decl_err 
      ,i_peak 
      ,i_peak_err 
      ,i_int 
      ,i_int_err  
  FROM assocxtrsources 
      ,extractedsources  
      ,images            
 WHERE xtrsrcid = assoc_xtrsrc_id 
   AND imageid = image_id         
   AND xtrsrc_id = 838
;




/* this query returns the (timestamp,flux+errors) points of a given source */
DECLARE idsid INT;
SET idsid = 1;

SELECT a1.xtrsrc_id
      ,a1.assoc_xtrsrc_id
      ,im1.taustart_timestamp
      ,x1.i_peak
      ,x1.i_peak_err
      ,x1.i_int
      ,x1.i_int_err
  FROM associatedsources a1
      ,extractedsources x1
      ,images im1
      ,datasets ds1
 WHERE a1.assoc_xtrsrc_id = x1.xtrsrcid 
   AND x1.image_id = im1.imageid
   AND im1.ds_id = ds1.dsid
   AND ds1.dsid = @dsid
ORDER BY a1.xtrsrc_id
        ,a1.assoc_xtrsrc_id
;



