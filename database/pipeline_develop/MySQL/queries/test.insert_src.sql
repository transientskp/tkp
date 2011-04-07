SELECT xtrsrcid AS assocxtrsrcid
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
AND @sin_itheta > SIN(2 * ASIN(SQRT(POW(x - @x, 2) +
POW(y - @y, 2) +
POW(z - @z, 2)) / 2))
AND doIntersectElls(@ra,@decl,@ra_err,@decl_err
,ra,decl,ra_err,decl_err)
;

