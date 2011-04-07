select bin_nr
      ,count(*)
      ,avg(assoc_lr)
      ,avg(assoc_distance_arcsec)
  from (select cast(1+floor(2*assoc_lr) as integer) as bin_nr 
              ,assoc_lr
              ,assoc_distance_arcsec
          from assoccatsources ac1
              ,extractedsources x1
              ,obscatsources oc1 
         where assoc_catsrc_id = obscatsrcid 
           and oc1.cat_id = 3 
           and xtrsrc_id = xtrsrcid 
           and image_id > 1 
           and assoc_lr >= -300.5 
       ) t
group by bin_nr 
order by bin_nr
;

select bin_dist
      ,count(*)
      ,avg(assoc_r)
  from (select cast(floor(assoc_distance_arcsec) as integer) as bin_dist
              ,assoc_r 
          from assoccatsources ac1
              ,extractedsources x1
              ,images im1
              ,obscatsources oc1
         where ac1.xtrsrc_id = x1.xtrsrcid
           and assoc_lr >= -100 
           and x1.image_id = im1.imageid
           AND im1.ds_id = 2 
           and ac1.assoc_catsrc_id = oc1.obscatsrcid 
           and oc1.cat_id = 3 
       ) t
GROUP BY bin_dist
ORDER BY bin_dist
;

