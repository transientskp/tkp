/* de Ruiter Algo: */

select *
      ,exp(-pi()*t.assoc_distance_arcsec*t.assoc_distance_arcsec*53/(3600*3600)) as p_nrao
      ,exp(-pi()*t.r*t.r*t.sigma_sq*54/(3600*3600)) as p_sutherland,t.r*exp(-t.r*t.r/2) as p_deruiter
      ,exp(-t.assoc_distance_arcsec*t.assoc_distance_arcsec/(2*t.sigma_sq))/(2*pi()*t.sigma_sq) as p_condon 
  from (select ac1.xtrsrc_id
              ,ac1.assoc_catsrc_id
              ,ac1.assoc_distance_arcsec
              ,(x1.ra_err)*(x1.ra_err)+(c1.ra_err)*(c1.ra_err) + (x1.decl_err)*(x1.decl_err)+(c1.decl_err)*(c1.decl_err) as sigma_sq
              ,sqrt(3600*3600*alpha(x1.ra - c1.ra,x1.decl) * alpha(x1.ra - c1.ra,x1.decl)/((x1.ra_err)*(x1.ra_err)+(c1.ra_err)*(c1.ra_err)) + 3600*3600*(x1.decl-c1.decl)*(x1.decl-c1.decl)/((x1.decl_err)*(x1.decl_err)+(c1.decl_err)*(c1.decl_err))) as r 
          from assoccatsources ac1
              ,extractedsources x1
              ,catalogedsources c1 
         where xtrsrc_id = xtrsrcid 
           and assoc_catsrc_id = catsrcid
       ) t 
order by t.xtrsrc_id
        ,t.assoc_catsrc_id
;




select sqrt(sum((t1.ra-t2.ra_avg)*(t1.ra-t2.ra_avg))/sum(1))  as standard_deviation 
from (select ra as ra 
        from extractedsources,assocxtrsources 
       where assoc_xtrsrc_id = xtrsrcid and xtrsrc_id = 4) t1
    ,(select avg(ra) as ra_avg 
        from extractedsources,assocxtrsources 
       where assoc_xtrsrc_id = xtrsrcid and xtrsrc_id = 4) t2
;

+------------------------+
| sqrt_sql_div_L23       |
+========================+
| 0.00011098378788518954 |
+------------------------+

/*
Or various equivalent forms of std can be choosen,
this eases the query, but makes the result less significant.
*/

select sqrt((sum(ra*ra)-sum(ra)*sum(ra)/sum(1))/sum(1)) from extractedsources,assocxtrsources where assoc_xtrsrc_id = xtrsrcid and xtrsrc_id = 4;

or 

select sqrt(sum(ra*ra)/sum(1)-avg(ra)*avg(ra)) from extractedsources,assocxtrsources where assoc_xtrsrc_id = xtrsrcid and xtrsrc_id = 4;

+------------------------+
| sql_sub_sql_div_L22    |
+========================+
| 0.00011098736973553585 |
+------------------------+

Compare this with top value.
