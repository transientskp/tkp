SELECT * 
  FROM (SELECT xtrsrc_id
              ,getNearestNeighborInCat('NVSS',1,xtrsrc_id) AS nearest_nvss_neighbor
              ,3600 * DEGREES(2 * ASIN(SQRT(POWER((COS(RADIANS(x1.decl)) * COS(RADIANS(x1.ra))
                                                  - COS(RADIANS(c1.decl)) * COS(RADIANS(c1.ra))
                                                  ), 2)
                                           + POWER((COS(RADIANS(x1.decl)) * SIN(RADIANS(x1.ra))
                                                   - COS(RADIANS(c1.decl)) * SIN(RADIANS(c1.ra))
                                                   ), 2)
                                           + POWER((SIN(RADIANS(x1.decl))
                                                   - SIN(RADIANS(c1.decl))
                                                   ), 2)
                                           ) / 2)) AS dist_arcsec
              ,(x1.ra + c1.ra) / 2 AS avg_ra
              ,(x1.decl + c1.decl) / 2 AS avg_decl
              ,SQRT((x1.ra_err * x1.ra_err) 
                   + (c1.ra_err * c1.ra_err)
                   ) AS avg_ra_err
              ,SQRT((x1.decl_err * x1.decl_err) 
                   + (c1.decl_err * c1.decl_err)
                   ) AS avg_decl_err
              ,SQRT((x1.ra_err * x1.ra_err) 
                   + (c1.ra_err * c1.ra_err) 
                   + (x1.decl_err * x1.decl_err) 
                   + (c1.decl_err * c1.decl_err)
                   ) AS avg_radius
              ,3600 * DEGREES(2 * ASIN(SQRT(POWER((COS(RADIANS(x1.decl)) * COS(RADIANS(x1.ra))
                                                  - COS(RADIANS(c1.decl)) * COS(RADIANS(c1.ra))
                                                  ), 2)
                                           + POWER((COS(RADIANS(x1.decl)) * SIN(RADIANS(x1.ra))
                                                   - COS(RADIANS(c1.decl)) * SIN(RADIANS(c1.ra))
                                                   ), 2)
                                           + POWER((SIN(RADIANS(x1.decl))
                                                   - SIN(RADIANS(c1.decl))
                                                   ), 2)
                                           ) / 2))
               / SQRT((x1.ra_err * x1.ra_err)
                     + (c1.ra_err * c1.ra_err)
                     + (x1.decl_err * x1.decl_err)
                     + (c1.decl_err * c1.decl_err)
                     ) AS assoc_sigma 
          FROM associatedsources
              ,extractedsources x1
              ,catalogedsources c1 
         WHERE xtrsrcid - xtrsrc_id
           AND catsrcid = getnearestneighborincat('NVSS',1,xtrsrc_id) 
       ) t
order by t.xtrsrc_id
;

SELECT xtrsrc_id ,getNearestNeighborInCat('NVSS',1,xtrsrc_id) AS nearest_nvss_neighbor ,getDistanceArcsec(x1.ra,x1.decl,c1.ra,c1.decl) AS dist_arcsec ,(x1.ra+c1.ra)/2 AS avg_ra ,(x1.decl+c1.decl)/2 AS avg_decl ,SQRT((x1.ra_err*x1.ra_err)+(c1.ra_err*c1.ra_err)) AS avg_ra_err ,SQRT((x1.decl_err*x1.decl_err)+(c1.decl_err*c1.decl_err)) AS avg_decl_err ,SQRT((x1.ra_err*x1.ra_err)+(c1.ra_err*c1.ra_err)+(x1.decl_err*x1.decl_err)+(c1.decl_err*c1.decl_err)) AS avg_radius ,getdistancearcsec(x1.ra,x1.decl,c1.ra,c1.decl) / SQRT((x1.ra_err*x1.ra_err)+(c1.ra_err*c1.ra_err)+(x1.decl_err*x1.decl_err)+(c1.decl_err*c1.decl_err)) AS assoc_sigma FROM associatedsources ,extractedsources x1 ,catalogedsources c1  WHERE xtrsrcid = xtrsrc_id  AND catsrcid = getnearestneighborincat('NVSS',1,xtrsrc_id) ORDER BY xtrsrc_id;


