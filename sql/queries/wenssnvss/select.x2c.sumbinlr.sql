select bin_lr_nr
      ,CAST(bin_lr_nr AS DOUBLE) / 2 AS bin_lr
      ,count(*) as cnt
      ,avg(reliab)
  from (select t2.xtrsrc_id
              ,t2.assoc_catsrc_id
              ,CAST(1 + FLOOR(2 * t2.assoc_lr) AS INTEGER) as bin_lr_nr 
              ,t2.assoc_lr
              ,t2.cnt_sf
              ,t2.cnt_bg
              ,(t2.cnt_sf - t2.cnt_bg / 8) / t2.cnt_sf as reliab
          from (select t1.xtrsrc_id as xtrsrc_id
                      ,t1.assoc_catsrc_id as assoc_catsrc_id
                      ,t1.assoc_lr as assoc_lr
                      ,getCountLogLRbin_CatSF(2,(t1.assoc_lr - 0.25),(t1.assoc_lr + 0.25)) as cnt_sf
                      ,getCountLogLRbin_CatBG(3,10,(t1.assoc_lr - 0.25),(t1.assoc_lr + 0.25)) as cnt_bg
                  from (select ac1.xtrsrc_id as xtrsrc_id
                              ,ac1.assoc_catsrc_id as assoc_catsrc_id
                              ,ac1.assoc_lr as assoc_lr
                          from assoccatsources ac1
                              ,extractedsources x1
                              ,images im1
                              ,catalogedsources c1
                         where ac1.xtrsrc_id = x1.xtrsrcid
                           and x1.image_id = im1.imageid
                           and im1.ds_id = 2
                           and ac1.assoc_catsrc_id = c1.catsrcid
                           and c1.cat_id = 3
                           and ac1.assoc_lr > -300
                           and ac1.xtrsrc_id between 60861 and 60870
                           and ac1.assoc_catsrc_id between 3215 and 3247
                       ) t1
               ) t2
       ) t3
group by bin_lr_nr 
order by bin_lr_nr 
;


order by t2.xtrsrc_id
        ,t2.assoc_catsrc_id
limit 10
;



/*
 * This query selects the SF sources and their calculated assoc_lr
 * Then it counts (by functions) the number of sources 
 * in the SF and BG fields (N_src, N_BG) that have 
 * an assoc_lr between assoc_lr +- 0.25  assoc_r.
 * The reliability of an association pair is then defined as 
 * (N_sf - N_bg) / N_sf
 */

select t2.xtrsrc_id
      ,t2.assoc_catsrc_id
      ,t2.assoc_lr
      ,t2.cnt_sf
      ,t2.cnt_bg
      ,(t2.cnt_sf - t2.cnt_bg / 8) / t2.cnt_sf as reliab
  from (select t1.xtrsrc_id as xtrsrc_id
              ,t1.assoc_catsrc_id as assoc_catsrc_id
              ,t1.assoc_lr as assoc_lr
              ,getCountLogLRbin_CatSF(2,(t1.assoc_lr - 0.25),(t1.assoc_lr + 0.25)) as cnt_sf
              ,getCountLogLRbin_CatBG(3,10,(t1.assoc_lr - 0.25),(t1.assoc_lr + 0.25)) as cnt_bg
          from (select ac1.xtrsrc_id as xtrsrc_id
                      ,ac1.assoc_catsrc_id as assoc_catsrc_id
                      ,ac1.assoc_lr as assoc_lr
                  from assoccatsources ac1
                      ,extractedsources x1
                      ,images im1
                 where ac1.xtrsrc_id = x1.xtrsrcid
                   and x1.image_id = im1.imageid
                   and ac1.assoc_lr > -300
                   and im1.ds_id = 2
                   and ac1.xtrsrc_id between 60861 and 60870
                   and ac1.assoc_catsrc_id between 3215 and 3247
               ) t1
       ) t2
order by t2.xtrsrc_id
        ,t2.assoc_catsrc_id
limit 10
;








