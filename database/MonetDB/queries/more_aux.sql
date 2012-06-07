SET @ds_id = 1;
SET @xtrsrcid = 5;

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

select 'all the associations:' as '';

select id
      ,xtrsrc_id
      ,assoc_xtrsrcid 
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

SELECT FLOOR((@decl - @theta)/@zoneheight) as zone_min
      ,FLOOR((@decl + @theta)/@zoneheight) as zone_max
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
   
   AND 4 * POW(@sin_itheta, 2) >
       POW(x - @x, 2) + POW(y - @y, 2) + POW(z - @z, 2)
   /*
   AND @sin_itheta > SIN(2 * ASIN(SQRT(POW(x - @x, 2) +
                                      POW(y - @y, 2) +
                                      POW(z - @z, 2)) / 2))
   */
   AND doIntersectElls(@ra,@decl,@ra_err,@decl_err
                      ,ra,decl,ra_err,decl_err)
;

/*SELECT xtrsrcid as id
      ,zone
      ,ra
      ,decl
      ,ra_err as ra_e
      ,decl_err as decl_e
      ,GREATEST(@ra_err,@decl_err) + GREATEST(ra_err,decl_err) as 'theta(deg)'
      ,RADIANS((GREATEST(@ra_err,@decl_err) + GREATEST(ra_err,decl_err)) / 2) as 'theta/2(rad)'
      ,SIN(RADIANS((GREATEST(@ra_err,@decl_err) + GREATEST(ra_err,decl_err)) / 2)) as 'sin(theta/2)'
      ,SQRT(POW(x - @x, 2)+POW(y - @y, 2)+POW(z - @z, 2))/2 as halfdistvect
      ,SIN(RADIANS((GREATEST(@ra_err,@decl_err) + GREATEST(ra_err,decl_err)) / 2)) > SQRT(POW(x - @x, 2)+POW(y - @y, 2)+POW(z - @z, 2))/2 as distcheck
      ,FLOOR((@decl - (GREATEST(@ra_err,@decl_err) + GREATEST(ra_err,decl_err)))/@zoneheight) as zone_min
      ,FLOOR((@decl + (GREATEST(@ra_err,@decl_err) + GREATEST(ra_err,decl_err)))/@zoneheight) as zone_max
      ,@ra - (alpha((GREATEST(@ra_err,@decl_err) + GREATEST(ra_err,decl_err)), @decl)) as ra_min
      ,@ra + (alpha((GREATEST(@ra_err,@decl_err) + GREATEST(ra_err,decl_err)), @decl)) as ra_max
      ,@decl - (GREATEST(@ra_err,@decl_err) + GREATEST(ra_err,decl_err)) as decl_min
      ,@decl + (GREATEST(@ra_err,@decl_err) + GREATEST(ra_err,decl_err)) as decl_max
      ,4 * POW(SIN(RADIANS((GREATEST(@ra_err,@decl_err) + GREATEST(ra_err,decl_err)) / 2)), 2) as links
      ,POW(x - @x, 2) + POW(y - @y, 2) + POW(z - @z, 2) as rechts
      ,4 * POW(SIN(RADIANS((GREATEST(@ra_err,@decl_err) + GREATEST(ra_err,decl_err)) / 2)), 2) > POW(x - @x, 2) + POW(y - @y, 2) + POW(z - @z, 2) as 'l>r'
      ,(POW(x - @x, 2) + POW(y - @y, 2) + POW(z - @z, 2)) / 2 as diffvector
      ,SIN(RADIANS((GREATEST(@ra_err,@decl_err) + GREATEST(ra_err,decl_err)) / 2)) > (POW(x - @x, 2) + POW(y - @y, 2) + POW(z - @z, 2)) / 2 as 'sin>dist'
      ,COS(RADIANS(GREATEST(@ra_err,@decl_err) + GREATEST(ra_err,decl_err))) as cos
      ,(@x * x + @y * y + @z * z) > COS(RADIANS(GREATEST(@ra_err,@decl_err) + GREATEST(ra_err,decl_err))) as 'dot>cos'
      ,SQRT(x*x+y*y+z*z) as length
      ,2*SIN(RADIANS((GREATEST(@ra_err,@decl_err) + GREATEST(ra_err,decl_err)) / 2)) as sin
      ,2*SIN(RADIANS((GREATEST(@ra_err,@decl_err) + GREATEST(ra_err,decl_err)) / 2)) > SQRT(POW(x - @x, 2)+POW(y - @y, 2)+POW(z - @z, 2)) as 'inner'
      ,(@x * x + @y * y + @z * z) as dotprod
  FROM extractedsources
      ,images 
 WHERE imageid = image_id 
   AND ds_id = (SELECT ds_id FROM images WHERE imageid = @image_id) 
   AND image_id < @image_id 
   AND zone BETWEEN FLOOR((@decl - (GREATEST(@ra_err,@decl_err) + GREATEST(ra_err,decl_err)))/@zoneheight) 
                AND FLOOR((@decl + (GREATEST(@ra_err,@decl_err) + GREATEST(ra_err,decl_err)))/@zoneheight) 
   AND ra BETWEEN @ra - (alpha((GREATEST(@ra_err,@decl_err) + GREATEST(ra_err,decl_err)), @decl)) 
              AND @ra + (alpha((GREATEST(@ra_err,@decl_err) + GREATEST(ra_err,decl_err)), @decl)) 
   AND decl BETWEEN @decl - (GREATEST(@ra_err,@decl_err) + GREATEST(ra_err,decl_err)) 
                AND @decl + (GREATEST(@ra_err,@decl_err) + GREATEST(ra_err,decl_err)) 
   AND doIntersectElls(@ra,@decl,@ra_err,@decl_err,ra,decl,ra_err,decl_err) 
   AND (@x * x + @y * y + @z * z) > COS(RADIANS(GREATEST(@ra_err,@decl_err) + GREATEST(ra_err,decl_err)))
   AND 4 * POW(SIN(RADIANS((GREATEST(@ra_err,@decl_err) + GREATEST(ra_err,decl_err)) / 2)), 2) > 
             POW(x - @x, 2) + POW(y - @y, 2) + POW(z - @z, 2) 
order by xtrsrcid
;
*/
