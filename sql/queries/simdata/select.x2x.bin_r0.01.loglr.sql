/*
 * 100 * assoc_r forces it to have binwidth = 0.01
 */

select cnt
      ,min_loglr
      ,avg_loglr
      ,max_loglr
      ,cast(bin_r_nr as double)/100 as bin_r 
  from (select count(*) as cnt 
              ,min(assoc_lr) as min_loglr
              ,avg(assoc_lr) as avg_loglr
              ,max(assoc_lr) as max_loglr
              ,cast(1 + floor(100 * assoc_r) as integer) as bin_r_nr 
          from assocxtrsources
              ,extractedsources
              ,images 
         where xtrsrc_id = xtrsrcid 
           and image_id = imageid 
           and xtrsrc_id <> assoc_xtrsrc_id 
           and ds_id = 1 
        group by bin_r_nr
       ) t 
order by bin_r
;



