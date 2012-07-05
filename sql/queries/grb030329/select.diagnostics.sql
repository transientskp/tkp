select * from (select ax1.xtrsrc_id as xtrsrc_id ,ax1.assoc_xtrsrc_id as assoc_xtrsrc_id,im2.imageid as img2,im2.band as band2 ,im2.taustart_ts as ts2 ,assoc_distance_arcsec ,assoc_r ,assoc_lr ,3600 * DEGREES(2 * ASIN(SQRT((c1.x - x2.x) * (c1.x - x2.x)  + (c1.y - x2.y) * (c1.y - x2.y)  + (c1.z - x2.z) * (c1.z - x2.z)  ) / 2) ) AS grb_distance_arcsec from assocxtrsources ax1 ,extractedsources x1 ,extractedsources x2 ,images im1 ,images im2 ,catalogedsources c1 where ax1.xtrsrc_id = x1.xtrsrcid and x1.image_id = im1.imageid AND ax1.assoc_xtrsrc_id = x2.xtrsrcid and x2.image_id = im2.imageid and c1.catsrcid = 2071217 and im1.ds_id = 45 AND ax1.assoc_lr >= 0) t where t.xtrsrc_id = 2143197 or t.assoc_xtrsrc_id = 2143197 order by t.xtrsrc_id,t.img2,t.assoc_xtrsrc_id;



SELECT t1.xtrsrc_id
      ,count(*) as cnt
      ,getdistancexsource2catarcsec(t1.xtrsrc_id,2071217) as grb_dist
  FROM (SELECT ax2.xtrsrc_id 
              ,im2.band as band2
          FROM assocxtrsources ax2 
              ,extractedsources x1 
              ,extractedsources x2 
              ,images im1 
              ,images im2 
         WHERE ax2.xtrsrc_id = x1.xtrsrcid 
           AND ax2.assoc_xtrsrc_id = x2.xtrsrcid 
           AND x1.image_id = im1.imageid 
           AND x2.image_id = im2.imageid 
           AND im1.ds_id = im2.ds_id 
           AND im1.ds_id = 45
           AND im1.band <> 17
           AND im2.band <> 17
           AND ax2.xtrsrc_id IN (SELECT ax3.xtrsrc_id 
                                   FROM assocxtrsources ax3 
                                       ,extractedsources x3 
                                       ,extractedsources x4 
                                       ,images im3 
                                       ,images im4 
                                  WHERE ax3.xtrsrc_id = x3.xtrsrcid 
                                    AND ax3.assoc_xtrsrc_id = x4.xtrsrcid 
                                    AND x3.image_id = im3.imageid 
                                    AND x4.image_id = im4.imageid 
                                    AND im3.ds_id = im4.ds_id 
                                    AND im3.ds_id = 45
                                    AND im3.band = 14
                                    AND im3.band = im4.band 
                                 GROUP BY ax3.xtrsrc_id 
                                 HAVING COUNT(*) > 8 
                                )
           /*AND im1.band = im2.band */
       ) t1
group by t1.xtrsrc_id
order by cnt desc
        ,t1.xtrsrc_id
;

SELECT t1.xtrsrc_id
      ,t1.band2
      ,count(*) as cnt
  FROM (SELECT ax2.xtrsrc_id 
              ,im2.band as band2
          FROM assocxtrsources ax2 
              ,extractedsources x1 
              ,extractedsources x2 
              ,images im1 
              ,images im2 
         WHERE ax2.xtrsrc_id = x1.xtrsrcid 
           AND ax2.assoc_xtrsrc_id = x2.xtrsrcid 
           AND x1.image_id = im1.imageid 
           AND x2.image_id = im2.imageid 
           AND im1.ds_id = im2.ds_id 
           AND im1.ds_id = 45
           AND im1.band <> 17
           AND im2.band <> 17
           AND ax2.xtrsrc_id IN (SELECT ax3.xtrsrc_id 
                                   FROM assocxtrsources ax3 
                                       ,extractedsources x3 
                                       ,extractedsources x4 
                                       ,images im3 
                                       ,images im4 
                                  WHERE ax3.xtrsrc_id = x3.xtrsrcid 
                                    AND ax3.assoc_xtrsrc_id = x4.xtrsrcid 
                                    AND x3.image_id = im3.imageid 
                                    AND x4.image_id = im4.imageid 
                                    AND im3.ds_id = im4.ds_id 
                                    AND im3.ds_id = 45
                                    AND im3.band = 14
                                    AND im3.band = im4.band 
                                 GROUP BY ax3.xtrsrc_id 
                                 HAVING COUNT(*) > 5 
                                )
           /*AND im1.band = im2.band */
       ) t1
group by t1.xtrsrc_id
        ,t1.band2
order by t1.xtrsrc_id
        ,t1.band2
;


GROUP BY ax2.xtrsrc_id 
HAVING COUNT(*) > 8 
ORDER BY datapoints 
        ,ax2.xtrsrc_id
;

select band,count(*) from images where ds_id = 45 group by band;

/* we skip band 17 (8400MHz), because it only has edge sources*/


SELECT ax2.xtrsrc_id 
      ,count(*) as datapoints 
      ,1000 * min(x2.i_int) as min_i_int_mJy 
      ,1000 * avg(x2.i_int) as avg_i_int_mJy 
      ,1000 * max(x2.i_int) as max_i_int_mJy 
      ,sqrt(count(*) * (avg(x2.i_int * x2.i_int) - avg(x2.i_int) * avg(x2.i_int))/ (count(*)-1))/avg(x2.i_int) as sigma_over_mu 
  FROM assocxtrsources ax2 
      ,extractedsources x1 
      ,extractedsources x2 
      ,images im1 
      ,images im2 
 WHERE ax2.xtrsrc_id = x1.xtrsrcid 
   AND ax2.assoc_xtrsrc_id = x2.xtrsrcid 
   AND x1.image_id = im1.imageid 
   AND x2.image_id = im2.imageid 
   AND im1.ds_id = im2.ds_id 
   AND im1.ds_id = 45
   AND im1.band = 14
   AND im1.band = im2.band 
GROUP BY ax2.xtrsrc_id 
HAVING COUNT(*) > 8 
ORDER BY datapoints 
        ,ax2.xtrsrc_id
;

