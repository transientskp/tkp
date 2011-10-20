DROP FUNCTION getRelyNormFacAssocs;

CREATE FUNCTION getRelyNormFacAssocs() RETURNS TABLE (xtrsrc_id INT
                                                     ,cnt INT
                                                     ,normfac double precision
                                                     ) as $$
BEGIN
  
  RETURN query
     select t3.xtrsrc_id
           ,count(*) as cnt
           ,1 + sum(assoc_rely/(1 - assoc_rely)) as normfac
       from (select t2.xtrsrc_id
                   ,CAST((t2.cnt_sf - t2.cnt_bg / 8) / t2.cnt_sf AS double precision) as assoc_rely
               from (select t1.xtrsrc_id 
                           ,getCountLogLRbin_CatSF(1, t1.lr_min, t1.lr_max) as cnt_sf
                           ,getCountLogLRbin_CatBG(2, 9, t1.lr_min, t1.lr_max) as cnt_bg
                       from (select ac1.xtrsrc_id
                                   ,ac1.assoc_lr-0.25 as lr_min
                                   ,ac1.assoc_lr+0.25 as lr_max 
                               from assoccatsources ac1
                                   ,extractedsources x1
                                   ,images im1
                              where ac1.xtrsrc_id = x1.xtrsrcid
                                and x1.image_id = im1.imageid
                                and im1.ds_id = 1
                                and ac1.assoc_lr >= -20
                            ) t1
                    ) t2
            ) t3
     group by t3.xtrsrc_id
    ;

END
;
$$ language plpgsql;
