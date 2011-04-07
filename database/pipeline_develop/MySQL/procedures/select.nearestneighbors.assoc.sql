SELECT xtrsrc_id
      ,getnearestneighborincat('NVSS',1,xtrsrc_id) AS nearest_nvss_neighbor
      ,getdistancearcsec(x1.ra,x1.decl,c1.ra,c1.decl) AS dist_arcsec
      ,(x1.ra+c1.ra)/2 AS avg_ra
      ,(x1.decl+c1.decl)/2 AS avg_decl
      ,sqrt((x1.ra_err*x1.ra_err)+(c1.ra_err*c1.ra_err)) AS avg_ra_err
      ,sqrt((x1.decl_err*x1.decl_err)+(c1.decl_err*c1.decl_err)) AS avg_decl_err
      ,sqrt((x1.ra_err*x1.ra_err)+(c1.ra_err*c1.ra_err)+(x1.decl_err*x1.decl_err)+(c1.decl_err*c1.decl_err)) AS avg_radius
      ,getdistancearcsec(x1.ra,x1.decl,c1.ra,c1.decl) / sqrt((x1.ra_err*x1.ra_err)+(c1.ra_err*c1.ra_err)+(x1.decl_err*x1.decl_err)+(c1.decl_err*c1.decl_err)) AS assoc_sigma 
  from associatedsources
      ,extractedsources x1
      ,catalogedsources c1 
 where xtrsrcid = xtrsrc_id 
   and catsrcid = getnearestneighborincat('NVSS',1,xtrsrc_id) 
order by xtrsrc_id
;

