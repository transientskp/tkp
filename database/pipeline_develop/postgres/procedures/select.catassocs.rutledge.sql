/* Here we describe the sequence of actions taken on the sample of 
 * extracted sources to evaluate possible association with the
 * cataloged sources
 */

DECLARE izoneheight, itheta, N_density_avg double precision;
DECLARE iimageid INT;

SET izoneheight = 1;
SET iimageid = 1;
SET itheta = 0.025;

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

/* That's not all! 
 * In Rutlegde's method also background fields are evaluated.
 * The fields per source are offset in RA by n * (2*search radius), 
 * where n = [-5,-1] and [1,5], so per source there are 10 background fields.
 * Here we place the source at the central position in the background fields 
 * along with the catlogedsources that are actually in those background fields.
 */

/* Here we offset the sources in the source field by:
 * +1 * (2*search_radius) = 2*90 ["] = 0.05 [deg]
 * and select the catalogedsources that are in the offset fiels, 
 * i.e. the +1 background field.
 */

/* First, we select the source associations for this field 
 * that need to be evaluated.
 *
SELECT x1.xtrsrcid
      ,c.catname
      ,c1.catsrcid
      ,3600 * DEGREES(2 * ASIN(SQRT(POWER(c1.x - x1.x, 2) 
                                   + POWER(c1.y - x1.y, 2) 
                                   + POWER(c1.z - x1.z, 2)
                                   ) / 2) 
                     ) AS assoc_distance_arcsec 
  FROM (SELECT xtrsrcid AS xtrsrcid
              ,ra + alpha(1 * (2 * itheta), decl) AS ra
              ,decl AS decl
              ,COS(RADIANS(decl)) * COS(RADIANS(ra + alpha(1 * (2 * itheta), decl))) AS x
              ,COS(RADIANS(decl)) * SIN(RADIANS(ra + alpha(1 * (2 * itheta), decl))) AS y
              ,z AS z 
          FROM extractedsources xp1 
         WHERE image_id = iimageid
       ) x1
      ,catalogedsources c1
      ,catalogs c 
 WHERE c1.cat_id = c.catid 
   AND c1.zone BETWEEN CAST(FLOOR((x1.decl - itheta) / izoneheight) AS INTEGER) 
                   AND CAST(FLOOR((x1.decl + itheta) / izoneheight) AS INTEGER) 
   AND c1.ra BETWEEN x1.ra - alpha(itheta,x1.decl) 
                 AND x1.ra + alpha(itheta,x1.decl) 
   AND c1.decl BETWEEN x1.decl - itheta 
                   AND x1.decl + itheta 
   AND c1.x * x1.x + c1.y * x1.y + c1.z * x1.z > COS(RADIANS(itheta))
;

/* Here we select the absolute number of background sources in field -5 
SELECT xtrsrcid
      ,x1.ra
      ,x1.decl
      ,x1.x
      ,x1.y
      ,x1.z
      ,catsrcid
  FROM (SELECT xtrsrcid AS xtrsrcid
              ,ra + alpha(3 * (2 * itheta), decl) AS ra
              ,decl AS decl
              ,COS(RADIANS(decl)) * COS(RADIANS(ra + alpha(3 * (2 * itheta), decl))) AS x
              ,COS(RADIANS(decl)) * SIN(RADIANS(ra + alpha(3 * (2 * itheta), decl))) AS y
              ,z AS z 
          FROM extractedsources 
         WHERE image_id = iimageid
       ) x1
      ,catalogedsources c1
      ,catalogs c 
 WHERE c1.cat_id = c.catid 
   AND c1.zone BETWEEN CAST(FLOOR((x1.decl - itheta) / izoneheight) AS INTEGER) 
                   AND CAST(FLOOR((x1.decl + itheta) / izoneheight) AS INTEGER) 
   AND c1.ra BETWEEN x1.ra - alpha(itheta,x1.decl) 
                 AND x1.ra + alpha(itheta,x1.decl) 
   AND c1.decl BETWEEN x1.decl - itheta 
                   AND x1.decl + itheta 
;

SELECT COUNT(*)
  FROM extractedsources x1 
      ,catalogedsources c1
      ,catalogs c 
 WHERE c1.cat_id = c.catid
   AND x1.image_id = iimageid
   AND c1.zone BETWEEN CAST(FLOOR((x1.decl - itheta) / izoneheight) AS INTEGER) 
                   AND CAST(FLOOR((x1.decl + itheta) / izoneheight) AS INTEGER) 
   AND c1.ra BETWEEN x1.ra - alpha(itheta,x1.decl) 
                 AND x1.ra + alpha(itheta,x1.decl) 
   AND c1.decl BETWEEN x1.decl - itheta 
                   AND x1.decl + itheta 
;

SELECT COUNT(*)
  FROM (SELECT xtrsrcid AS xtrsrcid
              ,ra + alpha(3 * (2 * itheta), decl) AS ra
              ,decl AS decl
              ,COS(RADIANS(decl)) * COS(RADIANS(ra + alpha(3 * (2 * itheta), decl))) AS x
              ,COS(RADIANS(decl)) * SIN(RADIANS(ra + alpha(3 * (2 * itheta), decl))) AS y
              ,z AS z 
          FROM extractedsources 
         WHERE image_id = iimageid
       ) x1
      ,catalogedsources c1
      ,catalogs c 
 WHERE c1.cat_id = c.catid 
   AND c1.zone BETWEEN CAST(FLOOR((x1.decl - itheta) / izoneheight) AS INTEGER) 
                   AND CAST(FLOOR((x1.decl + itheta) / izoneheight) AS INTEGER) 
   AND c1.ra BETWEEN x1.ra - alpha(itheta,x1.decl) 
                 AND x1.ra + alpha(itheta,x1.decl) 
   AND c1.decl BETWEEN x1.decl - itheta 
                   AND x1.decl + itheta 
;
*/

/* Just the On-source Field */
/*
SELECT t.xtrsrcid
      ,t.catname
      ,t.catsrcid
      ,t.assoc_distance_arcsec
      ,t.sigma
      ,LOG10(EXP(-t.assoc_distance_arcsec * t.assoc_distance_arcsec / (2 * t.sigma * t.sigma)) / (t.sigma * 106)) AS LR_rutledge
  FROM (
SELECT x1.xtrsrcid
      ,c.catname
      ,c1.catsrcid
      ,3600 * DEGREES(2 * ASIN(SQRT(POWER(c1.x - x1.x, 2) + POWER(c1.y - x1.y, 2) + POWER(c1.z - x1.z, 2)) / 2) ) AS assoc_distance_arcsec
      ,SQRT((x1.ra_err)*(x1.ra_err) + (x1.decl_err)*(x1.decl_err) + (c1.ra_err)*(c1.ra_err) + (c1.decl_err)*(c1.decl_err)) AS sigma 
  FROM extractedsources x1
      ,catalogedsources c1
      ,catalogs c 
 WHERE image_id = iimageid 
   AND c1.cat_id = c.catid 
   AND c1.zone BETWEEN CAST(FLOOR((x1.decl - itheta) / izoneheight) AS INTEGER) 
                   AND CAST(FLOOR((x1.decl + itheta) / izoneheight) AS INTEGER) 
   AND c1.ra BETWEEN x1.ra - alpha(itheta,x1.decl) 
                 AND x1.ra + alpha(itheta,x1.decl) 
   AND c1.decl BETWEEN x1.decl - itheta 
                   AND x1.decl + itheta 
   AND c1.x * x1.x + c1.y * x1.y + c1.z * x1.z > COS(RADIANS(itheta))
) t
ORDER BY LR_rutledge
;
*/


/* And now we proceed by collecting them all for the on-source field and the 
 * 10 background fields as well.
 */
/*
SELECT t.BGfield
      ,t.xtrsrcid
      ,t.catname
      ,t.catsrcid
      ,t.assoc_distance_arcsec
      ,t.sigma
      ,LOG10(EXP(-t.assoc_distance_arcsec * t.assoc_distance_arcsec / (2 * t.sigma * t.sigma)) / (t.sigma * 106)) AS LR_rutledge
  FROM (
SELECT -5 AS BGfield,x1.xtrsrcid,c.catname,c1.catsrcid,3600 * DEGREES(2 * ASIN(SQRT(POWER(c1.x - x1.x, 2) + POWER(c1.y - x1.y, 2) + POWER(c1.z - x1.z, 2)) / 2) ) AS assoc_distance_arcsec, SQRT((x1.ra_err)*(x1.ra_err) + (x1.decl_err)*(x1.decl_err) + (c1.ra_err)*(c1.ra_err) + (c1.decl_err)*(c1.decl_err)) AS sigma FROM (SELECT xtrsrcid AS xtrsrcid,ra - alpha(5 * (2 * itheta), decl) AS ra,decl AS decl,ra_err AS ra_err,decl_err AS decl_err,COS(RADIANS(decl)) * COS(RADIANS(ra - alpha(5 * (2 * itheta), decl))) AS x,COS(RADIANS(decl)) * SIN(RADIANS(ra - alpha(5 * (2 * itheta), decl))) AS y,z AS z FROM extractedsources xp1 WHERE image_id = iimageid) x1,catalogedsources c1,catalogs c WHERE c1.cat_id = c.catid AND c1.zone BETWEEN CAST(FLOOR((x1.decl - itheta) / izoneheight) AS INTEGER) AND CAST(FLOOR((x1.decl + itheta) / izoneheight) AS INTEGER) AND c1.ra BETWEEN x1.ra - alpha(itheta,x1.decl) AND x1.ra + alpha(itheta,x1.decl) AND c1.decl BETWEEN x1.decl - itheta AND x1.decl + itheta AND c1.x * x1.x + c1.y * x1.y + c1.z * x1.z > COS(RADIANS(itheta))
UNION
SELECT -4 AS BGfield,x1.xtrsrcid,c.catname,c1.catsrcid,3600 * DEGREES(2 * ASIN(SQRT(POWER(c1.x - x1.x, 2) + POWER(c1.y - x1.y, 2) + POWER(c1.z - x1.z, 2)) / 2) ) AS assoc_distance_arcsec, SQRT((x1.ra_err)*(x1.ra_err) + (x1.decl_err)*(x1.decl_err) + (c1.ra_err)*(c1.ra_err) + (c1.decl_err)*(c1.decl_err)) AS sigma FROM (SELECT xtrsrcid AS xtrsrcid,ra - alpha(4 * (2 * itheta), decl) AS ra,decl AS decl,ra_err AS ra_err,decl_err AS decl_err,COS(RADIANS(decl)) * COS(RADIANS(ra - alpha(4 * (2 * itheta), decl))) AS x,COS(RADIANS(decl)) * SIN(RADIANS(ra - alpha(4 * (2 * itheta), decl))) AS y,z AS z FROM extractedsources xp1 WHERE image_id = iimageid) x1,catalogedsources c1,catalogs c WHERE c1.cat_id = c.catid AND c1.zone BETWEEN CAST(FLOOR((x1.decl - itheta) / izoneheight) AS INTEGER) AND CAST(FLOOR((x1.decl + itheta) / izoneheight) AS INTEGER) AND c1.ra BETWEEN x1.ra - alpha(itheta,x1.decl) AND x1.ra + alpha(itheta,x1.decl) AND c1.decl BETWEEN x1.decl - itheta AND x1.decl + itheta AND c1.x * x1.x + c1.y * x1.y + c1.z * x1.z > COS(RADIANS(itheta))
UNION
SELECT -3 AS BGfield,x1.xtrsrcid,c.catname,c1.catsrcid,3600 * DEGREES(2 * ASIN(SQRT(POWER(c1.x - x1.x, 2) + POWER(c1.y - x1.y, 2) + POWER(c1.z - x1.z, 2)) / 2) ) AS assoc_distance_arcsec, SQRT((x1.ra_err)*(x1.ra_err) + (x1.decl_err)*(x1.decl_err) + (c1.ra_err)*(c1.ra_err) + (c1.decl_err)*(c1.decl_err)) AS sigma FROM (SELECT xtrsrcid AS xtrsrcid,ra - alpha(3 * (2 * itheta), decl) AS ra,decl AS decl,ra_err AS ra_err,decl_err AS decl_err,COS(RADIANS(decl)) * COS(RADIANS(ra - alpha(3 * (2 * itheta), decl))) AS x,COS(RADIANS(decl)) * SIN(RADIANS(ra - alpha(3 * (2 * itheta), decl))) AS y,z AS z FROM extractedsources xp1 WHERE image_id = iimageid) x1,catalogedsources c1,catalogs c WHERE c1.cat_id = c.catid AND c1.zone BETWEEN CAST(FLOOR((x1.decl - itheta) / izoneheight) AS INTEGER) AND CAST(FLOOR((x1.decl + itheta) / izoneheight) AS INTEGER) AND c1.ra BETWEEN x1.ra - alpha(itheta,x1.decl) AND x1.ra + alpha(itheta,x1.decl) AND c1.decl BETWEEN x1.decl - itheta AND x1.decl + itheta AND c1.x * x1.x + c1.y * x1.y + c1.z * x1.z > COS(RADIANS(itheta))
UNION
SELECT -2 AS BGfield,x1.xtrsrcid,c.catname,c1.catsrcid,3600 * DEGREES(2 * ASIN(SQRT(POWER(c1.x - x1.x, 2) + POWER(c1.y - x1.y, 2) + POWER(c1.z - x1.z, 2)) / 2) ) AS assoc_distance_arcsec, SQRT((x1.ra_err)*(x1.ra_err) + (x1.decl_err)*(x1.decl_err) + (c1.ra_err)*(c1.ra_err) + (c1.decl_err)*(c1.decl_err)) AS sigma FROM (SELECT xtrsrcid AS xtrsrcid,ra - alpha(2 * (2 * itheta), decl) AS ra,decl AS decl,ra_err AS ra_err,decl_err AS decl_err,COS(RADIANS(decl)) * COS(RADIANS(ra - alpha(2 * (2 * itheta), decl))) AS x,COS(RADIANS(decl)) * SIN(RADIANS(ra - alpha(2 * (2 * itheta), decl))) AS y,z AS z FROM extractedsources xp1 WHERE image_id = iimageid) x1,catalogedsources c1,catalogs c WHERE c1.cat_id = c.catid AND c1.zone BETWEEN CAST(FLOOR((x1.decl - itheta) / izoneheight) AS INTEGER) AND CAST(FLOOR((x1.decl + itheta) / izoneheight) AS INTEGER) AND c1.ra BETWEEN x1.ra - alpha(itheta,x1.decl) AND x1.ra + alpha(itheta,x1.decl) AND c1.decl BETWEEN x1.decl - itheta AND x1.decl + itheta AND c1.x * x1.x + c1.y * x1.y + c1.z * x1.z > COS(RADIANS(itheta))
UNION
SELECT -1 AS BGfield,x1.xtrsrcid,c.catname,c1.catsrcid,3600 * DEGREES(2 * ASIN(SQRT(POWER(c1.x - x1.x, 2) + POWER(c1.y - x1.y, 2) + POWER(c1.z - x1.z, 2)) / 2) ) AS assoc_distance_arcsec, SQRT((x1.ra_err)*(x1.ra_err) + (x1.decl_err)*(x1.decl_err) + (c1.ra_err)*(c1.ra_err) + (c1.decl_err)*(c1.decl_err)) AS sigma FROM (SELECT xtrsrcid AS xtrsrcid,ra - alpha(1 * (2 * itheta), decl) AS ra,decl AS decl,ra_err AS ra_err,decl_err AS decl_err,COS(RADIANS(decl)) * COS(RADIANS(ra - alpha(1 * (2 * itheta), decl))) AS x,COS(RADIANS(decl)) * SIN(RADIANS(ra - alpha(1 * (2 * itheta), decl))) AS y,z AS z FROM extractedsources xp1 WHERE image_id = iimageid) x1,catalogedsources c1,catalogs c WHERE c1.cat_id = c.catid AND c1.zone BETWEEN CAST(FLOOR((x1.decl - itheta) / izoneheight) AS INTEGER) AND CAST(FLOOR((x1.decl + itheta) / izoneheight) AS INTEGER) AND c1.ra BETWEEN x1.ra - alpha(itheta,x1.decl) AND x1.ra + alpha(itheta,x1.decl) AND c1.decl BETWEEN x1.decl - itheta AND x1.decl + itheta AND c1.x * x1.x + c1.y * x1.y + c1.z * x1.z > COS(RADIANS(itheta))
UNION
SELECT 1 AS BGfield,x1.xtrsrcid,c.catname,c1.catsrcid,3600 * DEGREES(2 * ASIN(SQRT(POWER(c1.x - x1.x, 2) + POWER(c1.y - x1.y, 2) + POWER(c1.z - x1.z, 2)) / 2) ) AS assoc_distance_arcsec, SQRT((x1.ra_err)*(x1.ra_err) + (x1.decl_err)*(x1.decl_err) + (c1.ra_err)*(c1.ra_err) + (c1.decl_err)*(c1.decl_err)) AS sigma FROM (SELECT xtrsrcid AS xtrsrcid,ra + alpha(1 * (2 * itheta), decl) AS ra,decl AS decl,ra_err AS ra_err,decl_err AS decl_err,COS(RADIANS(decl)) * COS(RADIANS(ra + alpha(1 * (2 * itheta), decl))) AS x,COS(RADIANS(decl)) * SIN(RADIANS(ra + alpha(1 * (2 * itheta), decl))) AS y,z AS z FROM extractedsources xp1 WHERE image_id = iimageid) x1,catalogedsources c1,catalogs c WHERE c1.cat_id = c.catid AND c1.zone BETWEEN CAST(FLOOR((x1.decl - itheta) / izoneheight) AS INTEGER) AND CAST(FLOOR((x1.decl + itheta) / izoneheight) AS INTEGER) AND c1.ra BETWEEN x1.ra - alpha(itheta,x1.decl) AND x1.ra + alpha(itheta,x1.decl) AND c1.decl BETWEEN x1.decl - itheta AND x1.decl + itheta AND c1.x * x1.x + c1.y * x1.y + c1.z * x1.z > COS(RADIANS(itheta))
UNION
SELECT 2 AS BGfield,x1.xtrsrcid,c.catname,c1.catsrcid,3600 * DEGREES(2 * ASIN(SQRT(POWER(c1.x - x1.x, 2) + POWER(c1.y - x1.y, 2) + POWER(c1.z - x1.z, 2)) / 2) ) AS assoc_distance_arcsec, SQRT((x1.ra_err)*(x1.ra_err) + (x1.decl_err)*(x1.decl_err) + (c1.ra_err)*(c1.ra_err) + (c1.decl_err)*(c1.decl_err)) AS sigma FROM (SELECT xtrsrcid AS xtrsrcid,ra + alpha(2 * (2 * itheta), decl) AS ra,decl AS decl,ra_err AS ra_err,decl_err AS decl_err,COS(RADIANS(decl)) * COS(RADIANS(ra + alpha(2 * (2 * itheta), decl))) AS x,COS(RADIANS(decl)) * SIN(RADIANS(ra + alpha(2 * (2 * itheta), decl))) AS y,z AS z FROM extractedsources xp1 WHERE image_id = iimageid) x1,catalogedsources c1,catalogs c WHERE c1.cat_id = c.catid AND c1.zone BETWEEN CAST(FLOOR((x1.decl - itheta) / izoneheight) AS INTEGER) AND CAST(FLOOR((x1.decl + itheta) / izoneheight) AS INTEGER) AND c1.ra BETWEEN x1.ra - alpha(itheta,x1.decl) AND x1.ra + alpha(itheta,x1.decl) AND c1.decl BETWEEN x1.decl - itheta AND x1.decl + itheta AND c1.x * x1.x + c1.y * x1.y + c1.z * x1.z > COS(RADIANS(itheta))
UNION
SELECT 3 AS BGfield,x1.xtrsrcid,c.catname,c1.catsrcid,3600 * DEGREES(2 * ASIN(SQRT(POWER(c1.x - x1.x, 2) + POWER(c1.y - x1.y, 2) + POWER(c1.z - x1.z, 2)) / 2) ) AS assoc_distance_arcsec, SQRT((x1.ra_err)*(x1.ra_err) + (x1.decl_err)*(x1.decl_err) + (c1.ra_err)*(c1.ra_err) + (c1.decl_err)*(c1.decl_err)) AS sigma FROM (SELECT xtrsrcid AS xtrsrcid,ra + alpha(3 * (2 * itheta), decl) AS ra,decl AS decl,ra_err AS ra_err,decl_err AS decl_err,COS(RADIANS(decl)) * COS(RADIANS(ra + alpha(3 * (2 * itheta), decl))) AS x,COS(RADIANS(decl)) * SIN(RADIANS(ra + alpha(3 * (2 * itheta), decl))) AS y,z AS z FROM extractedsources xp1 WHERE image_id = iimageid) x1,catalogedsources c1,catalogs c WHERE c1.cat_id = c.catid AND c1.zone BETWEEN CAST( FLOOR((x1.decl - itheta) / izoneheight) AS INTEGER) AND CAST(FLOOR((x1.decl + itheta) / izoneheight) AS INTEGER) AND c1.ra BETWEEN x1.ra - alpha(itheta,x1.decl) AND x1.ra + alpha(itheta,x1.decl) AND c1.decl BETWEEN x1.decl - itheta AND x1.decl + itheta AND c1.x * x1.x + c1.y * x1.y + c1.z * x1.z > COS(RADIANS(itheta))
UNION
SELECT 4 AS BGfield,x1.xtrsrcid,c.catname,c1.catsrcid,3600 * DEGREES(2 * ASIN(SQRT(POWER(c1.x - x1.x, 2) + POWER(c1.y - x1.y, 2) + POWER(c1.z - x1.z, 2)) / 2) ) AS assoc_distance_arcsec, SQRT((x1.ra_err)*(x1.ra_err) + (x1.decl_err)*(x1.decl_err) + (c1.ra_err)*(c1.ra_err) + (c1.decl_err)*(c1.decl_err)) AS sigma FROM (SELECT xtrsrcid AS xtrsrcid,ra + alpha(4 * (2 * itheta), decl) AS ra,decl AS decl,ra_err AS ra_err,decl_err AS decl_err,COS(RADIANS(decl)) * COS(RADIANS(ra + alpha(4 * (2 * itheta), decl))) AS x,COS(RADIANS(decl)) * SIN(RADIANS(ra + alpha(4 * (2 * itheta), decl))) AS y,z AS z FROM extractedsources xp1 WHERE image_id = iimageid) x1,catalogedsources c1,catalogs c WHERE c1.cat_id = c.catid AND c1.zone BETWEEN CAST( FLOOR((x1.decl - itheta) / izoneheight) AS INTEGER) AND CAST(FLOOR((x1.decl + itheta) / izoneheight) AS INTEGER) AND c1.ra BETWEEN x1.ra - alpha(itheta,x1.decl) AND x1.ra + alpha(itheta,x1.decl) AND c1.decl BETWEEN x1.decl - itheta AND x1.decl + itheta AND c1.x * x1.x + c1.y * x1.y + c1.z * x1.z > COS(RADIANS(itheta))
UNION
SELECT 5 AS BGfield,x1.xtrsrcid,c.catname,c1.catsrcid,3600 * DEGREES(2 * ASIN(SQRT(POWER(c1.x - x1.x, 2) + POWER(c1.y - x1.y, 2) + POWER(c1.z - x1.z, 2)) / 2) ) AS assoc_distance_arcsec, SQRT((x1.ra_err)*(x1.ra_err) + (x1.decl_err)*(x1.decl_err) + (c1.ra_err)*(c1.ra_err) + (c1.decl_err)*(c1.decl_err)) AS sigma FROM (SELECT xtrsrcid AS xtrsrcid,ra + alpha(5 * (2 * itheta), decl) AS ra,decl AS decl,ra_err AS ra_err,decl_err AS decl_err,COS(RADIANS(decl)) * COS(RADIANS(ra + alpha(5 * (2 * itheta), decl))) AS x,COS(RADIANS(decl)) * SIN(RADIANS(ra + alpha(5 * (2 * itheta), decl))) AS y,z AS z FROM extractedsources xp1 WHERE image_id = iimageid) x1,catalogedsources c1,catalogs c WHERE c1.cat_id = c.catid AND c1.zone BETWEEN CAST( FLOOR((x1.decl - itheta) / izoneheight) AS INTEGER) AND CAST(FLOOR((x1.decl + itheta) / izoneheight) AS INTEGER) AND c1.ra BETWEEN x1.ra - alpha(itheta,x1.decl) AND x1.ra + alpha(itheta,x1.decl) AND c1.decl BETWEEN x1.decl - itheta AND x1.decl + itheta AND c1.x * x1.x + c1.y * x1.y + c1.z * x1.z > COS(RADIANS(itheta))
) t
ORDER BY xtrsrcid
        ,catsrcid
;
*/

/* And now the on-source filed included as well */
SELECT t.BGfield
      ,t.xtrsrcid
      ,t.catname
      ,t.catsrcid
      ,t.assoc_distance_arcsec
      ,t.sigma
      ,LOG10(EXP(-t.assoc_distance_arcsec * t.assoc_distance_arcsec / (2 * t.sigma * t.sigma)) / (t.sigma * 106)) AS LR_rutledge
  FROM (
SELECT -5 AS BGfield,x1.xtrsrcid,c.catname,c1.catsrcid,3600 * DEGREES(2 * ASIN(SQRT(POWER(c1.x - x1.x, 2) + POWER(c1.y - x1.y, 2) + POWER(c1.z - x1.z, 2)) / 2) ) AS assoc_distance_arcsec, SQRT((x1.ra_err)*(x1.ra_err) + (x1.decl_err)*(x1.decl_err) + (c1.ra_err)*(c1.ra_err) + (c1.decl_err)*(c1.decl_err)) AS sigma FROM (SELECT xtrsrcid AS xtrsrcid,ra - alpha(5 * (2 * itheta), decl) AS ra,decl AS decl,ra_err AS ra_err,decl_err AS decl_err,COS(RADIANS(decl)) * COS(RADIANS(ra - alpha(5 * (2 * itheta), decl))) AS x,COS(RADIANS(decl)) * SIN(RADIANS(ra - alpha(5 * (2 * itheta), decl))) AS y,z AS z FROM extractedsources xp1 WHERE image_id = iimageid) x1,catalogedsources c1,catalogs c WHERE c1.cat_id = c.catid AND c1.zone BETWEEN CAST(FLOOR((x1.decl - itheta) / izoneheight) AS INTEGER) AND CAST(FLOOR((x1.decl + itheta) / izoneheight) AS INTEGER) AND c1.ra BETWEEN x1.ra - alpha(itheta,x1.decl) AND x1.ra + alpha(itheta,x1.decl) AND c1.decl BETWEEN x1.decl - itheta AND x1.decl + itheta AND c1.x * x1.x + c1.y * x1.y + c1.z * x1.z > COS(RADIANS(itheta))
UNION
SELECT -4 AS BGfield,x1.xtrsrcid,c.catname,c1.catsrcid,3600 * DEGREES(2 * ASIN(SQRT(POWER(c1.x - x1.x, 2) + POWER(c1.y - x1.y, 2) + POWER(c1.z - x1.z, 2)) / 2) ) AS assoc_distance_arcsec, SQRT((x1.ra_err)*(x1.ra_err) + (x1.decl_err)*(x1.decl_err) + (c1.ra_err)*(c1.ra_err) + (c1.decl_err)*(c1.decl_err)) AS sigma FROM (SELECT xtrsrcid AS xtrsrcid,ra - alpha(4 * (2 * itheta), decl) AS ra,decl AS decl,ra_err AS ra_err,decl_err AS decl_err,COS(RADIANS(decl)) * COS(RADIANS(ra - alpha(4 * (2 * itheta), decl))) AS x,COS(RADIANS(decl)) * SIN(RADIANS(ra - alpha(4 * (2 * itheta), decl))) AS y,z AS z FROM extractedsources xp1 WHERE image_id = iimageid) x1,catalogedsources c1,catalogs c WHERE c1.cat_id = c.catid AND c1.zone BETWEEN CAST(FLOOR((x1.decl - itheta) / izoneheight) AS INTEGER) AND CAST(FLOOR((x1.decl + itheta) / izoneheight) AS INTEGER) AND c1.ra BETWEEN x1.ra - alpha(itheta,x1.decl) AND x1.ra + alpha(itheta,x1.decl) AND c1.decl BETWEEN x1.decl - itheta AND x1.decl + itheta AND c1.x * x1.x + c1.y * x1.y + c1.z * x1.z > COS(RADIANS(itheta))
UNION
SELECT -3 AS BGfield,x1.xtrsrcid,c.catname,c1.catsrcid,3600 * DEGREES(2 * ASIN(SQRT(POWER(c1.x - x1.x, 2) + POWER(c1.y - x1.y, 2) + POWER(c1.z - x1.z, 2)) / 2) ) AS assoc_distance_arcsec, SQRT((x1.ra_err)*(x1.ra_err) + (x1.decl_err)*(x1.decl_err) + (c1.ra_err)*(c1.ra_err) + (c1.decl_err)*(c1.decl_err)) AS sigma FROM (SELECT xtrsrcid AS xtrsrcid,ra - alpha(3 * (2 * itheta), decl) AS ra,decl AS decl,ra_err AS ra_err,decl_err AS decl_err,COS(RADIANS(decl)) * COS(RADIANS(ra - alpha(3 * (2 * itheta), decl))) AS x,COS(RADIANS(decl)) * SIN(RADIANS(ra - alpha(3 * (2 * itheta), decl))) AS y,z AS z FROM extractedsources xp1 WHERE image_id = iimageid) x1,catalogedsources c1,catalogs c WHERE c1.cat_id = c.catid AND c1.zone BETWEEN CAST(FLOOR((x1.decl - itheta) / izoneheight) AS INTEGER) AND CAST(FLOOR((x1.decl + itheta) / izoneheight) AS INTEGER) AND c1.ra BETWEEN x1.ra - alpha(itheta,x1.decl) AND x1.ra + alpha(itheta,x1.decl) AND c1.decl BETWEEN x1.decl - itheta AND x1.decl + itheta AND c1.x * x1.x + c1.y * x1.y + c1.z * x1.z > COS(RADIANS(itheta))
UNION
SELECT -2 AS BGfield,x1.xtrsrcid,c.catname,c1.catsrcid,3600 * DEGREES(2 * ASIN(SQRT(POWER(c1.x - x1.x, 2) + POWER(c1.y - x1.y, 2) + POWER(c1.z - x1.z, 2)) / 2) ) AS assoc_distance_arcsec, SQRT((x1.ra_err)*(x1.ra_err) + (x1.decl_err)*(x1.decl_err) + (c1.ra_err)*(c1.ra_err) + (c1.decl_err)*(c1.decl_err)) AS sigma FROM (SELECT xtrsrcid AS xtrsrcid,ra - alpha(2 * (2 * itheta), decl) AS ra,decl AS decl,ra_err AS ra_err,decl_err AS decl_err,COS(RADIANS(decl)) * COS(RADIANS(ra - alpha(2 * (2 * itheta), decl))) AS x,COS(RADIANS(decl)) * SIN(RADIANS(ra - alpha(2 * (2 * itheta), decl))) AS y,z AS z FROM extractedsources xp1 WHERE image_id = iimageid) x1,catalogedsources c1,catalogs c WHERE c1.cat_id = c.catid AND c1.zone BETWEEN CAST(FLOOR((x1.decl - itheta) / izoneheight) AS INTEGER) AND CAST(FLOOR((x1.decl + itheta) / izoneheight) AS INTEGER) AND c1.ra BETWEEN x1.ra - alpha(itheta,x1.decl) AND x1.ra + alpha(itheta,x1.decl) AND c1.decl BETWEEN x1.decl - itheta AND x1.decl + itheta AND c1.x * x1.x + c1.y * x1.y + c1.z * x1.z > COS(RADIANS(itheta))
UNION
SELECT -1 AS BGfield,x1.xtrsrcid,c.catname,c1.catsrcid,3600 * DEGREES(2 * ASIN(SQRT(POWER(c1.x - x1.x, 2) + POWER(c1.y - x1.y, 2) + POWER(c1.z - x1.z, 2)) / 2) ) AS assoc_distance_arcsec, SQRT((x1.ra_err)*(x1.ra_err) + (x1.decl_err)*(x1.decl_err) + (c1.ra_err)*(c1.ra_err) + (c1.decl_err)*(c1.decl_err)) AS sigma FROM (SELECT xtrsrcid AS xtrsrcid,ra - alpha(1 * (2 * itheta), decl) AS ra,decl AS decl,ra_err AS ra_err,decl_err AS decl_err,COS(RADIANS(decl)) * COS(RADIANS(ra - alpha(1 * (2 * itheta), decl))) AS x,COS(RADIANS(decl)) * SIN(RADIANS(ra - alpha(1 * (2 * itheta), decl))) AS y,z AS z FROM extractedsources xp1 WHERE image_id = iimageid) x1,catalogedsources c1,catalogs c WHERE c1.cat_id = c.catid AND c1.zone BETWEEN CAST(FLOOR((x1.decl - itheta) / izoneheight) AS INTEGER) AND CAST(FLOOR((x1.decl + itheta) / izoneheight) AS INTEGER) AND c1.ra BETWEEN x1.ra - alpha(itheta,x1.decl) AND x1.ra + alpha(itheta,x1.decl) AND c1.decl BETWEEN x1.decl - itheta AND x1.decl + itheta AND c1.x * x1.x + c1.y * x1.y + c1.z * x1.z > COS(RADIANS(itheta))
UNION
SELECT 0 AS BGfield,x1.xtrsrcid,c.catname,c1.catsrcid,3600 * DEGREES(2 * ASIN(SQRT(POWER(c1.x - x1.x, 2) + POWER(c1.y - x1.y, 2) + POWER(c1.z - x1.z, 2)) / 2) ) AS assoc_distance_arcsec, SQRT((x1.ra_err)*(x1.ra_err) + (x1.decl_err)*(x1.decl_err) + (c1.ra_err)*(c1.ra_err) + (c1.decl_err)*(c1.decl_err)) AS sigma FROM extractedsources x1,catalogedsources c1,catalogs c WHERE x1.image_id = iimageid AND c1.cat_id = c.catid AND c1.zone BETWEEN CAST(FLOOR((x1.decl - itheta) / izoneheight) AS INTEGER) AND CAST(FLOOR((x1.decl + itheta) / izoneheight) AS INTEGER) AND c1.ra BETWEEN x1.ra - alpha(itheta,x1.decl) AND x1.ra + alpha(itheta,x1.decl) AND c1.decl BETWEEN x1.decl - itheta AND x1.decl + itheta AND c1.x * x1.x + c1.y * x1.y + c1.z * x1.z > COS(RADIANS(itheta))
UNION
SELECT 1 AS BGfield,x1.xtrsrcid,c.catname,c1.catsrcid,3600 * DEGREES(2 * ASIN(SQRT(POWER(c1.x - x1.x, 2) + POWER(c1.y - x1.y, 2) + POWER(c1.z - x1.z, 2)) / 2) ) AS assoc_distance_arcsec, SQRT((x1.ra_err)*(x1.ra_err) + (x1.decl_err)*(x1.decl_err) + (c1.ra_err)*(c1.ra_err) + (c1.decl_err)*(c1.decl_err)) AS sigma FROM (SELECT xtrsrcid AS xtrsrcid,ra + alpha(1 * (2 * itheta), decl) AS ra,decl AS decl,ra_err AS ra_err,decl_err AS decl_err,COS(RADIANS(decl)) * COS(RADIANS(ra + alpha(1 * (2 * itheta), decl))) AS x,COS(RADIANS(decl)) * SIN(RADIANS(ra + alpha(1 * (2 * itheta), decl))) AS y,z AS z FROM extractedsources xp1 WHERE image_id = iimageid) x1,catalogedsources c1,catalogs c WHERE c1.cat_id = c.catid AND c1.zone BETWEEN CAST(FLOOR((x1.decl - itheta) / izoneheight) AS INTEGER) AND CAST(FLOOR((x1.decl + itheta) / izoneheight) AS INTEGER) AND c1.ra BETWEEN x1.ra - alpha(itheta,x1.decl) AND x1.ra + alpha(itheta,x1.decl) AND c1.decl BETWEEN x1.decl - itheta AND x1.decl + itheta AND c1.x * x1.x + c1.y * x1.y + c1.z * x1.z > COS(RADIANS(itheta))
UNION
SELECT 2 AS BGfield,x1.xtrsrcid,c.catname,c1.catsrcid,3600 * DEGREES(2 * ASIN(SQRT(POWER(c1.x - x1.x, 2) + POWER(c1.y - x1.y, 2) + POWER(c1.z - x1.z, 2)) / 2) ) AS assoc_distance_arcsec, SQRT((x1.ra_err)*(x1.ra_err) + (x1.decl_err)*(x1.decl_err) + (c1.ra_err)*(c1.ra_err) + (c1.decl_err)*(c1.decl_err)) AS sigma FROM (SELECT xtrsrcid AS xtrsrcid,ra + alpha(2 * (2 * itheta), decl) AS ra,decl AS decl,ra_err AS ra_err,decl_err AS decl_err,COS(RADIANS(decl)) * COS(RADIANS(ra + alpha(2 * (2 * itheta), decl))) AS x,COS(RADIANS(decl)) * SIN(RADIANS(ra + alpha(2 * (2 * itheta), decl))) AS y,z AS z FROM extractedsources xp1 WHERE image_id = iimageid) x1,catalogedsources c1,catalogs c WHERE c1.cat_id = c.catid AND c1.zone BETWEEN CAST(FLOOR((x1.decl - itheta) / izoneheight) AS INTEGER) AND CAST(FLOOR((x1.decl + itheta) / izoneheight) AS INTEGER) AND c1.ra BETWEEN x1.ra - alpha(itheta,x1.decl) AND x1.ra + alpha(itheta,x1.decl) AND c1.decl BETWEEN x1.decl - itheta AND x1.decl + itheta AND c1.x * x1.x + c1.y * x1.y + c1.z * x1.z > COS(RADIANS(itheta))
UNION
SELECT 3 AS BGfield,x1.xtrsrcid,c.catname,c1.catsrcid,3600 * DEGREES(2 * ASIN(SQRT(POWER(c1.x - x1.x, 2) + POWER(c1.y - x1.y, 2) + POWER(c1.z - x1.z, 2)) / 2) ) AS assoc_distance_arcsec, SQRT((x1.ra_err)*(x1.ra_err) + (x1.decl_err)*(x1.decl_err) + (c1.ra_err)*(c1.ra_err) + (c1.decl_err)*(c1.decl_err)) AS sigma FROM (SELECT xtrsrcid AS xtrsrcid,ra + alpha(3 * (2 * itheta), decl) AS ra,decl AS decl,ra_err AS ra_err,decl_err AS decl_err,COS(RADIANS(decl)) * COS(RADIANS(ra + alpha(3 * (2 * itheta), decl))) AS x,COS(RADIANS(decl)) * SIN(RADIANS(ra + alpha(3 * (2 * itheta), decl))) AS y,z AS z FROM extractedsources xp1 WHERE image_id = iimageid) x1,catalogedsources c1,catalogs c WHERE c1.cat_id = c.catid AND c1.zone BETWEEN CAST( FLOOR((x1.decl - itheta) / izoneheight) AS INTEGER) AND CAST(FLOOR((x1.decl + itheta) / izoneheight) AS INTEGER) AND c1.ra BETWEEN x1.ra - alpha(itheta,x1.decl) AND x1.ra + alpha(itheta,x1.decl) AND c1.decl BETWEEN x1.decl - itheta AND x1.decl + itheta AND c1.x * x1.x + c1.y * x1.y + c1.z * x1.z > COS(RADIANS(itheta))
UNION
SELECT 4 AS BGfield,x1.xtrsrcid,c.catname,c1.catsrcid,3600 * DEGREES(2 * ASIN(SQRT(POWER(c1.x - x1.x, 2) + POWER(c1.y - x1.y, 2) + POWER(c1.z - x1.z, 2)) / 2) ) AS assoc_distance_arcsec, SQRT((x1.ra_err)*(x1.ra_err) + (x1.decl_err)*(x1.decl_err) + (c1.ra_err)*(c1.ra_err) + (c1.decl_err)*(c1.decl_err)) AS sigma FROM (SELECT xtrsrcid AS xtrsrcid,ra + alpha(4 * (2 * itheta), decl) AS ra,decl AS decl,ra_err AS ra_err,decl_err AS decl_err,COS(RADIANS(decl)) * COS(RADIANS(ra + alpha(4 * (2 * itheta), decl))) AS x,COS(RADIANS(decl)) * SIN(RADIANS(ra + alpha(4 * (2 * itheta), decl))) AS y,z AS z FROM extractedsources xp1 WHERE image_id = iimageid) x1,catalogedsources c1,catalogs c WHERE c1.cat_id = c.catid AND c1.zone BETWEEN CAST( FLOOR((x1.decl - itheta) / izoneheight) AS INTEGER) AND CAST(FLOOR((x1.decl + itheta) / izoneheight) AS INTEGER) AND c1.ra BETWEEN x1.ra - alpha(itheta,x1.decl) AND x1.ra + alpha(itheta,x1.decl) AND c1.decl BETWEEN x1.decl - itheta AND x1.decl + itheta AND c1.x * x1.x + c1.y * x1.y + c1.z * x1.z > COS(RADIANS(itheta))
UNION
SELECT 5 AS BGfield,x1.xtrsrcid,c.catname,c1.catsrcid,3600 * DEGREES(2 * ASIN(SQRT(POWER(c1.x - x1.x, 2) + POWER(c1.y - x1.y, 2) + POWER(c1.z - x1.z, 2)) / 2) ) AS assoc_distance_arcsec, SQRT((x1.ra_err)*(x1.ra_err) + (x1.decl_err)*(x1.decl_err) + (c1.ra_err)*(c1.ra_err) + (c1.decl_err)*(c1.decl_err)) AS sigma FROM (SELECT xtrsrcid AS xtrsrcid,ra + alpha(5 * (2 * itheta), decl) AS ra,decl AS decl,ra_err AS ra_err,decl_err AS decl_err,COS(RADIANS(decl)) * COS(RADIANS(ra + alpha(5 * (2 * itheta), decl))) AS x,COS(RADIANS(decl)) * SIN(RADIANS(ra + alpha(5 * (2 * itheta), decl))) AS y,z AS z FROM extractedsources xp1 WHERE image_id = iimageid) x1,catalogedsources c1,catalogs c WHERE c1.cat_id = c.catid AND c1.zone BETWEEN CAST( FLOOR((x1.decl - itheta) / izoneheight) AS INTEGER) AND CAST(FLOOR((x1.decl + itheta) / izoneheight) AS INTEGER) AND c1.ra BETWEEN x1.ra - alpha(itheta,x1.decl) AND x1.ra + alpha(itheta,x1.decl) AND c1.decl BETWEEN x1.decl - itheta AND x1.decl + itheta AND c1.x * x1.x + c1.y * x1.y + c1.z * x1.z > COS(RADIANS(itheta))
) t
ORDER BY LR_rutledge
        ,BGfield
        ,xtrsrcid
        ,catsrcid
;


