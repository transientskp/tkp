SELECT bin_nr
      ,COUNT(*)
      ,AVG(assoc_distance_arcsec)
      ,MIN(assoc_distance_arcsec)
      ,MAX(assoc_distance_arcsec)
      ,AVG(assoc_r)
      ,MIN(assoc_r)
      ,MAX(assoc_r)
FROM (SELECT CAST(1 + FLOOR(2 * assoc_lr) AS INTEGER) AS bin_nr
      ,ax1.assoc_lr
      ,ax1.assoc_distance_arcsec
      ,ax1.assoc_r
  FROM assocxtrsources ax1
      ,extractedsources x1
      ,images im1
 WHERE ax1.xtrsrc_id = x1.xtrsrcid
   AND ax1.xtrsrc_id <> ax1.assoc_xtrsrc_id
   AND ax1.assoc_lr >= -100.5
   AND x1.image_id = im1.imageid
   AND im1.ds_id = 1
) t
GROUP BY bin_nr
ORDER BY bin_nr
;





SELECT bin_nr
      ,COUNT(*)
      ,AVG(assoc_distance_arcsec)
      ,MIN(assoc_distance_arcsec)
      ,MAX(assoc_distance_arcsec)
      ,AVG(assoc_r)
      ,MIN(assoc_r)
      ,MAX(assoc_r)
  FROM (SELECT CAST(1 + FLOOR(2 * assoc_lr) AS INTEGER) AS bin_nr
              ,ac1.assoc_lr
              ,ac1.assoc_distance_arcsec
              ,ac1.assoc_r
          FROM assoccatsources ac1
              ,extractedsources x1
              ,images im1
              ,obscatsources oc1
         WHERE ac1.xtrsrc_id = x1.xtrsrcid
           AND ac1.assoc_lr >= -100.5
           AND x1.image_id = im1.imageid
           AND im1.ds_id = 1
           AND ac1.assoc_catsrc_id = oc1.obscatsrcid
           AND oc1.cat_id = 3
       ) t
GROUP BY bin_nr
ORDER BY bin_nr
;

