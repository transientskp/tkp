select avg(log10(x1.i_int / c1.i_int_avg) / log10(c1.freq_eff / im1.freq_eff)) as sp_index_avg from assoccatsources ac1,catalogedsources c1,extractedsources x1,images im1 where assoc_catsrc_id = catsrcid and xtrsrc_id = xtrsrcid and image_id = imageid and ds_id = 2 and cat_id = 3 and assoc_lr > 3; 

 im1.freq_eff
,x1.i_int
,x1.i_int_err
,c1.freq_eff
,c1.i_int_avg
,c1.i_int_avg_err
,log10(x1.i_int / c1.i_int_avg) / log10(c1.freq_eff / im1.freq_eff) as sp_index



select count(*) 
  from assoccatsources
      ,catalogedsources
      ,extractedsources
      ,images 
 where assoc_catsrc_id = catsrcid 
   and xtrsrc_id = xtrsrcid 
   and image_id = imageid 
   and ds_id = 2 
   and cat_id = 3 
   and assoc_lr > 3 
;


select count(*) from assoccatsources,catalogedsources,extractedsources,images where assoc_catsrc_id = catsrcid and xtrsrc_id = xtrsrcid and image_id = imageid and ds_id = 2 and cat_id = 3 and assoc_lr > 3 ;
