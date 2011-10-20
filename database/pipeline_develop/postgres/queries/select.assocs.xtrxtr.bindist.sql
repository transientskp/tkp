/* These queries all provide information about the sources that
 * were associated with each other (so having entries in assocxtrsources)
 */

/* Here we select the number of associations that a source has.
 * All sources are binned into according to their number of 
 * associations.
 */
SELECT number_of_assocs
      ,COUNT(*) as number_of_sources
  FROM (SELECT xtrsrc_id 
              ,COUNT(*) AS number_of_assocs 
          FROM assocxtrsources 
              ,extractedsources 
              ,images 
         WHERE xtrsrc_id = xtrsrcid 
           AND image_id = imageid 
           AND ds_id = 6 
        GROUP BY xtrsrc_id 
       ) t 
GROUP BY t.number_of_assocs
ORDER BY t.number_of_assocs
;

/* Here we select the distances of the associated sources
 * We bin them in bins of 0.1 arcsec width
 */
select xtrsrc_id ,assoc_xtrsrc_id ,cast(1 + floor(10 * assoc_distance_arcsec) as integer) as bin_dist ,assoc_distance_arcsec ,assoc_r ,assoc_lr  from assocxtrsources ,extractedsources ,images  where xtrsrc_id = xtrsrcid  and image_id = imageid  and xtrsrc_id <> assoc_xtrsrc_id  and ds_id = 6 order by assoc_distance_arcsec
;


select bin_dist 
      ,count(*) 
      ,avg(assoc_r) 
      ,avg(assoc_lr) 
  from (select cast(floor(assoc_distance_arcsec) as integer) as bin_dist 
              ,assoc_r 
              ,assoc_lr 
         from assoccatsources ac1 
             ,extractedsources x1 
             ,images im1 
             ,obscatsources oc1 
        where ac1.xtrsrc_id = x1.xtrsrcid 
         and assoc_lr >= -100 
         and x1.image_id = im1.imageid 
         AND im1.ds_id = %s 
         and ac1.assoc_catsrc_id = oc1.obscatsrcid 
         and oc1.cat_id = %s 
       ) t 
GROUP BY bin_dist 
ORDER BY bin_dist
;

