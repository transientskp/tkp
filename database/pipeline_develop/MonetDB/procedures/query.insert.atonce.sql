SELECT getWeightRectIntersection(41.820210000000003, 69.025859999999994, 22.5,   8.4000000000000004, 41.831499999999998, 69.024780000000007, 27, 28.916116926700553);
SELECT getDistance_arcsec(41.820210000000003, 69.025859999999994, 41.831499999999998, 69.024780000000007);


select distance
  from (
SELECT s1.multcatsrcid as src1_id
      ,s2.multcatsrcid as src2_id
      ,s1.ra as ra1
      ,s1.decl as decl1
      ,s1.ra_err
      ,s1.decl_err
      ,s2.ra as ra2
      ,s2.decl as decl2
      ,s2.ra_err
      ,s2.decl_err
      ,getWeightRectIntersection(s1.ra,s1.decl,s1.ra_err,s1.decl_err,s2.ra,s2.decl,s2.ra_err,s2.decl_err) as weight
      ,getDistance_arcsec(s1.ra,s1.decl,s2.ra,s2.decl) as distance
  FROM multiplecatalogsources s1
      ,multiplecatalogsources s2 
 WHERE s1.multcatsrcid = 93
   AND s2.multcatsrcid = 132
   ) as t
;

/*
call MultipleCatMatchingInit();
SELECT s1.multcatsrcid as src1_id
      ,s2.multcatsrcid as src2_id
      ,getWeightRectIntersection(s1.ra,s1.decl,s1.ra_err,s1.decl_err,s2.ra,s2.decl,s2.ra_err,s2.decl_err) as weight
      ,getDistance_arcsec(s1.ra,s1.decl,s2.ra,s2.decl) as distance
      ,TRUE as active 
  FROM multiplecatalogsources s1
      ,multiplecatalogsources s2 
 WHERE s1.cat_id < s2.cat_id 
   AND doSourcesIntersect(s1.ra,s1.decl,s1.ra_err,s1.decl_err,s2.ra,s2.decl,s2.ra_err,s2.decl_err)
ORDER BY weight DESC
;
*/
