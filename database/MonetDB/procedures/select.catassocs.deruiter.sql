/* Here we describe the sequence of actions taken on the sample of 
 * extracted sources to evaluate possible association with the
 * cataloged sources
 */

DECLARE izoneheight, itheta, N_density_avg DOUBLE;
DECLARE iimageid INT;

SET izoneheight = 1;
SET iimageid = 1;

/* select the number of extractedsources in the image */
SELECT COUNT(*) AS N_xtr
  FROM extractedsources
 WHERE image_id = iimageid
;

/* select the number of catalogedsources that fall into the image regions */
SELECT c1.cat_id
      ,COUNT(*) AS N_cat
  FROM catalogedsources c1
 WHERE c1.zone BETWEEN CAST(FLOOR(20.75 / izoneheight) AS INTEGER)
                   AND CAST(FLOOR(22.3 / izoneheight) AS INTEGER)
   AND c1.ra BETWEEN 160.3 AND 161.85
   AND c1.decl BETWEEN 20.75 AND 22.3
GROUP BY c1.cat_id
;

/* If we take the cartesian product of the two samples we get the
 * the number of source pairs that need to be evaluated (N_xtr * N_cat)
 * for possible associations.
 */
SELECT c1.cat_id
      ,COUNT(*) AS "Cart_product"
  FROM extractedsources x1
      ,catalogedsources c1
      ,catalogs c
 WHERE x1.image_id = iimageid
   AND c1.cat_id = c.catid
   AND c1.zone BETWEEN CAST(FLOOR(20.75 / izoneheight) AS INTEGER)
                   AND CAST(FLOOR(22.3 / izoneheight) AS INTEGER)
   AND c1.ra BETWEEN 160.3 AND 161.85
   AND c1.decl BETWEEN 20.75 AND 22.3
GROUP BY c1.cat_id
;

/* Of course we can reduce this number by just selecting the cataloged sources
 * (the candidates) that are in a small area (radius = 90" = 0.025 deg) around
 * each extractedsource.
 * NOTE:
 * Instead of the simpler cosine expression, we might use the more significant sine
 * AND SQRT(POWER((c1.x - x1.x), 2) + POWER((c1.y - x1.y), 2) + POWER((c1.z - x1.z), 2)) / 2 < SIN(RADIANS(itheta) / 2)
 */
SET itheta = 0.025;

SELECT c1.cat_id
      ,COUNT(*) AS N_to_be_evald
  FROM extractedsources x1
      ,catalogedsources c1
      ,catalogs c
 WHERE x1.image_id = iimageid
   AND c1.cat_id = c.catid
   AND c1.zone BETWEEN CAST(FLOOR((x1.decl - itheta) / izoneheight) AS INTEGER)
                   AND CAST(FLOOR((x1.decl + itheta) / izoneheight) AS INTEGER)
   AND c1.ra BETWEEN x1.ra - alpha(itheta,x1.decl)
                 AND x1.ra + alpha(itheta,x1.decl)
   AND c1.decl BETWEEN x1.decl - itheta
                   AND x1.decl + itheta
   AND c1.x * x1.x + c1.y * x1.y + c1.z * x1.z > COS(RADIANS(itheta))
GROUP BY c1.cat_id
;

/* For these N_to_be_evald sources we calculate the distances */
SELECT *
  FROM (SELECT x1.xtrsrcid
              ,c.catname
              ,c1.catsrcid
              ,3600 * DEGREES(2 * ASIN(SQRT(POWER(c1.x - x1.x, 2)
                                           + POWER(c1.y - x1.y, 2)
                                           + POWER(c1.z - x1.z, 2)
                                           ) / 2)
                             ) AS assoc_distance_arcsec
          FROM extractedsources x1
              ,catalogedsources c1
              ,catalogs c
         WHERE x1.image_id = iimageid
           AND c1.cat_id = c.catid
           AND c1.zone BETWEEN CAST(FLOOR((x1.decl - itheta) / izoneheight) AS INTEGER)
                           AND CAST(FLOOR((x1.decl + itheta) / izoneheight) AS INTEGER)
           AND c1.ra BETWEEN x1.ra - alpha(itheta,x1.decl)
                         AND x1.ra + alpha(itheta,x1.decl)
           AND c1.decl BETWEEN x1.decl - itheta
                           AND x1.decl + itheta
           AND c1.x * x1.x + c1.y * x1.y + c1.z * x1.z > COS(RADIANS(itheta))
       ) t
ORDER BY t.assoc_distance_arcsec
;

/* De Ruiter uses r, dp(r|c) and dp(r|id) to determine the LR value of the assoc */
SET N_density_avg = 54;
SELECT *
  FROM (SELECT x1.xtrsrcid AS xtrsrcid
              ,c.catname AS catname
              ,c1.catsrcid AS catsrcid
              ,3600 * DEGREES(2 * ASIN(SQRT(POWER(c1.x - x1.x, 2)
                                           + POWER(c1.y - x1.y, 2)
                                           + POWER(c1.z - x1.z, 2)
                                           ) / 2)
                             ) AS assoc_distance_arcsec
              ,3600 * SQRT( (alpha((x1.ra-c1.ra),x1.decl) * alpha((x1.ra-c1.ra),x1.decl))
                            / ((x1.ra_err)*(x1.ra_err) + (c1.ra_err)*(c1.ra_err)) 
                          + ((x1.decl-c1.decl) * (x1.decl-c1.decl))
                            / ((x1.decl_err)*(x1.decl_err) + (c1.decl_err)*(c1.decl_err))
                          ) AS assoc_r_deruiter
              ,PI() * (SQRT((x1.ra_err) * (x1.ra_err) + (c1.ra_err) * (c1.ra_err)) / 3600)
                    * (SQRT((x1.decl_err) * (x1.decl_err) + (c1.decl_err) * (c1.decl_err)) / 3600)
                    * N_density_avg AS lambda
              ,(1 / (2 * PI() * (SQRT((x1.ra_err) * (x1.ra_err) + (c1.ra_err) * (c1.ra_err)) / 3600)
                              * (SQRT((x1.decl_err) * (x1.decl_err) + (c1.decl_err) * (c1.decl_err)) / 3600)
                              * N_density_avg))
               * EXP((3600 * SQRT( (alpha((x1.ra-c1.ra),x1.decl) * alpha((x1.ra-c1.ra),x1.decl))
                                   / ((x1.ra_err)*(x1.ra_err) + (c1.ra_err)*(c1.ra_err))
                                 + ((x1.decl-c1.decl) * (x1.decl-c1.decl))
                                   / ((x1.decl_err)*(x1.decl_err) + (c1.decl_err)*(c1.decl_err))
                                 )) 
                     * 
                     (3600 * SQRT( (alpha((x1.ra-c1.ra),x1.decl) * alpha((x1.ra-c1.ra),x1.decl))
                                   / ((x1.ra_err)*(x1.ra_err) + (c1.ra_err)*(c1.ra_err))
                                 + ((x1.decl-c1.decl) * (x1.decl-c1.decl))
                                   / ((x1.decl_err)*(x1.decl_err) + (c1.decl_err)*(c1.decl_err))
                                 )) 
                     * 
                     (2 * PI() * (SQRT((x1.ra_err) * (x1.ra_err) + (c1.ra_err) * (c1.ra_err)) / 3600)
                               * (SQRT((x1.decl_err) * (x1.decl_err) + (c1.decl_err) * (c1.decl_err)) / 3600)
                               * N_density_avg - 1) 
                     / 
                     2
                    ) AS LR_deruiter
          FROM extractedsources x1
              ,catalogedsources c1
              ,catalogs c
         WHERE x1.image_id = iimageid
           AND c1.cat_id = c.catid
           AND c1.zone BETWEEN CAST(FLOOR((x1.decl - itheta) / izoneheight) AS INTEGER)
                           AND CAST(FLOOR((x1.decl + itheta) / izoneheight) AS INTEGER)
           AND c1.ra BETWEEN x1.ra - alpha(itheta,x1.decl)
                         AND x1.ra + alpha(itheta,x1.decl)
           AND c1.decl BETWEEN x1.decl - itheta
                           AND x1.decl + itheta
           AND c1.x * x1.x + c1.y * x1.y + c1.z * x1.z > COS(RADIANS(itheta))
       ) t
ORDER BY t.xtrsrcid
;

/* Depending on the value of LR_deruiter we decide to reject or adopt an association */


