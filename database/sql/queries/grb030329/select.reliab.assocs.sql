select * from (select ax1.xtrsrc_id as xtrsrc_id ,im1.imageid as img1,im1.band as band1 ,im1.taustart_ts as ts1 ,ax1.assoc_xtrsrc_id as assoc_xtrsrc_id,im2.imageid as img2,im2.band as band2 ,im2.taustart_ts as ts2 ,assoc_distance_arcsec ,assoc_r ,assoc_lr ,3600 * DEGREES(2 * ASIN(SQRT((c1.x - x2.x) * (c1.x - x2.x)  + (c1.y - x2.y) * (c1.y - x2.y)  + (c1.z - x2.z) * (c1.z - x2.z)  ) / 2) ) AS grb_distance_arcsec from assocxtrsources ax1 ,extractedsources x1 ,extractedsources x2 ,images im1 ,images im2 ,catalogedsources c1 where ax1.xtrsrc_id = x1.xtrsrcid and x1.image_id = im1.imageid AND ax1.assoc_xtrsrc_id = x2.xtrsrcid and x2.image_id = im2.imageid and c1.catsrcid = 2071217 and im1.ds_id = 37 AND c1.x * x1.x + c1.y * x1.y + c1.z * x1.z > COS(RADIANS(0.05)) AND ax1.assoc_lr >= 0) t where t.xtrsrc_id = 2139681 or t.assoc_xtrsrc_id = 2139681 order by t.img1,t.xtrsrc_id,t.img2,t.assoc_xtrsrc_id;

select ax1.xtrsrc_id ,im1.band ,im1.taustart_ts ,ax1.assoc_xtrsrc_id ,im2.band ,im2.taustart_ts ,assoc_distance_arcsec ,assoc_r ,assoc_lr ,3600 * DEGREES(2 * ASIN(SQRT((c1.x - x2.x) * (c1.x - x2.x)  + (c1.y - x2.y) * (c1.y - x2.y)  + (c1.z - x2.z) * (c1.z - x2.z)  ) / 2) ) AS grb_distance_arcsec from assocxtrsources ax1 ,extractedsources x1 ,extractedsources x2 ,images im1 ,images im2 ,catalogedsources c1 where ax1.xtrsrc_id = x1.xtrsrcid and x1.image_id = im1.imageid AND ax1.assoc_xtrsrc_id = x2.xtrsrcid and x2.image_id = im2.imageid and c1.catsrcid = 2071217 and im1.ds_id = 37 AND c1.x * x1.x + c1.y * x1.y + c1.z * x1.z > COS(RADIANS(0.05)) AND ax1.assoc_lr >= 0 order by ax1.xtrsrc_id ,im1.band ,im1.taustart_ts ,ax1.assoc_xtrsrc_id ,im2.band ,im2.taustart_ts;

select ax1.xtrsrc_id
      ,im1.band
      ,im1.taustart_ts
      ,ax1.assoc_xtrsrc_id
      ,im2.band
      ,im2.taustart_ts
      ,assoc_distance_arcsec
      ,assoc_r
      ,assoc_lr
      ,3600 * DEGREES(2 * ASIN(SQRT((c1.x - x2.x) * (c1.x - x2.x) 
                                   + (c1.y - x2.y) * (c1.y - x2.y)
                                   + (c1.z - x2.z) * (c1.z - x2.z)
                                   ) / 2) ) AS grb_distance_arcsec 
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
   and c1.catsrcid = 2071217 
   and im1.ds_id = 37
   AND c1.x * x1.x + c1.y * x1.y + c1.z * x1.z > COS(RADIANS(0.05))
   AND ax1.assoc_lr >= 0
order by ax1.xtrsrc_id
        ,im1.band
        ,im1.taustart_ts
        ,ax1.assoc_xtrsrc_id
        ,im2.band
        ,im2.taustart_ts
;


order by im2.band
        ,im2.taustart_ts
        ,im1.band
        ,im1.taustart_ts
;

/* this will give us the spectral lightcurve of 
 * xtrsrcid = 2141777
 */
SELECT ax1.assoc_xtrsrc_id 
      ,x1.image_id 
      ,im1.band
      ,im1.taustart_ts
  FROM (SELECT xtrsrc_id 
          FROM assocxtrsources 
         WHERE assoc_xtrsrc_id = 2141777 
       ) t 
      ,assocxtrsources ax1 
      ,extractedsources x1 
      ,images im1 
 WHERE ax1.xtrsrc_id = t.xtrsrc_id 
   AND ax1.assoc_xtrsrc_id = x1.xtrsrcid 
   AND x1.image_id = im1.imageid 
ORDER BY ax1.assoc_xtrsrc_id
;

/***********************************************************/

SELECT ax1.xtrsrc_id
      ,x1.image_id 
      ,im1.band
      ,im1.taustart_ts
      ,3600 * DEGREES(2 * ASIN(SQRT((c1.x - x1.x) * (c1.x - x1.x) 
                                   + (c1.y - x1.y) * (c1.y - x1.y)
                                   + (c1.z - x1.z) * (c1.z - x1.z)
                                   ) / 2) ) AS grb_dist1 
      ,x2.image_id 
      ,im2.band
      ,im2.taustart_ts
      ,ax1.assoc_xtrsrc_id 
      ,3600 * DEGREES(2 * ASIN(SQRT((c1.x - x2.x) * (c1.x - x2.x) 
                                   + (c1.y - x2.y) * (c1.y - x2.y)
                                   + (c1.z - x2.z) * (c1.z - x2.z)
                                   ) / 2) ) AS grb_dist2 
  FROM (select ax1.xtrsrc_id
              ,im1.imageid
              ,im1.band
              ,im1.taustart_ts
              ,ax1.assoc_xtrsrc_id
              ,im2.imageid
              ,im2.band
              ,im2.taustart_ts 
          from assocxtrsources ax1
              ,extractedsources x1
              ,images im1
              ,extractedsources x2
              ,images im2 
         where ax1.xtrsrc_id = x1.xtrsrcid 
           and x1.image_id = im1.imageid 
           and im1.ds_id = 37 
           and ax1.assoc_xtrsrc_id = x2.xtrsrcid 
           and x2.image_id = im2.imageid 
           and ax1.assoc_xtrsrc_id = 2141777
       ) t 
      ,assocxtrsources ax1 
      ,extractedsources x1 
      ,images im1 
      ,extractedsources x2 
      ,images im2 
      ,catalogedsources c1
 WHERE ax1.xtrsrc_id = t.xtrsrc_id 
   AND ax1.xtrsrc_id = x1.xtrsrcid 
   AND x1.image_id = im1.imageid 
   AND ax1.assoc_xtrsrc_id = x2.xtrsrcid 
   AND x2.image_id = im2.imageid 
   AND im1.band = im2.band
   AND im1.band = 14
   AND c1.cat_id = 6
   AND c1.catsrcid = 2071217 
ORDER BY im2.band
        ,im2.taustart_ts
        ,im1.band
        ,im1.taustart_ts
;

/***********************************************************/





