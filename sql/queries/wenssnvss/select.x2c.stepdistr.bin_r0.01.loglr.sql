SELECT * 
  FROM (SELECT npairs 
              ,CAST(bin_lr_nr AS DOUBLE)/2 AS bin_lr 
              ,bin_lr_nr 
          FROM (SELECT COUNT(*) AS npairs 
                      ,CAST(1 + floor(2 * assoc_lr) AS INTEGER) AS bin_lr_nr 
                  FROM assoccatsources 
                      ,extractedsources 
                      ,images 
                      ,lsm 
                  WHERE xtrsrc_id = xtrsrcid 
                    AND image_id = imageid 
                    AND ds_id = 2
                    AND assoc_catsrc_id = lsmid 
                    AND cat_id = 3
                    AND assoc_lr > -40 
                GROUP BY bin_lr_nr 
               ) t 
       ) t2 
ORDER BY t2.bin_lr
;





SELECT count(*)
  FROM (SELECT npairs
              ,min_loglr 
              ,avg_loglr 
              ,max_loglr 
              ,CAST(bin_r_nr AS DOUBLE)/40 AS bin_r 
              ,bin_r_nr 
          FROM (SELECT COUNT(*) AS npairs 
                      ,MIN(assoc_lr) AS min_loglr 
                      ,AVG(assoc_lr) AS avg_loglr 
                      ,MAX(assoc_lr) AS max_loglr 
                      ,CAST(1 + floor(40 * assoc_r) AS INTEGER) AS bin_r_nr 
                  FROM assoccatsources 
                      ,extractedsources 
                      ,images 
                      ,lsm 
                  WHERE xtrsrc_id = xtrsrcid 
                    AND image_id = imageid 
                    AND ds_id = 2
                    AND assoc_catsrc_id = lsmid 
                    AND cat_id = 3 
                    AND assoc_lr > -100
                GROUP BY bin_r_nr 
               ) t 
       ) t2 
ORDER BY t2.bin_r
;

