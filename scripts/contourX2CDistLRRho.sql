select xtrsrc_id 
      ,assoc_catsrc_id 
      ,cast(1 + floor(10 * assoc_distance_arcsec) as integer) as bin_dist 
      ,assoc_distance_arcsec 
      ,assoc_r 
      ,assoc_lr 
  from assoccatsources
      ,extractedsource
      ,image
      ,lsm 
 where xtrsrc = extractedsource.id
   and image = image.id
   and dataset = 1
   and assoc_catsrc_id = lsmid 
   and cat_id = 3 
order by assoc_distance_arcsec
;
