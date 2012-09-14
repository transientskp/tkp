/*
 * 100 * assoc_r forces it to have binwidth = 0.01
 */
--select npairs,min_loglr,avg_loglr,max_loglr,cast(bin_r_nr as double)/100 as bin_r from (select count(*) as npairs,min(assoc_lr) as min_loglr,avg(assoc_lr) as avg_loglr,max(assoc_lr) as max_loglr,cast(1 + floor(100 * assoc_r) as integer) as bin_r_nr from assoccatsources,extractedsources,images,lsm where xtrsrc_id = xtrsrcid and image_id = imageid and ds_id = 2 and assoc_catsrc_id = lsmid and cat_id = 3 and assoc_lr > -300 group by bin_r_nr) t order by bin_r;


select * 
  from (
select npairs
      ,avg_loglr
      ,cast(bin_r_nr as double) / 40 as bin_r 
      ,bin_r_nr
  from (select count(*) as npairs
              ,avg(assoc_lr) as avg_loglr
              ,cast(1 + floor(40 * assoc_r) as integer) as bin_r_nr 
          from assoccatsources
              ,extractedsources
              ,images 
              ,lsm
         where xtrsrc_id = xtrsrcid 
           and image_id = imageid 
           /*and ds_id between 3 and 10
           */and ds_id = 2
           and assoc_catsrc_id = lsmid 
           and cat_id = 3
           and assoc_lr > -100
        group by bin_r_nr
       ) t 
     ) t2
order by t2.bin_r
;



