
INSERT INTO catalogs
  (catid
  ,catname
  ,fullname
  ) 
VALUES 
  (3
  ,'NVSS'
  ,'1.4GHz NRAO VLA Sky Survey (NVSS)'
  )
;


CREATE TABLE aux_catalogedsources
  (aviz_RAJ2000 double precision
  ,aviz_DEJ2000 double precision
  ,aorig_catsrcid INT
  ,afield VARCHAR(8)
  ,axpos double precision
  ,aypos double precision
  ,aname VARCHAR(14)
  ,aRAJ2000 VARCHAR(11)
  ,aDEJ2000 VARCHAR(11)
  ,ae_RAJ2000 double precision
  ,ae_DEJ2000 double precision
  ,aS1400 double precision
  ,ae_S1400 double precision
  ,al_MajAxis CHAR(1)
  ,aMajAxis double precision
  ,al_MinAxis CHAR(1)
  ,aMinAxis double precision
  ,aPA double precision
  ,ae_MajAxis double precision
  ,ae_MinAxis double precision 
  ,ae_PA double precision 
  ,af_resFlux VARCHAR(2)
  ,aresFlux double precision
  ,apolFlux double precision
  ,apolPA double precision
  ,ae_polFlux double precision
  ,ae_polPA double precision
  ,aImage VARCHAR(5)
  ) 
;

COPY  aux_catalogedsources
FROM
/* '/scratch/bscheers/tkp-code/pipe/database/catfiles/nvss/nvss-few.csv' */
/* '${TKPDBCODE}/catfiles/nvss/nvss-all_strip.csv' */
/* '/home/scheers/tkp-code/pipe/database/catfiles/nvss/NVSS-all_strip.csv' */
/* '/export/scratch1/bscheers/code/pipe/database/catfiles/nvss/NVSS-all_strip.csv' */
'/zfs/heastro-plex/scratch/evert/catfiles/NVSS-all_strip.csv'
/* '/data/scratch/rol/catalogs/NVSS-all_strip.csv' */
/* '/Users/evert/lofar/data/catalogs/NVSS-all_strip.csv' */
WITH DELIMITER AS ';'
NULL AS ''
;

/* So we can put our FoV conditions in here...*/
INSERT INTO catalogedsources
  (orig_catsrcid
  ,catsrcname
  ,cat_id
  ,band
  ,ra
  ,decl
  ,zone
  ,ra_err
  ,decl_err
  ,freq_eff
  ,x
  ,y
  ,z
  /*,src_type*/
  ,fit_probl
  ,pa
  ,pa_err
  ,major
  ,major_err
  ,minor
  ,minor_err
  ,i_int_avg
  ,i_int_avg_err
  ,frame
  )
  SELECT aorig_catsrcid
        ,'J' || aname
        ,3
        ,getBand(1.4e9)
        ,aviz_RAJ2000
        ,aviz_DEJ2000
        ,CAST(FLOOR(aviz_DEJ2000) AS INTEGER)
        /*,3600 * deg(2 * ASIN(SQRT((COS(rad(aviz_DEJ2000)) * COS(rad(aviz_RAJ2000 + ae_RAJ2000 / 480)) - COS(rad(aviz_DEJ2000)) * COS(rad(aviz_RAJ2000))) 
                                      * 
                                      (COS(rad(aviz_DEJ2000)) * COS(rad(aviz_RAJ2000 + ae_RAJ2000 / 480)) - COS(rad(aviz_DEJ2000)) * COS(rad(aviz_RAJ2000)))
                                     +
                                      (COS(rad(aviz_DEJ2000)) * SIN(rad(aviz_RAJ2000 + ae_RAJ2000 / 480)) - COS(rad(aviz_DEJ2000)) * SIN(rad(aviz_RAJ2000)))
                                      *
                                      (COS(rad(aviz_DEJ2000)) * SIN(rad(aviz_RAJ2000 + ae_RAJ2000 / 480)) - COS(rad(aviz_DEJ2000)) * SIN(rad(aviz_RAJ2000)))
                                     )
                                / 2
                                )
                       )*/
        ,15 * ae_RAJ2000 * COS(rad(aviz_DEJ2000))
        ,ae_DEJ2000 
        ,1.e49
        ,COS(rad(aviz_DEJ2000)) * COS(rad(aviz_RAJ2000))
        ,COS(rad(aviz_DEJ2000)) * SIN(rad(aviz_RAJ2000))
        ,SIN(rad(aviz_DEJ2000))
        ,af_resFlux 
        ,aPA
        ,ae_PA
        ,aMajAxis
        ,ae_MajAxis
        ,aMinAxis
        ,ae_MinAxis
        ,aS1400 / 1000
        ,ae_S1400 / 1000
        ,aImage
    FROM aux_catalogedsources
  ;

DROP TABLE aux_catalogedsources;

--SELECT NOW();
