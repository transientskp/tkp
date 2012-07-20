select bin_r
      ,count(*)
      ,avg(assoc_r)
      ,avg(assoc_distance_arcsec)
  from (select cast(floor(assoc_r) as integer) as bin_r
              ,assoc_r
              ,assoc_distance_arcsec
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
GROUP BY bin_r
ORDER BY bin_r
;

select bin_r
      ,count(*)
  from (select cast(floor(assoc_r) as integer) as bin_r
          from assoccatsources ac1
              ,extractedsources x1
              ,images im1
              ,obscatsources oc1
         where ac1.xtrsrc_id = x1.xtrsrcid
           and assoc_lr >= -300 
           and x1.image_id = im1.imageid
           AND im1.ds_id = 2 
           and ac1.assoc_catsrc_id = oc1.obscatsrcid 
           and oc1.cat_id = 3 
       ) t
GROUP BY bin_r
ORDER BY bin_r
;

