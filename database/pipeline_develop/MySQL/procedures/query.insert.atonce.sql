SELECT s1.multcatsrcid as src1_id
      ,s2.multcatsrcid as src2_id
      ,getWeightRectIntersection(s1.ra,s1.decl,s1.ra_err,s1.decl_err,s2.ra,s2.decl,s2.ra_err,s2.decl_err) as weight
      ,getDistance_arcsec(s1.ra,s1.decl,s2.ra,s2.decl) as distance
      ,TRUE as active 
  FROM multiplecatalogsources s1
      ,multiplecatalogsources s2 
 WHERE s1.cat_id < s2.cat_id 
   AND doSourcesIntersect(s1.ra,s1.decl,s1.ra_err,s1.decl_err,s2.ra,s2.decl,s2.ra_err,s2.decl_err)
;

