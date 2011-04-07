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
              ,lsm lsm1
         WHERE ac1.xtrsrc_id = x1.xtrsrcid
           AND ac1.assoc_lr >= -100.5
           AND x1.image_id = im1.imageid
           AND im1.ds_id = 1
           AND ac1.assoc_catsrc_id = lsm1.lsmid
           AND lsm1.cat_id = 3
       ) t
GROUP BY bin_nr
ORDER BY bin_nr
;

