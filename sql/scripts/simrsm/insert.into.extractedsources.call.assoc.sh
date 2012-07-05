#!/usr/bin/env bash

# arguments:
# $1 host
# $2 database
# $3 dbuser
# $4 dbpw


# An example call of this script could be:
# %> ./scriptname.sh ldb001 pipeline_wenssnvss wenssnvss ch3
# The procedure will process all the wenss sources as if they were extracted from 
# the source extraction modules in our TKP-pipeline.
# Then, every source is offset by 180", and this is done eight times,
# where the 8 offset sources lie on a rectangular 3x3 grid with the
# wenss source in the middle. These Background sources are also 
# processed as if they were extracted from the source extraction modules

#host=${1}
#db=${2}
#dbuser=${3}
#dbpasswd=${4}

DSID=1
echo "Insert dataset"
mclient -lsql -h$1 -d$2 -u$3 -P$4 <<-EOF
INSERT INTO datasets
  (dsid
  ,rerun
  ,dstype
  ,process_ts
  ,dsinname
  ) VALUES
  ($DSID
  ,0
  ,1
  ,NOW()
  ,'10 sources per image'
  )
;
EOF

#DECLARE t_cnt INT;
#SET t_cnt = $COUNT;
#SELECT ooim;

#Image_id in the input file is defaulted to 0
COUNT=1
while [ $COUNT -le 10 ]; do
  echo Transaction, DELETE,COPY INTO file, INSERT, Run $COUNT
  mclient -t -lsql -h$1 -d$2 -u$3 -P$4 <<-EOF
  DECLARE oimgid INT;
  SET oimgid = insertImage($DSID,42000000,4000000,CAST(NOW() AS TIMESTAMP),'this/is/fake');
  DELETE FROM loadxtrsources;
  COPY 10 RECORDS
  INTO loadxtrsources
  FROM '/home/scheers/tkp-code/pipe/database/pipeline_develop/MonetDB/scripts/simrsm/copy.into.extractedsources.10.csv'
  USING DELIMITERS ','
                  ,'\n'
  NULL AS '';
  INSERT INTO extractedsources
    (image_id 
    ,zone
    ,ra
    ,decl
    ,ra_err
    ,decl_err
    ,x
    ,y
    ,z
    ,det_sigma
    ,I_peak
    ,I_peak_err
    ,I_int
    ,I_int_err
    )
    SELECT oimgid
          ,CAST(FLOOR(ldecl/1) AS INTEGER)
          ,lra
          ,ldecl
          ,lra_err * 3600
          ,ldecl_err * 3600
          ,COS(RADIANS(ldecl)) * COS(RADIANS(lra))
          ,COS(RADIANS(ldecl)) * SIN(RADIANS(lra))
          ,SIN(RADIANS(ldecl))
          ,ldet_sigma
          ,lI_peak
          ,lI_peak_err
          ,lI_int
          ,lI_int_err
      FROM loadxtrsources
  ;
  DELETE FROM loadxtrsources
  ;
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
                  ,5 AS assoc_lr_method  
                  ,t2.assoc_distance_arcsec / SQRT(t2.sigma_ra_squared + t2.sigma_decl_squared) AS assoc_r  
                  ,LOG10(EXP(-t2.assoc_distance_arcsec * t2.assoc_distance_arcsec / (2 * (t2.sigma_ra_squared + t2.sigma_decl_squared)) ) / (2 * PI() * SQRT(t2.sigma_ra_squared) * SQRT(t2.sigma_decl_squared) * 4.02439375E-06) ) AS assoc_lr 
              FROM (SELECT t1.xtrsrc_id  
                          ,t1.assoc_xtrsrc_id  
                          ,3600 * DEGREES(2 * ASIN(SQRT( (t1.assoc_x - t1.x) * (t1.assoc_x - t1.x) + (t1.assoc_y - t1.y) * (t1.assoc_y - t1.y) + (t1.assoc_z - t1.z) * (t1.assoc_z - t1.z) ) / 2 ) ) AS assoc_distance_arcsec 
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
                             WHERE x0.image_id = oimgid 
                               AND x0.image_id = im0.imageid  
                               AND a1.xtrsrc_id = x1.xtrsrcid  
                               AND a1.xtrsrc_id = a1.assoc_xtrsrc_id  
                               AND x1.image_id = im1.imageid  
                               AND im1.ds_id = im0.ds_id  
                               AND x1.zone BETWEEN CAST(FLOOR((x0.decl - 0.025) / 1) AS INTEGER)  
                                               AND CAST(FLOOR((x0.decl + 0.025) / 1) AS INTEGER)  
                               AND x1.ra BETWEEN x0.ra - alpha(0.025,x0.decl)  
                                             AND x0.ra + alpha(0.025,x0.decl)  
                               AND x1.decl BETWEEN x0.decl - 0.025  
                                               AND x0.decl + 0.025  
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
             WHERE x0.image_id = oimgid 
               AND x0.image_id = im0.imageid  
               AND a1.assoc_xtrsrc_id = x2.xtrsrcid  
               AND x2.image_id = im2.imageid  
               AND im2.ds_id = im0.ds_id 
               AND x0.x * x2.x + x0.y * x2.y + x0.z * x2.z > COS(RADIANS(0.025))  
               AND a1.xtrsrc_id = x1.xtrsrcid  
               AND x0.x * x1.x + x0.y * x1.y + x0.z * x1.z < COS(RADIANS(0.025))  
               AND NOT EXISTS (SELECT t1.xtrsrc_id  
                                 FROM assocxtrsources t1 
                                WHERE t1.xtrsrc_id = a1.assoc_xtrsrc_id 
                                  AND t1.assoc_xtrsrc_id = t1.xtrsrc_id 
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
                          ,3600 * DEGREES(2 * ASIN(SQRT( (t1.assoc_x - t1.x) * (t1.assoc_x - t1.x) + (t1.assoc_y - t1.y) * (t1.assoc_y - t1.y) + (t1.assoc_z - t1.z) * (t1.assoc_z - t1.z) ) / 2 ) ) AS assoc_distance_arcsec 
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
                             WHERE x0.image_id = oimgid 
                               AND x0.image_id = im0.imageid  
                               AND a1.assoc_xtrsrc_id = x2.xtrsrcid  
                               AND x2.image_id = im2.imageid  
                               AND im2.ds_id = im0.ds_id 
                               AND x0.x * x2.x + x0.y * x2.y + x0.z * x2.z > COS(RADIANS(0.025))  
                               AND a1.xtrsrc_id = x1.xtrsrcid  
                               AND x0.x * x1.x + x0.y * x1.y + x0.z * x1.z < COS(RADIANS(0.025))  
                               AND NOT EXISTS (SELECT t1.xtrsrc_id  
                                                 FROM assocxtrsources t1 
                                                WHERE t1.xtrsrc_id = a1.assoc_xtrsrc_id 
                                                  AND t1.assoc_xtrsrc_id = t1.xtrsrc_id 
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
             where x10.image_id = oimgid 
               AND x10.xtrsrcid NOT IN (SELECT x0.xtrsrcid 
                                          FROM extractedsources x0 
                                              ,images im0 
                                              ,assocxtrsources a1 
                                              ,extractedsources x1 
                                              ,images im1 
                                         WHERE x0.image_id = oimgid 
                                           AND x0.image_id = im0.imageid 
                                           AND a1.xtrsrc_id = x1.xtrsrcid 
                                           AND x1.image_id = im1.imageid 
                                           AND im1.ds_id = im0.ds_id 
                                           AND x0.x * x1.x + x0.y * x1.y + x0.z * x1.z > COS(RADIANS(0.025)) 
                                       ) 
               AND x10.xtrsrcid NOT IN (SELECT x0.xtrsrcid 
                                          FROM extractedsources x0 
                                              ,images im0 
                                              ,assocxtrsources a1 
                                              ,extractedsources x2 
                                              ,images im2 
                                         WHERE x0.image_id = oimgid 
                                           AND x0.image_id = im0.imageid 
                                           AND a1.assoc_xtrsrc_id = x2.xtrsrcid 
                                           AND x2.image_id = im2.imageid 
                                           AND im2.ds_id = im0.ds_id 
                                           AND x0.x * x2.x + x0.y * x2.y + x0.z * x2.z > COS(RADIANS(0.025)) 
                                       ) 
                ) ut 
  ;
EOF
  let COUNT=COUNT+1
done

echo "READY"

