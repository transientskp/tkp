DROP FUNCTION getRelyAssocs;

CREATE FUNCTION getRelyAssocs() RETURNS TABLE (xtrsrc_id INT
                                              ,assoc_catsrc_id INT
                                              ,assoc_distance_arcsec DOUBLE
                                              ,assoc_lr DOUBLE
                                              ,cnt_sf INT
                                              ,cnt_bg INT
                                              ,assoc_rely DOUBLE
                                              )
BEGIN
  
  RETURN TABLE 
    (
     SELECT t2.xtrsrc_id
           ,t2.assoc_catsrc_id
           ,t2.assoc_distance_arcsec
           ,t2.assoc_lr
           ,t2.cnt_sf
           ,t2.cnt_bg
           ,CAST((t2.cnt_sf - t2.cnt_bg / 8) / t2.cnt_sf AS DOUBLE) AS assoc_rely
       FROM (SELECT t1.xtrsrc_id 
                   ,t1.assoc_catsrc_id 
                   ,t1.assoc_distance_arcsec 
                   ,t1.assoc_lr 
                   ,getCountLogLRbin_CatSF(1,t1.lr_min,t1.lr_max) AS cnt_sf
                   ,getCountLogLRbin_CatBG(2,9,t1.lr_min,t1.lr_max) AS cnt_bg
               FROM (SELECT ac1.xtrsrc_id
                           ,ac1.assoc_catsrc_id
                           ,ac1.assoc_distance_arcsec
                           ,ac1.assoc_lr
                           ,ac1.assoc_lr - 0.25 AS lr_min
                           ,ac1.assoc_lr + 0.25 AS lr_max 
                       FROM assoccatsources ac1
                           ,extractedsources x1
                           ,images im1
                      where ac1.xtrsrc_id = x1.xtrsrcid
                        AND x1.image_id = im1.imageid
                        AND im1.ds_id = 1
                        AND ac1.assoc_lr >= -20
                    ) t1
            ) t2
    )
    ;

END
;

