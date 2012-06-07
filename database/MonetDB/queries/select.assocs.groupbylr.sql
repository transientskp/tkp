SELECT CASE WHEN ac1.assoc_lr < -35  THEN -35.1  ELSE ac1.assoc_lr END FROM assoccatsources ac1 ,extractedsources x1 ,images im1 ,obscatsources oc1 WHERE ac1.xtrsrc_id = x1.xtrsrcid AND x1.image_id = im1.imageid AND im1.ds_id = 2 AND ac1.assoc_catsrc_id = oc1.obscatsrcid AND oc1.cat_id = 3
;

SELECT CASE WHEN ac1.assoc_lr < -35 
            THEN -35.1
            ELSE ac1.assoc_lr
       END 
  FROM assoccatsources ac1 
      ,extractedsources x1 
      ,images im1 
      ,obscatsources oc1 
 WHERE ac1.xtrsrc_id = x1.xtrsrcid 
   AND x1.image_id = im1.imageid 
   AND im1.ds_id = 2 
   AND ac1.assoc_catsrc_id = oc1.obscatsrcid 
   AND oc1.cat_id = 3
LIMIT 10
;

SELECT bin_nr
      ,COUNT(*)
  FROM (SELECT CAST(1 + FLOOR(2 * t.bin_lr) AS INTEGER) AS bin_nr
          FROM (SELECT ac1.xtrsrc_id 
                      ,ac1.assoc_catsrc_id 
                      ,ac1.assoc_r 
                      ,ac1.assoc_lr 
                      ,CASE WHEN ac1.assoc_lr < -100 
                            THEN -100.1
                            ELSE ac1.assoc_lr
                       END AS bin_lr
                  FROM assoccatsources ac1 
                      ,extractedsources x1 
                      ,images im1 
                      ,obscatsources oc1 
                 WHERE ac1.xtrsrc_id = x1.xtrsrcid 
                   AND ac1.assoc_lr > -320 
                   AND x1.image_id = im1.imageid 
                   AND im1.ds_id = 2 
                   AND ac1.assoc_catsrc_id = oc1.obscatsrcid 
                   AND oc1.cat_id = 3
               ) t
       ) t1
GROUP BY bin_nr
ORDER BY bin_nr
;

SELECT bin_nr,COUNT(*) FROM (SELECT CAST(-1 * FLOOR(2 * t.bin_lr) AS INTEGER) AS bin_nr FROM (SELECT ac1.xtrsrc_id,ac1.assoc_catsrc_id,ac1.assoc_r,ac1.assoc_lr,CASE WHEN ac1.assoc_lr < -35 THEN -35.1 ELSE ac1.assoc_lr END AS bin_lr FROM assoccatsources ac1,extractedsources x1,images im1,obscatsources oc1 WHERE ac1.xtrsrc_id = x1.xtrsrcid AND x1.image_id = im1.imageid AND im1.ds_id = 2 AND ac1.assoc_catsrc_id = oc1.obscatsrcid AND oc1.cat_id = 3) t) t1 GROUP BY bin_nr ORDER BY bin_nr
;

