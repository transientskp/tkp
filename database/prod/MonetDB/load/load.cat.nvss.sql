DECLARE icatid INT;
DECLARE i_freq_eff DOUBLE;
DECLARE iband INT;
SET icatid = 3;

--SELECT NOW();

INSERT INTO catalogs
  (catid
  ,catname
  ,fullname
  ) 
VALUES 
  (icatid
  ,'NVSS'
  ,'1.4GHz NRAO VLA Sky Survey (NVSS)'
  )
;

SET i_freq_eff = 1400000000.0;
SET iband = getBand(i_freq_eff, 10000000.0);

CREATE TABLE aux_catalogedsources
  (aviz_RAJ2000 DOUBLE
  ,aviz_DEJ2000 DOUBLE
  ,aorig_catsrcid INT
  ,afield VARCHAR(8)
  ,axpos DOUBLE
  ,aypos DOUBLE
  ,aname VARCHAR(14)
  ,aRAJ2000 VARCHAR(11)
  ,aDEJ2000 VARCHAR(11)
  ,ae_RAJ2000 DOUBLE
  ,ae_DEJ2000 DOUBLE
  ,aS1400 DOUBLE
  ,ae_S1400 DOUBLE
  ,al_MajAxis CHAR(1)
  ,aMajAxis DOUBLE
  ,al_MinAxis CHAR(1)
  ,aMinAxis DOUBLE
  ,aPA DOUBLE
  ,ae_MajAxis DOUBLE
  ,ae_MinAxis DOUBLE 
  ,ae_PA DOUBLE 
  ,af_resFlux VARCHAR(2)
  ,aresFlux DOUBLE
  ,apolFlux DOUBLE
  ,apolPA DOUBLE
  ,ae_polFlux DOUBLE
  ,ae_polPA DOUBLE
  ,aImage VARCHAR(5)
  ) 
;

COPY 1773484 RECORDS
INTO aux_catalogedsources
/*FROM '/scratch/bscheers/databases/catalogs/nvss/csv/nvss-all.csv'*/
FROM '/home/bscheers/tkp-code/pipe/database/catfiles/nvss/nvss-all.csv'
/*FROM '/Users/bart/databases/catalogs/nvss/nvss-all.csv'*/
USING DELIMITERS ';', '\n'
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
        ,CONCAT('NVSS J', aname)
        ,icatid
        ,iband
        ,aviz_RAJ2000
        ,aviz_DEJ2000
        ,CAST(FLOOR(aviz_DEJ2000) AS INTEGER)
        ,3600 * DEGREES(2 * ASIN(SQRT((COS(RADIANS(aviz_DEJ2000)) * COS(RADIANS(aviz_RAJ2000 + ae_RAJ2000 / 480)) - COS(radians(aviz_DEJ2000)) * COS(radians(aviz_RAJ2000))) 
                                      * 
                                      (COS(RADIANS(aviz_DEJ2000)) * COS(RADIANS(aviz_RAJ2000 + ae_RAJ2000 / 480)) - COS(radians(aviz_DEJ2000)) * COS(radians(aviz_RAJ2000)))
                                     +
                                      (COS(RADIANS(aviz_DEJ2000)) * SIN(RADIANS(aviz_RAJ2000 + ae_RAJ2000 / 480)) - COS(radians(aviz_DEJ2000)) * SIN(radians(aviz_RAJ2000)))
                                      *
                                      (COS(RADIANS(aviz_DEJ2000)) * SIN(RADIANS(aviz_RAJ2000 + ae_RAJ2000 / 480)) - COS(radians(aviz_DEJ2000)) * SIN(radians(aviz_RAJ2000)))
                                     )
                                / 2
                                )
                       )
        ,ae_DEJ2000 / 2
        ,i_freq_eff
        ,COS(radians(aviz_DEJ2000)) * COS(radians(aviz_RAJ2000))
        ,COS(radians(aviz_DEJ2000)) * SIN(radians(aviz_RAJ2000))
        ,SIN(radians(aviz_DEJ2000))
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
