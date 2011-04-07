select ac1.xtrsrc_id
      ,x1.image_id
      ,x1.ra
      ,x1.decl
      ,ac1.assoc_catsrc_id
      ,c1.ra
      ,c1.decl
      ,ac1.assoc_distance_arcsec
      ,sqrt(3600 * 3600 * alpha(x1.ra - c1.ra,x1.decl) 
                        * alpha(x1.ra - c1.ra,x1.decl)
                        / ((x1.ra_err)*(x1.ra_err)+(c1.ra_err)*(c1.ra_err)) 
           + 3600 * 3600 * (x1.decl-c1.decl)
                         * (x1.decl-c1.decl)
                         / ((x1.decl_err)*(x1.decl_err)+(c1.decl_err)*(c1.decl_err))
           ) as r 
  from assoccatsources ac1
      ,extractedsources x1
      ,catalogedsources c1 
 where xtrsrc_id = xtrsrcid 
   and assoc_catsrc_id = catsrcid 
order by 9 desc
;

select x1.image_id
      ,avg(sqrt(3600 * 3600 * alpha(x1.ra - c1.ra,x1.decl) 
                        * alpha(x1.ra - c1.ra,x1.decl)
                        / ((x1.ra_err)*(x1.ra_err)+(c1.ra_err)*(c1.ra_err)) 
               + 3600 * 3600 * (x1.decl-c1.decl)
                         * (x1.decl-c1.decl)
                         / ((x1.decl_err)*(x1.decl_err)+(c1.decl_err)*(c1.decl_err))
               )) as r_avg
  from assoccatsources ac1
      ,extractedsources x1
      ,catalogedsources c1 
 where xtrsrc_id = xtrsrcid 
   and assoc_catsrc_id = catsrcid 
group by x1.image_id
;


