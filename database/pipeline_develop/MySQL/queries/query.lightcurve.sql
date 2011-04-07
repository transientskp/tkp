/* this query returns the (timestamp,flux+errors) points of a given source */
SET @dsid = 1;

SELECT a1.xtrsrc_id
      ,a1.assoc_xtrsrc_id
      ,im1.taustart_timestamp
      ,x1.i_peak
      ,x1.i_peak_err
      ,x1.i_int
      ,x1.i_int_err
  FROM associatedsources a1
      ,extractedsources x1
      ,images im1
      ,datasets ds1
 WHERE a1.assoc_xtrsrc_id = x1.xtrsrcid 
   AND x1.image_id = im1.imageid
   AND im1.ds_id = ds1.dsid
   AND ds1.dsid = @dsid
ORDER BY a1.xtrsrc_id
        ,a1.assoc_xtrsrc_id
;



