select xtrsrc_id
      ,count(*) as datapoints
      ,SUM(x2.ra / (x2.ra_err * x2.ra_err)) / SUM(1 / (x2.ra_err * x2.ra_err)) as avg_ra
      ,SUM(x2.decl / (x2.decl_err * x2.decl_err)) / SUM(1 / (x2.decl_err * x2.decl_err)) as avg_decl
      ,SQRT(1 / SUM(1 / (x2.ra_err * x2.ra_err))) as avg_ra_err
      ,SQRT(1 / SUM(1 / (x2.decl_err * x2.decl_err))) as avg_decl_err
      ,SUM(x2.i_peak / (x2.i_peak_err * x2.i_peak_err)) / SUM(1 / (x2.i_peak_err * x2.i_peak_err)) as avg_i_peak
      ,SUM(x2.i_int / (x2.i_int_err * x2.i_int_err)) / SUM(1 / (x2.i_int_err * x2.i_int_err)) as avg_i_int
      ,SQRT(count(*) * (AVG(x2.i_peak * x2.i_peak) - AVG(x2.i_peak) * AVG(x2.i_peak))/ (count(*)-1))/AVG(x2.i_peak) AS s_over_i_peak
      ,SQRT(count(*) * (AVG(x2.i_int * x2.i_int) - AVG(x2.i_int) * AVG(x2.i_int))/ (count(*)-1))/AVG(x2.i_int) AS s_over_i_int
  from assocxtrsources ax1
      ,extractedsources x1
      ,images im1
      ,extractedsources x2
 where ax1.xtrsrc_id = x1.xtrsrcid 
   and x1.image_id = im1.imageid 
   and im1.ds_id = 1 
   and ax1.assoc_xtrsrc_id = x2.xtrsrcid
group by xtrsrc_id 
order by xtrsrc_id
;

