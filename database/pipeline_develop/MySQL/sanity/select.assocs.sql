/* Here we select all the sources that are in associatedsources.
 * It is a neat way to inspect them
 */
SELECT a.xtrsrc_id
      ,a.assoc_type
      ,a.assoc_xtrsrc_id
      ,x1.image_id
      ,a.assoc_catsrc_id
      ,CASE WHEN c.catname IS NULL 
            THEN '' 
            ELSE c.catname 
       END AS catname
      ,a.assoc_weight
      ,a.assoc_distance_arcsec 
  FROM associatedsources a 
       LEFT OUTER JOIN extractedsources x1 ON trsrc_id = xtrsrcid 
       LEFT OUTER JOIN catalogedsources c1 ON assoc_catsrc_id = catsrcid 
       LEFT OUTER JOIN catalogs c ON cat_id = catid 
ORDER BY xtrsrc_id
;

