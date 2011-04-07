SET @xtrsrcid = 537;
SET @catname = 'WENSS';
SET @theta = 1;
SET @zoneheight = 1;

SELECT ra
      ,decl
      ,ra_err
      ,decl_err
      ,x
      ,y
      ,z
  INTO @ra
      ,@decl
      ,@ra_err
      ,@decl_err
      ,@x
      ,@y
      ,@z
  FROM extractedsources
 WHERE xtrsrcid = @xtrsrcid
;

SET @alpha = alpha(@theta,@decl);
SET @sintheta = SIN(RADIANS(@theta));

SELECT @ra
      ,@decl
      ,@ra_err
      ,@decl_err
      ,@x
      ,@y
      ,@z
      ,@alpha
      ,@sintheta
;

SELECT @xtrsrcid AS xtrsrc_id
      ,'C' AS src_type
      ,catsrcid AS assoc_catsrcid
      ,getWeightRectIntersection(ra,decl,ra_err,decl_err,@ra,@decl,@ra_err,@decl_err) AS assoc_weight
      ,getDistance_arcsec(ra,decl,@ra,@decl) AS assoc_distance_arcsec
  FROM catalogedsources 
      ,catalogs 
 WHERE cat_id = catid 
   AND catname = @catname
   AND zone BETWEEN FLOOR((@decl - @theta) / @zoneheight)
                AND FLOOR((@decl + @theta) / @zoneheight)
   AND ra BETWEEN @ra - @alpha
              AND @ra + @alpha
   AND decl BETWEEN @decl - @theta
                AND @decl + @theta
   AND @sintheta > SIN(2 * ASIN(SQRT(POWER(x - @x, 2) + POWER(y - @y, 2) + POWER(z - @z, 2)) / 2))
   AND doSourcesIntersect(ra,decl,ra_err,decl_err,@ra,@decl,@ra_err,@decl_err)
;

