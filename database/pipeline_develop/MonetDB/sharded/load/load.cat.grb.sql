DECLARE icatid INT;
DECLARE i_freq_eff DOUBLE;
DECLARE iband INT;
--SET icatid = 6;
SET icatid = 6;

--SELECT NOW();

INSERT INTO catalogs
  (catid
  ,catname
  ,fullname
  ) 
VALUES 
  (icatid
  ,'GRB'
  ,'Gamma Ray Bursts Catalog'
  )
;

/*SET iband = getBand(i_freq_eff);*/

CREATE TABLE aux_catalogedsources
  (aorig_catsrcid INT
  ,aname VARCHAR(14)
  ,afreq_eff DOUBLE
  ,aRAJ2000 DOUBLE
  ,aDEJ2000 DOUBLE
  ,ae_RAJ2000 DOUBLE
  ,ae_DEJ2000 DOUBLE
  ) 
;

COPY 1 RECORDS
INTO aux_catalogedsources
/*
FROM '/scratch/bscheers/databases/catalogs/nvss/csv/nvss-all.csv'
FROM '/home/bscheers/databases/catalogs/nvss/nvss-all.csv'
FROM '/home/bscheers/tkp-code/pipe/database/catfiles/nvss/nvss-all.csv'
FROM '/home/bscheers/tkp-code/pipe/database/catfiles/nvss/nvss-few.csv'
FROM '/home/bscheers/tkp-code/pipe/database/catfiles/nvss/nvss-all-nov2009sp2.csv'
FROM '/Users/bart/databases/catalogs/nvss/nvss-all.csv'
FROM '/home/scheers/tkp-code/pipe/database/catfiles/nvss/nvss-few.csv'
*/
FROM '/home/scheers/tkp-code/pipe/database/catfiles/grb/grb-all.csv'
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
  )
  SELECT aorig_catsrcid
        ,aname
        ,icatid
        ,getBand(afreq_eff)
        ,aRAJ2000
        ,aDEJ2000
        ,CAST(FLOOR(aDEJ2000) AS INTEGER)
        ,ae_RAJ2000
        ,ae_DEJ2000
        ,afreq_eff
        ,COS(radians(aDEJ2000)) * COS(radians(aRAJ2000))
        ,COS(radians(aDEJ2000)) * SIN(radians(aRAJ2000))
        ,SIN(radians(aDEJ2000))
    FROM aux_catalogedsources
  ;

DROP TABLE aux_catalogedsources;

--SELECT NOW();
