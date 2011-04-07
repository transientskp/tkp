SET @ds_id = 1;

SELECT 'The cursor selects these rows:' as '';

SELECT xtrsrc_id AS ixtrsrcid1
      ,src_type
      ,assoc_xtrsrcid AS ixtrsrcid2
      ,assoc_catsrcid
      ,assoc_class_id
  FROM associatedsources
      ,extractedsources 
      ,images
 WHERE xtrsrc_id = xtrsrcid
   AND image_id = imageid
   AND ds_id = @ds_id
   AND assoc_xtrsrcid IS NOT NULL
   /* how do we set src_type ? */
ORDER BY xtrsrc_id
        ,assoc_xtrsrcid
;
