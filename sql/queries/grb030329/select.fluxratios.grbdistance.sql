select * from (select x1.ra,x1.decl,/*x1.ra_err,x1.decl_err,*/x1.i_peak,x1.i_int,c1.i_int_avg,c1.i_int_avg / x1.i_peak as ip_ratio,c1.i_int_avg / x1.i_int as ii_ratio,3600 * DEGREES(2 * ASIN(SQRT(POWER((COS(RADIANS(x1.decl)) * COS(RADIANS(x1.ra))- COS(RADIANS(21.521663889)) * COS(RADIANS(161.208329167))), 2)+ POWER((COS(RADIANS(x1.decl)) * SIN(RADIANS(x1.ra))- COS(RADIANS(21.521663889)) * SIN(RADIANS(161.208329167))), 2)+ POWER((SIN(RADIANS(x1.decl))- SIN(RADIANS(21.521663889))), 2)) / 2)) AS grb_dist_arcsec from assoccatsources,catalogedsources c1,extractedsources x1,images where xtrsrc_id = xtrsrcid and image_id = imageid and ds_id = 18 and assoc_catsrc_id = catsrcid and cat_id = 3 and assoc_lr > 0) t order by grb_dist_arcsec asc

select x1.ra,x1.decl,x1.ra_err,x1.decl_err,x1.i_peak,x1.i_int,c1.i_int_avg,c1.i_peak_avg / x1.i_peak as pi_ratio,c1.i_int_avg / x1.i_peak as ii_ratio,3600 * DEGREES(2 * ASIN(SQRT(POWER((COS(RADIANS(x1.decl)) * COS(RADIANS(x1.ra))- COS(RADIANS(21.521663889)) * COS(RADIANS(161.208329167))), 2)+ POWER((COS(RADIANS(x1.decl)) * SIN(RADIANS(x1.ra))- COS(RADIANS(21.521663889)) * SIN(RADIANS(161.208329167))), 2)+ POWER((SIN(RADIANS(x1.decl))- SIN(RADIANS(21.521663889))), 2)) / 2)) AS grb_dist_arcsec from assoccatsources,catalogedsources c1,extractedsources x1,images where xtrsrc_id = xtrsrcid and image_id = imageid and ds_id = 18 and assoc_catsrc_id = catsrcid and cat_id = 3 and assoc_lr > 3 and assoc_r < 1 order by grb_dist_arcsec desc;

select x1.ra
      ,x1.decl
      ,x1.ra_err
      ,x1.decl_err
      ,x1.i_peak
      ,x1.i_int
      ,c1.i_int_avg
      ,c1.i_peak_avg / x1.i_peak as pi_ratio
      ,c1.i_int_avg / x1.i_peak as ii_ratio
      ,3600 * DEGREES(2 * ASIN(SQRT(POWER((COS(RADIANS(x1.decl)) * COS(RADIANS(x1.ra))
                                          - COS(RADIANS(21.521663889)) * COS(RADIANS(161.208329167))
                                         ), 2)
                                   + POWER((COS(RADIANS(x1.decl)) * SIN(RADIANS(x1.ra))
                                          - COS(RADIANS(21.521663889)) * SIN(RADIANS(161.208329167))
                                          ), 2)
                                   + POWER((SIN(RADIANS(x1.decl))
                                           - SIN(RADIANS(21.521663889))
                                          ), 2)
                                   ) / 2)) AS grb_dist_arcsec
  from assoccatsources
      ,catalogedsources c1
      ,extractedsources x1
      ,images 
 where xtrsrc_id = xtrsrcid 
   and image_id = imageid 
   and ds_id = 18 
   and assoc_catsrc_id = catsrcid 
   and cat_id = 3 
   and assoc_lr > 3 
   and assoc_r < 1 
order by grb_dist_arcsec desc 
limit 10
;

