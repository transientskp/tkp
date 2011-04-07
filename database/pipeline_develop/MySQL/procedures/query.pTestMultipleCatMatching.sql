/*
 *
 *
SET @mcsrcid = 21;

SELECT multcatsrcid
      ,ra
      ,decl
      ,ra_err
      ,decl_err
  INTO @multcatsrcid1
      ,@ra1
      ,@decl1
      ,@ra1_err
      ,@decl1_err
  FROM multiplecatalogsources
 WHERE multcatsrcid = @mcsrcid
;

SELECT @multcatsrcid1
      ,@ra1
      ,@decl1
      ,@ra1_err
      ,@decl1_err
;

INSERT INTO multiplecatalogassocs
  (src1_id
  ,src2_id
  ,weight
  ,active
  )
  SELECT @multcatsrcid1
        ,multcatsrcid
        ,getWeightRectIntersection(@ra1,@decl1,@ra1_err,@decl1_err,ra,decl,ra_err,decl_err)
        ,1
    FROM multiplecatalogsources
   WHERE multcatsrcid > @multcatsrcid1
     AND getWeightRectIntersection(@ra1,@decl1,@ra1_err,@decl1_err,ra,decl,ra_err,decl_err) >= 0
;

select SUM(ra / POW(ra_err, 2)) / SUM(1 / pow(ra_err, 2))  
      ,SUM(decl/ POW(decl_err, 2)) / SUM(1 / pow(decl_err, 2))
      ,SQRT(1 / SUM(1 / pow(ra_err, 2)))
      ,SQRT(1 / SUM(1 / pow(decl_err, 2)))
  from multiplecatalogsources
 where multcatsrcid = (select src1_id
                         from multiplecatalogassocs 
                        where multcatassocid = (select min(multcatassocid) 
                                                  from multiplecatalogassocs 
                                                 where weight = (select max(weight) 
                                                                   from multiplecatalogassocs 
                                                                   where active is true))
                      )
    or multcatsrcid = (select src2_id
                         from multiplecatalogassocs 
                        where multcatassocid = (select min(multcatassocid) 
                                                  from multiplecatalogassocs 
                                                 where weight = (select max(weight) 
                                                                   from multiplecatalogassocs 
                                                                   where active is true))
                      )
;
*/

SET @multcatassocid = 9;

SELECT a.src1_id
      ,s1.ra
      ,s1.decl
      ,s1.ra_err
      ,s1.decl_err
      ,a.src2_id
      ,s2.ra
      ,s2.decl
      ,s2.ra_err
      ,s2.decl_err
  INTO @src1_id
      ,@ra1
      ,@decl1
      ,@ra1_err
      ,@decl1_err
      ,@src2_id
      ,@ra2
      ,@decl2
      ,@ra2_err
      ,@decl2_err
  FROM multiplecatalogassocs a
      ,multiplecatalogsources s1
      ,multiplecatalogsources s2
 WHERE multcatassocid = @multcatassocid
   AND a.src1_id = s1.multcatsrcid
   AND a.src2_id = s2.multcatsrcid
;
  
SELECT @src1_id
      ,@ra1
      ,@decl1
      ,@ra1_err
      ,@decl1_err
      ,@src2_id
      ,@ra2
      ,@decl2
      ,@ra2_err
      ,@decl2_err
;

SELECT SUM(ra / POW(ra_err, 2)) / SUM(1 / pow(ra_err, 2))
      ,SUM(decl/ POW(decl_err, 2)) / SUM(1 / pow(decl_err, 2))
      ,SQRT(1 / SUM(1 / pow(ra_err, 2)))
      ,SQRT(1 / SUM(1 / pow(decl_err, 2)))
  INTO @new_ra
      ,@new_decl
      ,@new_ra_err
      ,@new_decl_err
  FROM multiplecatalogsources
 WHERE multcatsrcid = @src1_id
    OR multcatsrcid = @src2_id
;

SET @new_zone = FLOOR(@new_decl / 1);

SELECT @new_zone
      ,@new_ra
      ,@new_decl
      ,@new_ra_err
      ,@new_decl_err
;

INSERT INTO multiplecatalogsources
  (zone
  ,ra
  ,decl
  ,ra_err
  ,decl_err
  ,orig_src1_id
  ,orig_src2_id
  ,active
  )
VALUES
  (@new_zone
  ,@new_ra
  ,@new_decl
  ,@new_ra_err
  ,@new_decl_err
  ,@src1_id
  ,@src2_id
  ,TRUE
  )
;

SET @new_src_id = LAST_INSERT_ID();

SELECT @new_src_id;

UPDATE multiplecatalogsources
   SET active = FALSE
 WHERE multcatsrcid = @src1_id
    OR multcatsrcid = @src2_id
;

UPDATE multiplecatalogassocs
   SET active = FALSE
 WHERE multcatassocid = @multcatassocid
;




UPDATE multiplecatalogassocs a
      ,multiplecatalogsources s      
   SET a.src1_id = @new_src_id 
      ,a.weight = getWeightRectIntersection(@new_ra,@new_decl,@new_ra_err,@new_decl_err,s.ra,s.decl,s.ra_err,s.decl_err) 
      ,a.distance = getDistance_arcsec(@new_ra,@new_decl,s.ra,s.decl) 
 WHERE (a.src1_id = @src1_id 
        AND a.active = TRUE 
        AND a.src2_id = s.multcatsrcid
       )
    OR (a.src1_id = @src2_id
        AND a.active = TRUE 
        AND a.src2_id = s.multcatsrcid
       )
;

UPDATE multiplecatalogassocs a
      ,multiplecatalogsources s      
   SET a.src2_id = @new_src_id 
      ,a.weight = getWeightRectIntersection(@new_ra,@new_decl,@new_ra_err,@new_decl_err,s.ra,s.decl,s.ra_err,s.decl_err) 
      ,a.distance = getDistance_arcsec(@new_ra,@new_decl,s.ra,s.decl) 
 WHERE (a.src2_id = @src1_id
        AND a.active = TRUE 
        AND a.src1_id = s.multcatsrcid
       )
    OR (a.src2_id = @src2_id
        AND a.active = TRUE 
        AND a.src1_id = s.multcatsrcid
       )
;


