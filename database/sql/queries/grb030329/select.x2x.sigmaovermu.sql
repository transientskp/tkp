/*s over Ibar for single band (14) */
SELECT ax1.xtrsrc_id 
      ,count(*) as datapoints 
      ,1000 * min(x2.i_int) as min_i_int_mJy 
      ,1000 * avg(x2.i_int) as avg_i_int_mJy 
      ,1000 * max(x2.i_int) as max_i_int_mJy 
      ,sqrt(count(*) * (avg(x2.i_int * x2.i_int) - avg(x2.i_int) * avg(x2.i_int))/ (count(*)
-1))/avg(x2.i_int) as sigma_over_mu 
  FROM assocxtrsources ax1 
      ,extractedsources x1 
      ,extractedsources x2 
      ,images im1 
      ,images im2
 WHERE ax1.xtrsrc_id = x1.xtrsrcid 
   AND ax1.assoc_xtrsrc_id = x2.xtrsrcid 
   AND x1.image_id = im1.imageid 
   AND x2.image_id = im2.imageid 
   AND im1.ds_id = 45
   AND im1.band = 14
   AND im2.band = 14
GROUP BY ax1.xtrsrc_id 
HAVING COUNT(*) > 5
ORDER BY sigma_over_mu
;

select * 
  from (
SELECT ax1.xtrsrc_id 
      ,im2.band as band2
      ,count(*) as datapoints 
      /*,1000 * min(x2.i_int) as min_i_int_mJy 
      ,1000 * avg(x2.i_int) as avg_i_int_mJy 
      ,1000 * max(x2.i_int) as max_i_int_mJy */
      ,sqrt(count(*) * (avg(x2.i_int * x2.i_int) - avg(x2.i_int) * avg(x2.i_int))/ (count(*)-1))/avg(x2.i_int) as sigma_over_mu 
  FROM assocxtrsources ax1 
      ,extractedsources x1 
      ,extractedsources x2 
      ,images im1 
      ,images im2
 WHERE ax1.xtrsrc_id = x1.xtrsrcid 
   AND ax1.assoc_xtrsrc_id = x2.xtrsrcid 
   AND x1.image_id = im1.imageid 
   AND x2.image_id = im2.imageid 
   AND im1.ds_id = 45
   AND im1.band <> 17
   AND im2.band <> 17
GROUP BY ax1.xtrsrc_id 
        ,im2.band
having count(*) > 1
       ) t1
 where t1.sigma_over_mu > 0.2
ORDER BY t1.xtrsrc_id
        ,t1.band2
        ,t1.sigma_over_mu
;

SELECT ax1.xtrsrc_id 
      ,im2.band as band2
      ,count(*) as datapoints 
      /*,1000 * min(x2.i_int) as min_i_int_mJy 
      ,1000 * avg(x2.i_int) as avg_i_int_mJy 
      ,1000 * max(x2.i_int) as max_i_int_mJy */
      ,sqrt(count(*) * (avg(x2.i_int * x2.i_int) - avg(x2.i_int) * avg(x2.i_int))/ (count(*)-1))/avg(x2.i_int) as sigma_over_mu 
  FROM assocxtrsources ax1 
      ,extractedsources x1 
      ,extractedsources x2 
      ,images im1 
      ,images im2
 WHERE ax1.xtrsrc_id = x1.xtrsrcid 
   AND ax1.assoc_xtrsrc_id = x2.xtrsrcid 
   AND x1.image_id = im1.imageid 
   AND x2.image_id = im2.imageid 
   AND im1.ds_id = 45
   AND im1.band <> 17
   AND im2.band <> 17
GROUP BY ax1.xtrsrc_id 
        ,im2.band
having count(*) > 1
ORDER BY ax1.xtrsrc_id
        ,im2.band
;



/*s over Ibar for single band (14) */
SELECT ax1.xtrsrc_id 
      ,count(*) as datapoints 
      ,1000 * min(x2.i_int) as min_i_int_mJy 
      ,1000 * avg(x2.i_int) as avg_i_int_mJy 
      ,1000 * max(x2.i_int) as max_i_int_mJy 
      ,sqrt(count(*) * (avg(x2.i_int * x2.i_int) - avg(x2.i_int) * avg(x2.i_int))/ (count(*)
-1))/avg(x2.i_int) as sigma_over_mu 
  FROM assocxtrsources ax1 
      ,extractedsources x1 
      ,extractedsources x2 
      ,images im1 
      ,images im2
 WHERE ax1.xtrsrc_id = x1.xtrsrcid 
   AND ax1.assoc_xtrsrc_id = x2.xtrsrcid 
   AND x1.image_id = im1.imageid 
   AND x2.image_id = im2.imageid 
   AND im1.ds_id = 45
   AND im1.band = 14
   AND im2.band = 14
GROUP BY ax1.xtrsrc_id 
HAVING COUNT(*) > 5
ORDER BY sigma_over_mu
;













select ac1.*
      ,x1.image_id
      ,im1.band 
  from assocxtrsources ac1
      ,extractedsources x1
      ,images im1 
 where image_id = imageid 
   and assoc_xtrsrc_id = xtrsrcid 
   and xtrsrc_id in (select xtrsrc_id 
                       from assocxtrsources ac2
                           ,extractedsources x2
                           ,images im2
                      where image_id = imageid 
                        and assoc_xtrsrc_id = xtrsrcid  
                        and im2.band = 14 
                     group by xtrsrc_id 
                     having count(*) = 10
                    ) 
   and im1.band = 14 
order by xtrsrc_id
        ,assoc_xtrsrc_id
;




SELECT t.xtrsrc_id 
      ,t.sigma_over_mu 
  FROM (SELECT ax1.xtrsrc_id 
              ,sqrt(count(*) * (avg(x2.i_int * x2.i_int) - avg(x2.i_int) * avg(x2.i_int))/ (count(*)-1)) /avg(x2.i_int) as sigma_over_mu 
          FROM assocxtrsources ax1 
              ,extractedsources x1 
              ,extractedsources x2 
              ,images im1 
              ,images im2
         WHERE ax1.xtrsrc_id = x1.xtrsrcid 
           AND ax1.assoc_xtrsrc_id = x2.xtrsrcid 
           AND x1.image_id = im1.imageid 
           AND x2.image_id = im2.imageid 
           AND im1.ds_id = 37
           AND im1.band = im2.band
           AND im2.band = 14
        GROUP BY ax1.xtrsrc_id 
        having count(*) = 10
       ) t 
 WHERE t.sigma_over_mu = (SELECT MAX(t0.sigma_over_mu) 
                            FROM (SELECT sqrt(count(*) * (avg(x2.i_int * x2.i_int) - avg(x2.i_int) * avg(x2.i_int)) / (count(*) - 1)) / avg(x2.i_int) AS sigma_over_mu 
                                    FROM assocxtrsources ax1 
                                        ,extractedsources x1 
                                        ,extractedsources x2 
                                        ,images im1 
                                        ,images im2
                                   WHERE ax1.xtrsrc_id = x1.xtrsrcid 
                                     AND ax1.assoc_xtrsrc_id = x2.xtrsrcid 
                                     AND x1.image_id = im1.imageid 
                                     AND x2.image_id = im2.imageid 
                                     AND im1.ds_id = 37
                                     AND im1.band = im2.band
                                     AND im2.band = 14
                                  GROUP BY ax1.xtrsrc_id 
                                  having count(*) = 10
                                 ) t0 
                         )
;




select t1.xtrsrc_id 
from (select xtrsrc_id,im1.imageid,im1.band,assoc_xtrsrc_id,im2.imageid,im2.band 
        from assocxtrsources
            ,extractedsources x1
            ,extractedsources x2
            ,images im1
            ,images im2 
       where xtrsrc_id = x1.xtrsrcid 
         and x1.image_id = im1.imageid 
         and assoc_xtrsrc_id = x2.xtrsrcid 
         and x2.image_id = im2.imageid 
         and im1.band = im2.band 
         and im1.band = 14
     ) t1 
group by t1.xtrsrc_id 
having count(*) > 9
















select ac1.*
      ,x1.image_id
      ,im1.band 
  from assocxtrsources ac1
      ,extractedsources x1
      ,images im1 
 where image_id = imageid 
   and assoc_xtrsrc_id = xtrsrcid 
   and xtrsrc_id in (select xtrsrc_id 
                       from assocxtrsources ac1
                           ,extractedsources x1
                           ,images im1 
                      where image_id = imageid 
                        and assoc_xtrsrc_id = xtrsrcid  
                        and im1.band = 14 
                     group by xtrsrc_id 
                     having count(*) = 10
                    ) 
   and im1.band = 14 
order by xtrsrc_id
        ,assoc_xtrsrc_id
;

--DROP PROCEDURE AssocXSrc2XSrc;

/*+------------------------------------------------------------------+
 *| This procedure runs the source association algorithm.            |
 *| It takes an imageid AS input argument and checks whether all the |
 *| sources that were detected in this image have candidate          |
 *| association sources. These candidate are only searched in the    |
 *| images that belong to the same dataset (ds_id) AS the input      |
 *| image.                                                           |
 *| Then, every source in the input image is processed AS follows:   |
 *| (1) a search area of radius itheta [deg] is set around the source|
 *| (2) the other images are looked up for candidate sources that    |
 *|     fall in this area (there may be none, one or many candidates)|
 *| (3) THEN we check these candidates.                              |
 *|     a. Do they also have associations                            |
 *|     b. If so, do these associations also fall in the search area |
 *| (4) for every source-candidate pair the association parameters   |
 *|     are calculated (assoc_distance_arcsec, assoc_r, assoc_lr,    |
 *|     the distance in arcsec, the dimensionless position           |
 *|     difference, and the log of the likelihood ratio, resp.)      |
 *| (5) The pair is added to the associatedsources table, which      |
 *|     can be queried AS a light curve table.                       |
 *+------------------------------------------------------------------+
 *| Bart Scheers, 2010-03-30                                         |
 *+------------------------------------------------------------------+
 *|                                                                  |
 *+------------------------------------------------------------------+
 */
CREATE PROCEDURE AssocXSrc2XSrc(iimageid INT)

BEGIN

  DECLARE izoneheight, itheta, N_density DOUBLE;
  
  SELECT zoneheight 
    INTO izoneheight
    FROM zoneheight
  ;
  SET itheta = 0.025;
  /*SET N_density = getSkyDensity_deg2(1400, 0.0021);*/
  SET N_density = 4.02439375E-06; /*NVSS density */

  /* Here we insert the sources that coud be associated */
  INSERT INTO assocxtrsources
    (xtrsrc_id
    ,assoc_xtrsrc_id
    ,assoc_weight
    ,assoc_distance_arcsec
    ,assoc_lr_method
    ,assoc_r
    ,assoc_lr
    )
    SELECT ut.xtrsrc_id
          ,ut.assoc_xtrsrc_id
          ,ut.assoc_weight
          ,ut.assoc_distance_arcsec
          ,ut.assoc_lr_method
          ,ut.assoc_r
          ,ut.assoc_lr 
      FROM (SELECT t2.xtrsrc_id 
                  ,t2.assoc_xtrsrc_id 
                  ,1 AS assoc_weight 
                  ,t2.assoc_distance_arcsec 
                  ,4 AS assoc_lr_method 
                  ,t2.assoc_distance_arcsec / SQRT(t2.sigma_ra_squared + t2.sigma_decl_squared) AS assoc_r 
                  ,LOG10(EXP(-t2.assoc_distance_arcsec * t2.assoc_distance_arcsec 
                            / (2 * (t2.sigma_ra_squared + t2.sigma_decl_squared))
                            ) 
                        / (2 * PI() * SQRT(t2.sigma_ra_squared) * SQRT(t2.sigma_decl_squared) * N_density)
                        ) AS assoc_lr
              FROM (SELECT t1.xtrsrc_id 
                          ,t1.assoc_xtrsrc_id 
                          ,3600 * DEGREES(2 * ASIN(SQRT( (t1.assoc_xtrsrc_id_x - t1.xtrsrc_id_x) 
                                                         * (t1.assoc_xtrsrc_id_x - t1.xtrsrc_id_x) 
                                                       + (t1.assoc_xtrsrc_id_y - t1.xtrsrc_id_y) 
                                                         * (t1.assoc_xtrsrc_id_y - t1.xtrsrc_id_y) 
                                                       + (t1.assoc_xtrsrc_id_z - t1.xtrsrc_id_z) 
                                                         * (t1.assoc_xtrsrc_id_z - t1.xtrsrc_id_z) 
                                                       ) 
                                                  / 2
                                                  )
                                         ) AS assoc_distance_arcsec
                          ,t1.assoc_xtrsrc_id_ra_err * t1.assoc_xtrsrc_id_ra_err 
                           + t1.xtrsrc_id_ra_err * t1.xtrsrc_id_ra_err AS sigma_ra_squared 
                          ,t1.assoc_xtrsrc_id_decl_err * t1.assoc_xtrsrc_id_decl_err 
                           + t1.xtrsrc_id_decl_err * t1.xtrsrc_id_decl_err AS sigma_decl_squared 
                      FROM (SELECT CASE WHEN x3.x * x1.x + x3.y * x1.y + x3.z * x1.z > COS(RADIANS(itheta)) 
                                        THEN x3.xtrsrcid 
                                        ELSE x2.xtrsrcid 
                                   END AS xtrsrc_id 
                                  ,CASE WHEN x3.x * x1.x + x3.y * x1.y + x3.z * x1.z > COS(RADIANS(itheta)) 
                                        THEN x3.ra 
                                        ELSE x2.ra 
                                   END AS xtrsrc_id_ra 
                                  ,CASE WHEN x3.x * x1.x + x3.y * x1.y + x3.z * x1.z > COS(RADIANS(itheta)) 
                                        THEN x3.decl 
                                        ELSE x2.decl 
                                   END AS xtrsrc_id_decl 
                                  ,CASE WHEN x3.x * x1.x + x3.y * x1.y + x3.z * x1.z > COS(RADIANS(itheta)) 
                                        THEN x3.ra_err 
                                        ELSE x2.ra_err 
                                   END AS xtrsrc_id_ra_err 
                                  ,CASE WHEN x3.x * x1.x + x3.y * x1.y + x3.z * x1.z > COS(RADIANS(itheta)) 
                                        THEN x3.decl_err 
                                        ELSE x2.decl_err 
                                   END AS xtrsrc_id_decl_err 
                                  ,CASE WHEN x3.x * x1.x + x3.y * x1.y + x3.z * x1.z > COS(RADIANS(itheta)) 
                                        THEN x3.x 
                                        ELSE x2.x 
                                   END AS xtrsrc_id_x 
                                  ,CASE WHEN x3.x * x1.x + x3.y * x1.y + x3.z * x1.z > COS(RADIANS(itheta)) 
                                        THEN x3.y 
                                        ELSE x2.y 
                                   END AS xtrsrc_id_y 
                                  ,CASE WHEN x3.x * x1.x + x3.y * x1.y + x3.z * x1.z > COS(RADIANS(itheta)) 
                                        THEN x3.z 
                                        ELSE x2.z 
                                   END AS xtrsrc_id_z 
                                  ,x1.xtrsrcid AS assoc_xtrsrc_id 
                                  ,x1.ra AS assoc_xtrsrc_id_ra 
                                  ,x1.decl AS assoc_xtrsrc_id_decl 
                                  ,x1.ra_err AS assoc_xtrsrc_id_ra_err 
                                  ,x1.decl_err AS assoc_xtrsrc_id_decl_err 
                                  ,x1.x AS assoc_xtrsrc_id_x 
                                  ,x1.y AS assoc_xtrsrc_id_y 
                                  ,x1.z AS assoc_xtrsrc_id_z 
                              FROM extractedsources x1 
                                  ,images im1 
                                  ,assocxtrsources a1 
                                  ,extractedsources x2 
                                  ,images im2 
                                  ,extractedsources x3 
                             WHERE x1.image_id = iimageid 
                               AND x1.image_id = im1.imageid 
                               AND im1.ds_id = (SELECT im11.ds_id 
                                                  FROM images im11 
                                                 WHERE im11.imageid = iimageid 
                                               ) 
                               AND a1.assoc_xtrsrc_id = x2.xtrsrcid 
                               AND a1.xtrsrc_id = x3.xtrsrcid 
                               AND x2.image_id = im2.imageid 
                               AND im1.ds_id = im2.ds_id 
                               AND x2.zone BETWEEN CAST(FLOOR((x1.decl - itheta) / izoneheight) AS INTEGER) 
                                               AND CAST(FLOOR((x1.decl + itheta) / izoneheight) AS INTEGER) 
                               AND x2.ra BETWEEN x1.ra - alpha(itheta,x1.decl) 
                                             AND x1.ra + alpha(itheta,x1.decl) 
                               AND x2.decl BETWEEN x1.decl - itheta 
                                               AND x1.decl + itheta 
                               AND x2.x * x1.x + x2.y * x1.y + x2.z * x1.z > COS(RADIANS(itheta)) 
                               AND x3.zone BETWEEN CAST(FLOOR((x1.decl - itheta) / izoneheight) AS INTEGER) 
                                               AND CAST(FLOOR((x1.decl + itheta) / izoneheight) AS INTEGER) 
                               AND x3.ra BETWEEN x1.ra - alpha(itheta,x1.decl) 
                                             AND x1.ra + alpha(itheta,x1.decl) 
                               AND x3.decl BETWEEN x1.decl - itheta 
                                               AND x1.decl + itheta 
                           ) t1 
                   ) t2 
            UNION 
            SELECT x1.xtrsrcid AS xtrsrc_id 
                  ,x1.xtrsrcid AS assoc_xtrsrc_id 
                  ,2 AS assoc_weight 
                  ,0 AS assoc_distance_arcsec 
                  ,4 AS assoc_lr_method 
                  ,0 AS assoc_r 
                  ,LOG10(1 / (4 * pi() * x1.ra_err * x1.decl_err * N_density)) AS assoc_lr 
              FROM extractedsources x1 
             WHERE x1.image_id = iimageid 
               AND x1.xtrsrcid NOT IN (SELECT x3.xtrsrcid 
                                         FROM extractedsources x3 
                                             ,images im4 
                                             ,assocxtrsources a2 
                                             ,extractedsources x4 
                                             ,images im5 
                                        WHERE x3.image_id = iimageid 
                                          AND x3.image_id = im4.imageid 
                                          AND im4.ds_id = (SELECT im6.ds_id 
                                                             FROM images im6 
                                                            WHERE im6.imageid = iimageid 
                                                          ) 
                                          AND a2.xtrsrc_id = x4.xtrsrcid 
                                          AND x4.image_id = im5.imageid 
                                          AND im5.ds_id = im4.ds_id 
                                          AND x4.zone BETWEEN CAST(FLOOR((x3.decl - itheta) / izoneheight) AS INTEGER) 
                                                          AND CAST(FLOOR((x3.decl + itheta) / izoneheight) AS INTEGER) 
                                          AND x4.ra BETWEEN x3.ra - alpha(itheta,x3.decl) 
                                                        AND x3.ra + alpha(itheta,x3.decl) 
                                          AND x4.decl BETWEEN x3.decl - itheta 
                                                          AND x3.decl + itheta 
                                          AND x3.x * x4.x + x3.y * x4.y + x3.z * x4.z > COS(RADIANS(itheta)) 
                                      ) 
           ) ut
  ;

END;

