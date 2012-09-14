select *,3600 * DEGREES(2 * ASIN(SQRT((x2.x - c1.x) * (x2.x - c1.x)+ (x2.y - c1.y) * (x2.y - c1.y)+ (x2.z - c1.z) * (x2.z - c1.z)) / 2) ) as grb_dist from assocxtrsources,extractedsources x2,catalogedsources c1 where catsrcid = 2071217 and assoc_xtrsrc_id = xtrsrcid and (xtrsrc_id = 2146059 or assoc_xtrsrc_id = 2146059);


select 3600 * DEGREES(2 * ASIN(SQRT((x2.x - x1.x) * (x2.x - x1.x)+ (x2.y - x1.y) * (x2.y - x1.y)+ (x2.z - x1.z) * (x2.z - x1.z)) / 2) ) as dist, 3600 * DEGREES(2 * ASIN(SQRT((x2.x - x1.x) * (x2.x - x1.x)+ (x2.y - x1.y) * (x2.y - x1.y)+ (x2.z - x1.z) * (x2.z - x1.z)) / 2) ) / SQRT(x1.ra_err * x1.ra_err + x2.ra_err * x2.ra_err + x1.decl_err * x1.decl_err + x2.decl_err * x2.decl_err) as intersectratio,x1.ra_err,x1.decl_err,x2.ra_err,x2.decl_err,SQRT(x1.ra_err * x1.ra_err + x2.ra_err * x2.ra_err + x1.decl_err * x1.decl_err + x2.decl_err * x2.decl_err) as sigma_r  from extractedsources x1,extractedsources x2 where x1.xtrsrcid = 2143213 and x2.xtrsrcid = 2144111;

select * 
  from (
select t.srcid
      ,t.img
      ,t.band
      ,t.taustart_ts
  FROM (SELECT ax2.xtrsrc_id as srcid 
              ,im1.imageid as img
              ,im1.band as band
              ,im1.taustart_ts as taustart_ts
              ,ax2.assoc_xtrsrc_id as srcid2
              ,im2.imageid as img2
              ,im2.band as band2 
              ,im2.taustart_ts as taustart_ts2
              ,ax2.assoc_distance_arcsec
              ,ax2.assoc_lr
              ,ax2.assoc_distance_arcsec / SQRT(x1.ra_err * x1.ra_err + x2.ra_err * x2.ra_err
                                               + x1.decl_err * x1.decl_err + x2.decl_err * x2.decl_err
                                               ) as intersectratio
              ,3600 * DEGREES(2 * ASIN(SQRT((x2.x - c1.x) * (x2.x - c1.x)
                                            + (x2.y - c1.y) * (x2.y - c1.y)
                                            + (x2.z - c1.z) * (x2.z - c1.z)
                                            ) / 2) ) as grb_dist
          FROM assocxtrsources ax2 
              ,extractedsources x1 
              ,extractedsources x2 
              ,images im1 
              ,images im2
              ,catalogedsources c1
         WHERE ax2.xtrsrc_id = x1.xtrsrcid 
           AND ax2.assoc_xtrsrc_id = x2.xtrsrcid 
           AND x1.image_id = im1.imageid 
           AND x2.image_id = im2.imageid 
           and ax2.assoc_lr >= 0
           AND im1.band <> 17
           and im2.band <> 17
           AND im1.ds_id = 47
           and catsrcid = 2071217
       ) t 
 where t.grb_dist < 1
union
select t.srcid
      ,t.img
      ,t.band
      ,t.taustart_ts
  FROM (SELECT ax2.xtrsrc_id as srcid1 
              ,im1.imageid as img1
              ,im1.band as band1
              ,im1.taustart_ts as taustart_ts1
              ,ax2.assoc_xtrsrc_id as srcid
              ,im2.imageid as img
              ,im2.band as band 
              ,im2.taustart_ts as taustart_ts
              ,ax2.assoc_distance_arcsec
              ,ax2.assoc_lr
              ,ax2.assoc_distance_arcsec / SQRT(x1.ra_err * x1.ra_err + x2.ra_err * x2.ra_err
                                               + x1.decl_err * x1.decl_err + x2.decl_err * x2.decl_err
                                               ) as intersectratio
              ,3600 * DEGREES(2 * ASIN(SQRT((x2.x - c1.x) * (x2.x - c1.x)
                                            + (x2.y - c1.y) * (x2.y - c1.y)
                                            + (x2.z - c1.z) * (x2.z - c1.z)
                                            ) / 2) ) as grb_dist
          FROM assocxtrsources ax2 
              ,extractedsources x1 
              ,extractedsources x2 
              ,images im1 
              ,images im2
              ,catalogedsources c1
         WHERE ax2.xtrsrc_id = x1.xtrsrcid 
           AND ax2.assoc_xtrsrc_id = x2.xtrsrcid 
           AND x1.image_id = im1.imageid 
           AND x2.image_id = im2.imageid 
           and ax2.assoc_lr >= 0
           AND im1.band <> 17
           and im2.band <> 17
           AND im1.ds_id = 47
           and catsrcid = 2071217
       ) t 
 where t.grb_dist < 1
) t1
order by t1.band
        ,t1.taustart_ts
;
+---------+-------+-------+----------------------------+
| srcid   | img   | band  | taustart_ts                |
+=========+=======+=======+============================+
| 2143213 |  1337 |    14 | 2003-12-25 00:00:00.000000 |
| 2143262 |  1338 |    14 | 2004-01-29 00:00:00.000000 |
| 2143341 |  1339 |    14 | 2004-03-27 00:00:00.000000 |
| 2143426 |  1340 |    14 | 2004-05-19 00:00:00.000000 |
| 2143624 |  1343 |    14 | 2005-04-09 00:00:00.000000 |
| 2143693 |  1344 |    14 | 2005-12-09 00:00:00.000000 |
| 2143929 |  1347 |    15 | 2003-12-23 00:00:00.000000 |
| 2143966 |  1348 |    15 | 2004-01-30 00:00:00.000000 |
| 2144009 |  1349 |    15 | 2004-03-28 00:00:00.000000 |
| 2144064 |  1350 |    15 | 2004-05-22 00:00:00.000000 |
| 2144111 |  1351 |    15 | 2004-07-03 00:00:00.000000 |
| 2144185 |  1353 |    15 | 2005-04-10 00:00:00.000000 |
| 2145234 |  1363 |    16 | 2005-11-28 00:00:00.000000 |
+---------+-------+-------+----------------------------+
13 tuples

ds9 ../fits/GRBPBCOR_WSRT_1400_20040327.fits -regions 20100308-0807_img1337.reg -regions 20100308-0807_img1339.reg -regions 20100308-0807_img1338.reg  -regions 20100308-0807_img1344.reg  -regions 20100308-0807_img1343.reg  -regions 20100308-0807_img1340.reg  -regions 20100308-0807_img1348.reg  -regions 20100308-0807_img1347.reg  -regions 20100308-0807_img1351.reg  -regions 20100308-0807_img1350.reg  -regions 20100308-0807_img1349.reg  -regions 20100308-0807_img1363.reg  -regions 20100308-0807_img1353.reg &


order by t.srcid
        ,t.img2
        ,t.taustart_ts
;






select * from ( 
SELECT ax2.xtrsrc_id 
      ,im1.imageid as img1
      ,im1.band as band1
      ,ax2.assoc_xtrsrc_id
      ,im2.imageid as img2
      ,im2.band as band2 
      ,im2.taustart_ts
      ,ax2.assoc_distance_arcsec
      ,ax2.assoc_lr
      ,ax2.assoc_distance_arcsec / SQRT(x1.ra_err * x1.ra_err + x2.ra_err * x2.ra_err
                                       + x1.decl_err * x1.decl_err + x2.decl_err * x2.decl_err
                                       ) as intersectratio
      ,3600 * DEGREES(2 * ASIN(SQRT((x2.x - c1.x) * (x2.x - c1.x)
                                    + (x2.y - c1.y) * (x2.y - c1.y)
                                    + (x2.z - c1.z) * (x2.z - c1.z)
                                    ) / 2) ) as grb_dist
  FROM assocxtrsources ax2 
      ,extractedsources x1 
      ,extractedsources x2 
      ,images im1 
      ,images im2
      ,catalogedsources c1
 WHERE ax2.xtrsrc_id = x1.xtrsrcid 
   AND ax2.assoc_xtrsrc_id = x2.xtrsrcid 
   AND x1.image_id = im1.imageid 
   AND x2.image_id = im2.imageid 
   and ax2.assoc_lr >= 0
   AND im1.band <> 17
   and im2.band <> 17
   AND im1.ds_id = 57
   and catsrcid = 2071217
) t 
where t.grb_dist < 1
order by t.xtrsrc_id
        ,t.img2
        ,t.taustart_ts
;



ORDER BY ax2.xtrsrc_id 
        ,im2.band
        ,im2.taustart_ts
;


select getdistancexsourcesarcsec(getNearestNeighborInImage(1339,2143284),2143660);


select 3600 * DEGREES(2 * ASIN(SQRT((x2.x - x1.x) * (x2.x - x1.x)+ (x2.y - x1.y) * (x2.y - x1.y)+ (x2.z - x1.z) * (x2.z - x1.z)) / 2) ) as dist, 3600 * DEGREES(2 * ASIN(SQRT((x2.x - x1.x) * (x2.x - x1.x)+ (x2.y - x1.y) * (x2.y - x1.y)+ (x2.z - x1.z) * (x2.z - x1.z)) / 2) ) / SQRT(x1.ra_err * x1.ra_err + x2.ra_err * x2.ra_err + x1.decl_err * x1.decl_err + x2.decl_err * x2.decl_err) as intersectratio from extractedsources x1,extractedsources x2 where x1.xtrsrcid = 2143284 and x2.xtrsrcid = 2143191;



select t.*
      ,getdistancexsource2catarcsec(t.xtrsrc_id,2071217) as grb_dist 
      ,1000 * c2.i_int_avg as cat_i_avg
      ,avg_i_int_mJy / (1000 * c2.i_int_avg) as i_xtr_cat_ratio
  FROM (SELECT ax2.xtrsrc_id 
              ,im2.band
              ,count(*) as datapoints 
              ,1000 * min(x2.i_int) as min_i_int_mJy 
              ,1000 * max(x2.i_int) as max_i_int_mJy 
              ,1000 * avg(x2.i_int) as avg_i_int_mJy 
              ,sqrt(count(*) * (avg(x2.i_int * x2.i_int) - avg(x2.i_int) * avg(x2.i_int))/ (count(*)-1))/avg(x2.i_int) as sigma_over_mu 
          FROM assocxtrsources ax2 
              ,extractedsources x1 
              ,extractedsources x2 
              ,images im1 
              ,images im2
         WHERE ax2.xtrsrc_id = x1.xtrsrcid 
           AND ax2.assoc_xtrsrc_id = x2.xtrsrcid 
           AND x1.image_id = im1.imageid 
           AND x2.image_id = im2.imageid 
           and ax2.assoc_lr >= 0
           AND im1.band <> 17
           and im2.band <> 17
           AND im1.ds_id = 45
        GROUP BY ax2.xtrsrc_id 
                ,im2.band
        HAVING COUNT(*) > 1 
       ) t
      ,assoccatsources ac1 
      ,catalogedsources c2
 where t.sigma_over_mu > 0.2
   and t.datapoints > 5
   and t.xtrsrc_id = ac1.xtrsrc_id
   and ac1.assoc_catsrc_id = c2.catsrcid
ORDER BY t.xtrsrc_id 
        ,t.band
;

SELECT xtrsrc_id,COUNT(*) AS assoc_cnt FROM assocxtrsources,extractedsources,images WHERE xtrsrc_id = xtrsrcid AND image_id = imageid AND ds_id = 47 GROUP BY xtrsrc_id ;
;

