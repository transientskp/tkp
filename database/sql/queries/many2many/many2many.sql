-- 2nd query has to run in case of identical minimal distances:
SELECT runcat
      ,xtrsrc
      ,distance_arcsec
      ,r
      ,inactive
  FROM temprunningcatalog
 WHERE inactive = FALSE 
   AND xtrsrc IN (
SELECT xtrsrc 
  FROM temprunningcatalog
 WHERE runcat IN (SELECT runcat 
                    FROM temprunningcatalog 
                   WHERE runcat IN (SELECT runcat 
                                      FROM temprunningcatalog 
                                     WHERE xtrsrc IN (SELECT xtrsrc
                                                        FROM temprunningcatalog
                                                      GROUP BY xtrsrc
                                                      HAVING COUNT(*) > 1
                                                     )
                                   ) 
                  GROUP BY runcat 
                  HAVING COUNT(*) > 1
                 ) 
   AND xtrsrc IN (SELECT xtrsrc
                    FROM temprunningcatalog
                  GROUP BY xtrsrc
                  HAVING COUNT(*) > 1
                 )
  AND inactive = FALSE
GROUP BY xtrsrc
HAVING COUNT(*) > 1
) 
ORDER BY runcat DESC
LIMIT 1
;

-- This one selects the farthest out of the many-to-may assocs
elect t1.runcat
      ,t1.xtrsrc
  from (select xtrsrc
              ,min(r) as min_r
          from temprunningcatalog 
         where runcat in (select runcat 
                            from temprunningcatalog 
                           where runcat in (select runcat 
                                              from temprunningcatalog 
                                             where xtrsrc in (select xtrsrc
                                                                from temprunningcatalog
                                                              group by xtrsrc
                                                              having count(*) > 1
                                                             )
                                           ) 
                          group by runcat 
                          having count(*) > 1
                         ) 
           and xtrsrc in (select xtrsrc
                            from temprunningcatalog
                          group by xtrsrc
                          having count(*) > 1
                         )
        group by xtrsrc
       ) t0
      ,(select runcat
              ,xtrsrc
              ,r 
          from temprunningcatalog 
         where runcat in (select runcat 
                            from temprunningcatalog 
                           where runcat in (select runcat 
                                              from temprunningcatalog 
                                             where xtrsrc in (select xtrsrc
                                                                from temprunningcatalog
                                                              group by xtrsrc
                                                              having count(*) > 1
                                                             )
                                           ) 
                          group by runcat 
                          having count(*) > 1
                         ) 
           and xtrsrc in (select xtrsrc
                            from temprunningcatalog
                          group by xtrsrc
                          having count(*) > 1
                         )
       ) t1
 where t0.xtrsrc = t1.xtrsrc
   and t0.min_r < t1.r
;

-- This query selects the many-to-many associations
elect runcat
      ,xtrsrc
      ,distance_arcsec
      ,r
  from temprunningcatalog 
 where runcat in (select runcat 
                    from temprunningcatalog 
                   where runcat in (select runcat 
                                      from temprunningcatalog 
                                     where xtrsrc in (select xtrsrc
                                                        from temprunningcatalog
                                                      group by xtrsrc
                                                      having count(*) > 1
                                                     )
                                   ) 
                  group by runcat 
                  having count(*) > 1
                 ) 
   and xtrsrc in (select xtrsrc
                    from temprunningcatalog
                  group by xtrsrc
                  having count(*) > 1
                 )
;





/*
select runcat from temprunningcatalog where runcat in (select runcat from temprunningcatalog where xtrsrc in (38,40)) group by runcat having count(*) > 1;

select t.runcat
      ,t.xtrsrc
      ,t.distance_arcsec
      ,t.r
      ,t.inactive
      ,3600 * DEGREES(2 * ASIN(SQRT( (r.x - x.x) * (r.x - x.x)
                                   + (r.y - x.y) * (r.y - x.y)
                                   + (r.z - x.z) * (r.z - x.z)
                                   ) / 2) 
                     ) AS assoc_distance_arcsec
      ,3600 * DEGREES(ACOS(r.x*x.x + r.y * x.y + r.z*x.z)) as cos_dist_as
      ,3600 * SQRT(  (r.wm_ra * COS(RADIANS(r.wm_decl)) - x.ra * COS(RADIANS(x.decl)))
                   * (r.wm_ra * COS(RADIANS(r.wm_decl)) - x.ra * COS(RADIANS(x.decl))) 
                     / (r.wm_ra_err * r.wm_ra_err + x.ra_err * x.ra_err)
                   + (r.wm_decl - x.decl) * (r.wm_decl - x.decl)
                     / (r.wm_decl_err * r.wm_decl_err + x.decl_err * x.decl_err)
                  ) AS assoc_r
  from temprunningcatalog t
      ,runningcatalog r
      ,extractedsource x
 where t.runcat = r.id
   and t.xtrsrc = x.id
   and t.runcat in (select runcat 
                    from temprunningcatalog 
                   where xtrsrc in (select xtrsrc 
                                      from temprunningcatalog 
                                    group by xtrsrc 
                                    having count(*) > 1
                                   ) 
                  group by runcat 
                  having count(*) > 1
                 ) 
order by t.xtrsrc
        ,t.runcat
;
*/
