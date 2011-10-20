select count(*) from assocxtrsources,extractedsources,images where xtrsrc_id = xtrsrcid and image_id = imageid and xtrsrc_id <> assoc_xtrsrc_id and ds_id = 1 order by assoc_distance_arcsec;

select xtrsrc_id,assoc_xtrsrc_id,cast(1 + floor(10 * assoc_distance_arcsec) as integer) as bin_dist,assoc_distance_arcsec,assoc_r,assoc_lr from assocxtrsources,extractedsources,images where xtrsrc_id = xtrsrcid and image_id = imageid and xtrsrc_id <> assoc_xtrsrc_id and ds_id = 1 order by assoc_distance_arcsec;

select xtrsrc_id 
      ,assoc_xtrsrc_id 
      ,cast(1 + floor(10 * assoc_distance_arcsec) as integer) as bin_dist 
      ,assoc_distance_arcsec 
      ,assoc_r 
      ,assoc_lr 
  from assocxtrsources 
      ,extractedsources 
      ,images 
 where xtrsrc_id = xtrsrcid 
   and image_id = imageid 
   and xtrsrc_id <> assoc_xtrsrc_id 
   and ds_id = %s 
order by assoc_distance_arcsec
;

