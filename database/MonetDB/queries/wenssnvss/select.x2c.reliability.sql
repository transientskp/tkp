/*create table aux_assocs_wenss
  (xtrsrc_id INT
  ,assoc_catsrc_id INT
  ,bin_lr_nr INT
  ,assoc_lr DOUBLE
  ,cnt_sf INT
  ,cnt_bg INT
  ,reliab DOUBLE
  )
;
*/
insert into aux_assocs_wenss 
  (xtrsrc_id
  ,assoc_catsrc_id 
  ,bin_lr_nr 
  ,assoc_lr 
  ,cnt_sf 
  ,cnt_bg
  ,reliab 
  )
  select t2.xtrsrc_id
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
                       ) t1
               ) t2
;

select bin_lr_nr
      ,CAST(bin_lr_nr AS DOUBLE) / 2 AS bin_lr
      ,count(*) as cnt
      ,avg(reliab)
  from aux_assocs_wenss
 where cnt_sf > 1000
group by bin_lr_nr 
order by bin_lr_nr 
;

/*
                           and ac1.xtrsrc_id between 60861 and 60870
                           and ac1.assoc_catsrc_id between 3215 and 3247
*/
/*
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
*/


