SELECT xtrsrcid
      ,image_id
      ,zone
      ,ra
      ,decl
      ,ra_err
      ,decl_err
      ,x
      ,y
      ,z
      ,i_peak
      ,i_peak_err
      ,i_int
      ,i_int_err
      ,GREATEST(ra_err,decl_err)
  INTO @xtrsrcid
      ,@image_id
      ,@zone
      ,@ra
      ,@decl
      ,@ra_err
      ,@decl_err
      ,@x
      ,@y
      ,@z
      ,@i_peak
      ,@i_peak_err
      ,@i_int
      ,@i_int_err
      ,@theta
  FROM extractedsources 
 WHERE xtrsrcid = 819
;

SELECT xtrsrcid,image_id,zone,ra,decl,ra_err,decl_err,x,y,z,i_peak,i_peak_err,i_int,i_int_err,GREATEST(ra_err,decl_err) INTO @xtrsrcid,@image_id,@zone,@ra,@decl,@ra_err,@decl_err,@x,@y,@z,@i_peak,@i_peak_err,@i_int,@i_int_err,@theta FROM extractedsources WHERE xtrsrcid = 3827;
SELECT zoneheight INTO @zoneheight FROM zoneheight;
SET @alpha = alpha(@theta, @decl);
SELECT @xtrsrcid,@image_id,@zone,@ra,@decl,@ra_err,@decl_err,@x,@y,@z,@i_peak,@i_peak_err,@i_int,@i_int_err,@theta,@zoneheight;
SELECT xtrsrcid FROM extractedsources,images WHERE imageid = image_id AND ds_id = (SELECT ds_id FROM images WHERE imageid = @image_id) AND image_id < @image_id AND zone BETWEEN FLOOR((@decl - @theta)/@zoneheight) AND FLOOR((@decl + @theta)/@zoneheight) AND ra BETWEEN @ra - @alpha AND @ra + @alpha AND decl BETWEEN @decl - @theta AND @decl + @theta AND 4 * POW(SIN(RADIANS(@theta / 2)), 2) > POW(x - @x, 2) + POW(y - @y, 2) + POW(z - @z, 2) AND doIntersectElls(@ra,@decl,@ra_err,@decl_err,ra,decl,ra_err,decl_err);

/* These are the sources to be checked for association.
 * They are all in the same dataset but not in the current image
 */
SELECT xtrsrcid
      ,zone
      ,ra
      ,decl
      ,ra_err
      ,decl_err
      ,image_id
      ,ds_id
      ,tau
      ,band
      ,seq_nr
  FROM extractedsources
      ,images
      ,datasets
 WHERE image_id = imageid
   AND ds_id = dsid
   AND ds_id = (SELECT ds_id
                  FROM images
                 WHERE imageid = @image_id
               )
   AND image_id <> @image_id
;

SELECT xtrsrcid
      ,zone
      ,ra
      ,decl
      ,ra_err
      ,decl_err
      ,image_id
      ,ds_id
      ,tau
      ,band
      ,seq_nr
  FROM extractedsources
      ,images
      ,datasets
 WHERE image_id = imageid
   AND ds_id = dsid
   AND ds_id = (SELECT ds_id
                  FROM images
                 WHERE imageid = @image_id
               )
   AND seq_nr = (SELECT seq_nr - 1
                   FROM images
                  WHERE imageid = @image_id
                )
;



/* Of course, we can retrieve and associate at once:
*/



SELECT xtrsrcid
      ,zone
      ,ra
      ,decl
      ,ra_err
      ,decl_err
      ,image_id
      ,ds_id
      ,tau
      ,band
      ,seq_nr
  FROM extractedsources
      ,images
      ,datasets
 WHERE image_id = imageid
   AND ds_id = dsid
   AND ds_id = (SELECT ds_id
                  FROM images
                 WHERE imageid = @image_id
               )
   AND seq_nr = (SELECT seq_nr - 1
                   FROM images
                  WHERE imageid = @image_id
                )
   AND zone BETWEEN FLOOR((@decl - @theta)/@zoneheight)
                AND FLOOR((@decl + @theta)/@zoneheight)
   AND ra BETWEEN @ra - @alpha
              AND @ra + @alpha
   AND decl BETWEEN @decl - @theta
                AND @decl + @theta
   /* TODO: change to more accurate sin^2 */
   AND 4 * POW(SIN(RADIANS(@theta / 2)), 2) > POW(x - @x, 2) + POW(y - @y, 2) + POW(z - @z, 2)
   /*AND (@x * x + @y * y + @z * z) > COS(RADIANS(@theta))*/
   AND doIntersectElls(@ra,@decl,@ra_err,@decl_err
                      ,ra,decl,ra_err,decl_err)
;

SELECT xtrsrcid,zone,ra,decl,ra_err,decl_err,image_id,ds_id,tau,band,seq_nr FROM extractedsources,images,datasets WHERE image_id = imageid AND ds_id = dsid AND ds_id = (SELECT ds_id FROM images WHERE imageid = @image_id) AND seq_nr = (SELECT seq_nr - 1 FROM images WHERE imageid = @image_id) AND zone BETWEEN FLOOR((@decl - @theta)/@zoneheight) AND FLOOR((@decl + @theta)/@zoneheight) AND ra BETWEEN @ra - @alpha AND @ra + @alpha AND decl BETWEEN @decl - @theta AND @decl + @theta AND 4 * POW(SIN(RADIANS(@theta / 2)), 2) > POW(x - @x, 2) + POW(y - @y, 2) + POW(z - @z, 2) AND doIntersectElls(@ra,@decl,@ra_err,@decl_err,ra,decl,ra_err,decl_err);

SELECT xtrsrcid INTO @assoc_xtrsrcid FROM extractedsources,images,datasets WHERE image_id = imageid AND ds_id = dsid AND ds_id = (SELECT ds_id FROM images WHERE imageid = @image_id) AND seq_nr = (SELECT seq_nr - 1 FROM images WHERE imageid = @image_id) AND zone BETWEEN FLOOR((@decl - @theta)/@zoneheight) AND FLOOR((@decl + @theta)/@zoneheight) AND ra BETWEEN @ra - @alpha AND @ra + @alpha AND decl BETWEEN @decl - @theta AND @decl + @theta AND 4 * POW(SIN(RADIANS(@theta / 2)), 2) > POW(x - @x, 2) + POW(y - @y, 2) + POW(z - @z, 2) AND doIntersectElls(@ra,@decl,@ra_err,@decl_err,ra,decl,ra_err,decl_err);




