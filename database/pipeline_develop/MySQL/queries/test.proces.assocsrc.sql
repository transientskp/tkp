SET @ds_id = 1;
SET @xtrsrcid = 7;

SELECT '------------------------------------------------------------' as '';
SELECT '------------------------------------------------------------' 
    as 'This shows the processing in the stored procedure AssocSrc()';

select CONCAT('all the sources that were in ds_id = ', @ds_id) as '';

select xtrsrcid as id
      ,image_id as img_id
      ,zone
      ,ra
      ,decl
      ,ra_err
      ,decl_err
      ,x
      ,y
      ,z 
  from extractedsources
      ,images 
 where image_id = imageid 
   and ds_id = @ds_id 
order by xtrsrcid
;

select 'all the associations ordered by id:' as '';

select id
      ,xtrsrc_id as x_id
      ,insert_src1
      ,src_type as type
      ,assoc_xtrsrcid as assoc_x
      ,insert_src2
      ,assoc_catsrcid as assoc_c
  from associatedsources
      ,extractedsources
      ,images 
 where imageid = image_id 
   and xtrsrc_id = xtrsrcid 
   and ds_id = @ds_id 
   /*
   and xtrsrc_id <> assoc_xtrsrcid
   */ 
order by id
;

select 'all the associations ordered by xtrsrc_id:' as '';

select id
      ,xtrsrc_id as x_id
      ,insert_src1
      ,src_type as type
      ,assoc_xtrsrcid as assoc_x
      ,insert_src2
      ,assoc_catsrcid as assoc_c
  from associatedsources
      ,extractedsources
      ,images 
 where imageid = image_id 
   and xtrsrc_id = xtrsrcid 
   and ds_id = @ds_id 
   /*
   and xtrsrc_id <> assoc_xtrsrcid
   */ 
order by xtrsrc_id
;

select CONCAT('We pick out source w/ xtrsrcid = ', @xtrsrcid) as '';

SELECT image_id,zone,ra,decl,ra_err,decl_err,x,y,z,i_peak,i_peak_err,i_int,i_int_err 
  INTO @image_id,@zone,@ra,@decl,@ra_err,@decl_err,@x,@y,@z,@i_peak,@i_peak_err,@i_int,@i_int_err 
  FROM extractedsources 
 WHERE xtrsrcid = @xtrsrcid;

SELECT zoneheight INTO @zoneheight FROM zoneheight;
SET @theta = 1;
SET @alpha = alpha(@theta, @decl);

SELECT @xtrsrcid,@image_id,@zone,@ra,@decl,@ra_err,@decl_err,@x,@y,@z,@theta,@alpha;

SET @sin_itheta = SIN(RADIANS(@theta));

select 'The boundaries for source association:' as '';

SELECT FLOOR((@decl - @theta)/@zoneheight) as z_min
      ,FLOOR((@decl + @theta)/@zoneheight) as z_max
      ,@ra - @alpha as ra_min
      ,@ra + @alpha as ra_max
      ,@sin_itheta as 'sin(theta)'
;

SELECT CONCAT('These sources could be associated to xtrsrcid = ', @xtrsrcid) as '';

SELECT xtrsrcid
      ,DEGREES(2 * ASIN(SQRT(POW(x - @x, 2) +
                             POW(y - @y, 2) +
                             POW(z - @z, 2)) / 2)) AS 'sin_distance(deg)'
      ,SQRT(POW(x - @x, 2) + POW(y - @y, 2) + POW(z - @z, 2)) AS 'length'
      ,x * @x + y * @y + z * @z AS 'dotprod'
      ,DEGREES(ACOS(x * @x + y * @y + z * @z)) AS 'cos_distance(deg)'
  FROM extractedsources
      ,images
 WHERE imageid = image_id
   AND ds_id = (SELECT ds_id
                  FROM images
                 WHERE imageid = @image_id
               )
   AND image_id < @image_id
   AND zone BETWEEN FLOOR((@decl - @theta)/@zoneheight)
                AND FLOOR((@decl + @theta)/@zoneheight)
   AND ra BETWEEN @ra - @alpha
              AND @ra + @alpha
   AND decl BETWEEN @decl - @theta
                AND @decl + @theta
   /*
   AND 4 * POW(@sin_itheta, 2) >
       POW(x - @x, 2) + POW(y - @y, 2) + POW(z - @z, 2)
   */
   AND @sin_itheta > SIN(2 * ASIN(SQRT(POW(x - @x, 2) +
                                      POW(y - @y, 2) +
                                      POW(z - @z, 2)) / 2))
   AND doIntersectElls(@ra,@decl,@ra_err,@decl_err
                      ,ra,decl,ra_err,decl_err)
;

SELECT 'We will delete the content of assocxtrsrcids' as '';

DELETE FROM assocxtrsrcids;

SELECT 'And then we will insert the assocs in assocxtrsrcids' as '';

INSERT INTO assocxtrsrcids
SELECT xtrsrcid as assocxtrsrcid
  FROM extractedsources
      ,images
 WHERE imageid = image_id
   AND ds_id = (SELECT ds_id
                  FROM images
                 WHERE imageid = @image_id
               )
   AND image_id < @image_id
   AND zone BETWEEN FLOOR((@decl - @theta)/@zoneheight)
                AND FLOOR((@decl + @theta)/@zoneheight)
   AND ra BETWEEN @ra - @alpha
              AND @ra + @alpha
   AND decl BETWEEN @decl - @theta
                AND @decl + @theta
   /*
   AND 4 * POW(@sin_itheta, 2) >
       POW(x - @x, 2) + POW(y - @y, 2) + POW(z - @z, 2)
   */
   AND @sin_itheta > SIN(2 * ASIN(SQRT(POW(x - @x, 2) +
                                      POW(y - @y, 2) +
                                      POW(z - @z, 2)) / 2))
   AND doIntersectElls(@ra,@decl,@ra_err,@decl_err
                      ,ra,decl,ra_err,decl_err)
;

SELECT 'We count the number of sources that could be associated, i.e. the number of rows that will be inserted' as '';

SELECT COUNT(*)
  INTO @ncount
  FROM assocxtrsrcids
;

SELECT CONCAT('The count(*) of associated sources is ', @ncount) as '';

--IF @ncount > 0 THEN
  SELECT 'ncount > 0, so we insert as follows (only those which intersect, so that might be smaller than count(*)) in table associatedsources:' as '';

  SET @cnt = 0;
  SELECT xtrsrc_id as xtrsrc_id
        ,FALSE
        ,'X' as src_type
        ,assoc_xtrsrcid
        ,@xtrsrcid as 'assoc_xtrsrcid to be inserted'
        ,@cnt = @cnt + 1
    FROM associatedsources
        ,assocxtrsrcids
        ,extractedsources 
   WHERE xtrsrc_id = xtrsrcid 
     AND assocxtrsrcid = assoc_xtrsrcid 
     AND zone BETWEEN FLOOR((@decl - @theta)/@zoneheight)
                  AND FLOOR((@decl + @theta)/@zoneheight)
     AND ra BETWEEN @ra - @alpha
                AND @ra + @alpha
     AND decl BETWEEN @decl - @theta
                  AND @decl + @theta
     /*
     AND 4 * POW(SIN(RADIANS(itheta / 2)), 2) > 
             POW(x - ix, 2) + POW(y - iy, 2) + POW(z - iz, 2)
     */
     AND @sin_itheta > SIN(2 * ASIN(SQRT(POW(x - @x, 2) + 
                                         POW(y - @y, 2) + 
                                         POW(z - @z, 2)) / 2))
     AND doIntersectElls(@ra,@decl,@ra_err,@decl_err
                        ,ra,decl,ra_err,decl_err)
--  GROUP BY xtrsrc_id
  ;
  SELECT 'ncount > 0, same as above, but now with group by xtrsrc_id:' as '';
--select @cnt:=@cnt+1 , xtrsrc_id,insert_src1,assoc_xtrsrcid,insert_src2 from (select @cnt := 0) r,associatedsources where src_type = 'X' and assoc_xtrsrcid = 7;  
  SELECT xtrsrc_id as xtrsrc_id
        ,FALSE
        ,'X' as src_type
        ,@xtrsrcid 
    FROM associatedsources
        ,assocxtrsrcids
        ,extractedsources 
   WHERE xtrsrc_id = xtrsrcid 
     AND assocxtrsrcid = assoc_xtrsrcid 
     AND zone BETWEEN FLOOR((@decl - @theta)/@zoneheight)
                  AND FLOOR((@decl + @theta)/@zoneheight)
     AND ra BETWEEN @ra - @alpha
                AND @ra + @alpha
     AND decl BETWEEN @decl - @theta
                  AND @decl + @theta
     /*
     AND 4 * POW(SIN(RADIANS(itheta / 2)), 2) > 
             POW(x - ix, 2) + POW(y - iy, 2) + POW(z - iz, 2)
     */
     AND @sin_itheta > SIN(2 * ASIN(SQRT(POW(x - @x, 2) + 
                                         POW(y - @y, 2) + 
                                         POW(z - @z, 2)) / 2))
     AND doIntersectElls(@ra,@decl,@ra_err,@decl_err
                        ,ra,decl,ra_err,decl_err)
  GROUP BY xtrsrc_id
  ;

--ELSE
  SELECT 'ncount = 0, so we insert as follows in table associatedsources:' as '';

  SELECT @xtrsrcid as xtrsrc_id
        ,'X' as src_type
        ,@xtrsrcid as assoc_xtrsrcid
  ;

--END IF;
