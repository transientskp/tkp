SELECT a.xtrsrc_id
      ,AVG(e.ra)
      ,AVG(e.decl)
      ,AVG(e.ra_err)
      ,AVG(e.decl_err) 
      ,AVG(e.i_peak)
      ,AVG(e.i_peak_err)
      ,AVG(e.i_int)
      ,AVG(e.i_int_err)
  FROM associatedsources a
      ,extractedsources e
      ,images i 
 WHERE i.imageid = e.image_id  
   AND a.xtrsrc_id = e.xtrsrcid 
   AND a.src_type = 'X' 
   AND ds_id = 1 
   AND a.assoc_xtrsrcid IS NOT NULL 
GROUP BY a.xtrsrc_id  
ORDER BY a.xtrsrc_id
;
