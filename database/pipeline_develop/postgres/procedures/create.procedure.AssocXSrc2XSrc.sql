--DROP PROCEDURE AssocXSrc2XSrc;

/*+------------------------------------------------------------------+
 *| This procedure runs the source association algorithm.            |
 *| It takes an imageid as input argument and checks whether all the |
 *| sources that were detected in this image have candidate          |
 *| association sources within the source search radius.             |
 *| (Only candidate source from the same dataset (i.e. all sources in|
 *| the images with the same ds_id) are included in the search.      |
 *| All found sources that fall in the search radius will be         |
 *| treated as candidates.                                           |
 *| Criteria, limits, cutoffs determine then whether a candidate will|
 *| be considered as the true association/counterpart.               |
 *| This method also includes multifrequency searches.               |
 *|                                                                  |
 *| First, an explanation of the assocxtrsources table, in which all |
 *| the candidate association pairs are stored.                      |
 *| This table has two columns, xtrsrc_id and assoc_xtrsrc_id. The   |
 *| first is the ID of the source when it was detected for the first |
 *| time (in the processing, so this is not neccessarily             |
 *| chronologous). The second column is the ID of the source that    |
 *| fell in the search radius and so was considered as a candidate.  |
 *| In fact, this table might be regarded as the source light curve  |
 *| table.                                                           |
 *|                                                                  |
 *|  1- 1  2- 2  3- 3 4- 4                                           |
 *|  1- 5  2- 6  3- 7 4- 8                                           |
 *|  1- 9  2-10  3-11 4-12                                           |
 *|  1-13                                                            |
 *|                                                                  |
 *|                                                                  |
 *| It might be important to note that the images should be processed|
 *| atomic and this procedure must be executed in a transactional    |
 *| way, otherwise we process incomplete sets of sources and images, |
 *| and the results will be corrupted.                               |
 *|                                                                  |
 *| Then, we will try to find associations for all the sources that  |
 *| are in the current image.                                        |
 *| When we have source X_i under investigation:                     |
 *| (1) we will collect the association candidates found in the      |
 *|     assocxtrsources table by inspecting only the xtrsrc_id       |
 *|     column. , A_i,j where j= 1,2,...,M and                       |
 *|     max(M) ~ 5.                                                  |
 *|                                                                  |
 *| During processing, the following happens.                        |
 *| Every source in the input image is processed as follows:         |
 *| (1) a search area of radius 0.025 [deg] is set around the source|
 *| (2) the other images (belonging to the same dataset) are looked  |
 *|     up for candidate sources that                                |
 *|     fall in this area (there may be none, one or many candidates)|
 *| (3) Then we check these candidates.                              |
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

/* 
 * -- 1 -- 
 * Here we select the sources from assocxtrsources that are in xtrsrc_id
 * and fall in the search radius of source i.
 * They will be appended to the table as another "light curve" datapoint:
 * A_j_id - X_i_id
 * In this way we append a data point to the existing light curve data 
 * (this is the "next" data point)
 *
 * -- 2 -- 
 * Here we will select sources that are in the assoc_xtrsrc_id column and 
 * do not have an valid candidate in the corresponding xtrsrc_id column.
 * They will be inserted as :
 * A_j_id - A_j_id (here)
 * and as
 * A_j_id - X_j_id (in select in next union)
 * In this way we start a series of just branched light curve data 
 * (this is its first datapoint)
 *
 * -- 3 -- 
 * Here we will select sources that are in the assoc_xtrsrc_id column and 
 * do not have an valid candidate in the corresponding xtrsrc_id column.
 * (Same select as previous union
 * They will be inserted as :
 * A_j_id - X_j_id (here)
 * and as
 * A_j_id - A_j_id (in select in previous union)
 * In this way we append a data point to the just branched light curve 
 * data (this is the second data point)
 *
 * -- 4 -- 
 * Here we will insert sources that did not have an entry in 
 * assocxtrsources. They will be inserted as :
 * X_j_id - X_j_id 
 * In this way we start a new series of light curve data
 *
 */

CREATE PROCEDURE AssocXSrc2XSrc(iimageid INT)

BEGIN
  
  /*DECLARE N_density double precision;
  
  SET N_density = 4.02439375E-06; NVSS density */
  
  /*
  We set zoneheight directly in the clauses
  SELECT zoneheight
    INTO izoneheight
    FROM zoneheight
  ;
    
  SET itheta = 0.025;
  */

  insert into assocxtrsources
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
    FROM (
  SELECT t2.xtrsrc_id 
        ,t2.assoc_xtrsrc_id 
        ,1 AS assoc_weight 
        ,t2.assoc_distance_arcsec 
        ,5 AS assoc_lr_method 
        ,t2.assoc_distance_arcsec / SQRT(t2.sigma_ra_squared + t2.sigma_decl_squared) AS assoc_r 
        ,LOG10(EXP(-t2.assoc_distance_arcsec * t2.assoc_distance_arcsec 
                  / (2 * (t2.sigma_ra_squared + t2.sigma_decl_squared))
                  ) 
              / (2 * PI() * SQRT(t2.sigma_ra_squared) * SQRT(t2.sigma_decl_squared) * 4.02439375E-06)
              ) AS assoc_lr
    FROM (SELECT t1.xtrsrc_id 
                ,t1.assoc_xtrsrc_id 
                ,3600 * DEGREES(2 * ASIN(SQRT( (t1.assoc_x - t1.x) * (t1.assoc_x - t1.x) 
                                             + (t1.assoc_y - t1.y) * (t1.assoc_y - t1.y) 
                                             + (t1.assoc_z - t1.z) * (t1.assoc_z - t1.z) 
                                             ) 
                                        / 2
                                        )
                               ) AS assoc_distance_arcsec
                ,t1.assoc_ra_err * t1.assoc_ra_err + t1.ra_err * t1.ra_err AS sigma_ra_squared 
                ,t1.assoc_decl_err * t1.assoc_decl_err + t1.decl_err * t1.decl_err AS sigma_decl_squared 
            FROM (SELECT a1.xtrsrc_id AS xtrsrc_id 
                        ,x0.xtrsrcid AS assoc_xtrsrc_id
                        ,x1.ra_err AS ra_err 
                        ,x1.decl_err AS decl_err 
                        ,x1.x AS x 
                        ,x1.y AS y 
                        ,x1.z AS z 
                        ,x0.ra_err AS assoc_ra_err 
                        ,x0.decl_err AS assoc_decl_err 
                        ,x0.x AS assoc_x 
                        ,x0.y AS assoc_y 
                        ,x0.z AS assoc_z 
                    FROM extractedsources x0 
                        ,images im0 
                        ,assocxtrsources a1 
                        ,extractedsources x1 
                        ,images im1
                   WHERE x0.image_id = iimageid
                     AND x0.image_id = im0.imageid 
                     AND a1.xtrsrc_id = x1.xtrsrcid 
                     AND a1.xtrsrc_id = a1.assoc_xtrsrc_id 
                     AND x1.image_id = im1.imageid 
                     AND im1.ds_id = im0.ds_id 
                     /*AND x1.zone BETWEEN CAST(FLOOR((x0.decl - 0.025) / 1) AS INTEGER) 
                                     AND CAST(FLOOR((x0.decl + 0.025) / 1) AS INTEGER) 
                     AND x1.ra BETWEEN x0.ra - alpha(0.025,x0.decl) 
                                   AND x0.ra + alpha(0.025,x0.decl) 
                     AND x1.decl BETWEEN x0.decl - 0.025 
                                     AND x0.decl + 0.025 */
                     AND x0.x * x1.x + x0.y * x1.y + x0.z * x1.z > COS(RADIANS(0.025)) 
                 ) t1 
         ) t2 
  UNION
  SELECT a1.assoc_xtrsrc_id AS xtrsrc_id
        ,a1.assoc_xtrsrc_id AS assoc_xtrsrc_id
        ,2 AS assoc_weight
        ,0 AS assoc_distance_arcsec
        ,5 AS assoc_lr_method
        ,0 AS assoc_r
        ,LOG10(1 / (4 * pi() * x2.ra_err * x2.decl_err * 4.02439375E-06)) AS assoc_lr
    FROM assocxtrsources a1
        ,extractedsources x0
        ,images im0
        ,extractedsources x1
        ,extractedsources x2
        ,images im2
   WHERE x0.image_id = iimageid
     AND x0.image_id = im0.imageid 
     AND a1.assoc_xtrsrc_id = x2.xtrsrcid 
     AND x2.image_id = im2.imageid 
     AND im2.ds_id = im0.ds_id
     AND x0.x * x2.x + x0.y * x2.y + x0.z * x2.z > COS(RADIANS(0.025)) 
     AND a1.xtrsrc_id = x1.xtrsrcid 
     AND x0.x * x1.x + x0.y * x1.y + x0.z * x1.z < COS(RADIANS(0.025)) 
     and not exists (select t1.xtrsrc_id 
                       from assocxtrsources t1
                      where t1.xtrsrc_id = a1.assoc_xtrsrc_id
                        and t1.assoc_xtrsrc_id = t1.xtrsrc_id
                    )
  UNION
  SELECT t2.xtrsrc_id
        ,t2.assoc_xtrsrc_id
        ,3 AS assoc_weight
        ,t2.assoc_distance_arcsec
        ,5 AS assoc_lr_method
        ,t2.assoc_distance_arcsec / SQRT(t2.sigma_ra_squared + t2.sigma_decl_squared) AS assoc_r
        ,LOG10(EXP(-t2.assoc_distance_arcsec * t2.assoc_distance_arcsec
                  / (2 * (t2.sigma_ra_squared + t2.sigma_decl_squared))
                  )
              / (2 * PI() * SQRT(t2.sigma_ra_squared) * SQRT(t2.sigma_decl_squared) * 4.02439375E-06)
              ) AS assoc_lr
    FROM (SELECT t1.xtrsrc_id
                ,t1.assoc_xtrsrc_id
                ,3600 * DEGREES(2 * ASIN(SQRT( (t1.assoc_x - t1.x) * (t1.assoc_x - t1.x)
                                             + (t1.assoc_y - t1.y) * (t1.assoc_y - t1.y)
                                             + (t1.assoc_z - t1.z) * (t1.assoc_z - t1.z)
                                             )
                                             / 2
                                        )
                               ) AS assoc_distance_arcsec
                ,t1.assoc_ra_err * t1.assoc_ra_err + t1.ra_err * t1.ra_err AS sigma_ra_squared
                ,t1.assoc_decl_err * t1.assoc_decl_err + t1.decl_err * t1.decl_err AS sigma_decl_squared
            FROM (SELECT a1.assoc_xtrsrc_id AS xtrsrc_id
                        ,x2.ra_err AS ra_err
                        ,x2.decl_err AS decl_err
                        ,x2.x AS x
                        ,x2.y AS y
                        ,x2.z AS z
                        ,x0.xtrsrcid AS assoc_xtrsrc_id
                        ,x0.ra_err AS assoc_ra_err
                        ,x0.decl_err AS assoc_decl_err
                        ,x0.x AS assoc_x
                        ,x0.y AS assoc_y
                        ,x0.z AS assoc_z
                    FROM assocxtrsources a1
                        ,extractedsources x0
                        ,images im0
                        ,extractedsources x1
                        ,extractedsources x2
                        ,images im2
                   WHERE x0.image_id = iimageid
                     AND x0.image_id = im0.imageid 
                     AND a1.assoc_xtrsrc_id = x2.xtrsrcid 
                     AND x2.image_id = im2.imageid 
                     AND im2.ds_id = im0.ds_id
                     AND x0.x * x2.x + x0.y * x2.y + x0.z * x2.z > COS(RADIANS(0.025)) 
                     AND a1.xtrsrc_id = x1.xtrsrcid 
                     AND x0.x * x1.x + x0.y * x1.y + x0.z * x1.z < COS(RADIANS(0.025)) 
                     and not exists (select t1.xtrsrc_id 
                                       from assocxtrsources t1
                                      where t1.xtrsrc_id = a1.assoc_xtrsrc_id
                                        and t1.assoc_xtrsrc_id = t1.xtrsrc_id
                                    )
                 ) t1
         ) t2
  UNION
  SELECT x10.xtrsrcid AS xtrsrc_id
        ,x10.xtrsrcid AS assoc_xtrsrc_id
        ,4 AS assoc_weight
        ,0 AS assoc_distance_arcsec
        ,5 AS assoc_lr_method
        ,0 AS assoc_r
        ,LOG10(1 / (4 * pi() * x10.ra_err * x10.decl_err * 4.02439375E-06)) AS assoc_lr
    from extractedsources x10
   where x10.image_id = iimageid
     and x10.xtrsrcid not in (select x0.xtrsrcid
                                    /*,a1.xtrsrc_id
                                    ,3600 * DEGREES(2 * ASIN(SQRT( (x0.x - x1.x) * (x0.x - x1.x) 
                                                                 + (x0.y - x1.y) * (x0.y - x1.y) 
                                                                 + (x0.z - x1.z) * (x0.z - x1.z) 
                                                                 ) 
                                                                 / 2
                                                            )
                                                   ) AS assoc_distance_arcsec*/
                                FROM extractedsources x0
                                    ,images im0
                                    ,assocxtrsources a1
                                    ,extractedsources x1
                                    ,images im1
                               WHERE x0.image_id = iimageid
                                 AND x0.image_id = im0.imageid
                                 AND a1.xtrsrc_id = x1.xtrsrcid
                                 AND x1.image_id = im1.imageid
                                 AND im1.ds_id = im0.ds_id
                                 AND x0.x * x1.x + x0.y * x1.y + x0.z * x1.z > COS(RADIANS(0.025))
                              /*ORDER BY x0.xtrsrcid
                                      ,a1.xtrsrc_id*/
                             )
     and x10.xtrsrcid not in (select x0.xtrsrcid
                                    /*,a1.assoc_xtrsrc_id
                                    ,3600 * DEGREES(2 * ASIN(SQRT( (x0.x - x2.x) * (x0.x - x2.x) 
                                                                 + (x0.y - x2.y) * (x0.y - x2.y) 
                                                                 + (x0.z - x2.z) * (x0.z - x2.z) 
                                                                 ) 
                                                                 / 2
                                                            )
                                                   ) AS assoc_distance_arcsec*/
                                FROM extractedsources x0
                                    ,images im0
                                    ,assocxtrsources a1
                                    ,extractedsources x2
                                    ,images im2
                               WHERE x0.image_id = iimageid
                                 AND x0.image_id = im0.imageid
                                 AND a1.assoc_xtrsrc_id = x2.xtrsrcid
                                 AND x2.image_id = im2.imageid
                                 AND im2.ds_id = im0.ds_id
                                 AND x0.x * x2.x + x0.y * x2.y + x0.z * x2.z > COS(RADIANS(0.025))
                              /*ORDER BY x0.xtrsrcid
                                      ,a1.assoc_xtrsrc_id*/
                             )
      ) ut
  ;

END;

