select * from (select ax1.xtrsrc_id as xtrsrc_id ,ax1.assoc_xtrsrc_id as assoc_xtrsrc_id,im2.imageid as img2,im2.band as band2 ,im2.taustart_ts as ts2 ,assoc_distance_arcsec ,assoc_r ,assoc_lr ,3600 * DEGREES(2 * ASIN(SQRT((c1.x - x2.x) * (c1.x - x2.x)  + (c1.y - x2.y) * (c1.y - x2.y)  + (c1.z - x2.z) * (c1.z - x2.z)  ) / 2) ) AS grb_distance_arcsec from assocxtrsources ax1 ,extractedsources x1 ,extractedsources x2 ,images im1 ,images im2 ,catalogedsources c1 where ax1.xtrsrc_id = x1.xtrsrcid and x1.image_id = im1.imageid AND ax1.assoc_xtrsrc_id = x2.xtrsrcid and x2.image_id = im2.imageid and c1.catsrcid = 2071217 and im1.ds_id = 45 AND ax1.assoc_lr >= 0) t where t.xtrsrc_id = 2143261 or t.assoc_xtrsrc_id = 2143261 order by t.xtrsrc_id,t.img2,t.assoc_xtrsrc_id;





select ax1.xtrsrc_id 
      ,ax1.assoc_xtrsrc_id 
      ,im2.band 
      ,CAST(im2.taustart_ts AS TIMESTAMP) 
      ,CAST('2003-03-29' AS TIMESTAMP) 
      /*,assoc_distance_arcsec 
      ,assoc_r 
      ,assoc_lr 
      ,3600 * DEGREES(2 * ASIN(SQRT((c1.x - x2.x) * (c1.x - x2.x) 
                                   + (c1.y - x2.y) * (c1.y - x2.y) 
                                   + (c1.z - x2.z) * (c1.z - x2.z) 
                                   ) / 2) ) AS grb_distance_arcsec */
      ,1000 * x2.i_peak 
      ,1000 * x2.i_peak_err 
      ,1000 * x2.i_int 
      ,1000 * x2.i_int_err 
  from assocxtrsources ax1 
      ,extractedsources x1 
      ,extractedsources x2 
      ,images im1 
      ,images im2 
      ,catalogedsources c1 
 where ax1.xtrsrc_id = x1.xtrsrcid 
   and x1.image_id = im1.imageid 
   AND ax1.assoc_xtrsrc_id = x2.xtrsrcid 
   and x2.image_id = im2.imageid 
   AND ax1.assoc_lr >= 0 
   AND im1.band <> 17 
   AND im2.band <> 17 
   and c1.catsrcid = 2071217 
   /*AND c1.x * x1.x + c1.y * x1.y + c1.z * x1.z > COS(RADIANS(0.05))*/
   and ax1.xtrsrc_id = 2143203
   and im1.ds_id = 45
order by im2.band 
        ,im2.taustart_ts 
;

