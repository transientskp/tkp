DECLARE icatid INT;
DECLARE i_freq_eff DOUBLE;
DECLARE iband INT;
SET icatid = 7;

--SELECT NOW();

INSERT INTO catalogs
  (catid
  ,catname
  ,fullname
  ) 
VALUES 
  (icatid
  ,'EXO'
  ,'Exoplanets from exoplanet.eu and simbad (J.-M. Griessmeier)'
  )
;

/*SET i_freq_eff = 1400000000.0;
SET iband = getBand(i_freq_eff, 10000000.0);
SET iband = getBand(i_freq_eff);*/

CREATE TABLE aux_catalogedsources
  (aorig_catsrcname VARCHAR(25)
  ,aRAJ2000 VARCHAR(17)
  ,aDEJ2000 VARCHAR(19)
  ,ae_RAJ2000 VARCHAR(17)
  ,ae_DEJ2000 VARCHAR(17)
  ,aFreq VARCHAR(17)
  ,aFlux VARCHAR(17)
  ,aFlux_err VARCHAR(17)
  ) 
;

COPY 473 RECORDS
INTO aux_catalogedsources
/*
FROM '/scratch/bscheers/tkp-code/pipe/database/catfiles/nvss/nvss-few.csv'
FROM '${TKPDBCODE}/catfiles/nvss/nvss-all_strip.csv'
FROM '/home/scheers/tkp-code/pipe/database/catfiles/exoplanets/exoplanetDatabase.csv'
*/
FROM '/export/scratch1/bscheers/tkp-code/pipe/database/catfiles/exoplanets/exoplanetDatabase.csv'
USING DELIMITERS ';', '\n', '"'
NULL AS '""'
;

INSERT INTO catalogedsources
  (cat_id
  ,orig_catsrcid
  ,catsrcname
  ,band
  ,freq_eff
  ,zone
  ,ra
  ,decl
  ,ra_err
  ,decl_err
  ,x
  ,y
  ,z
  ,i_int_avg
  ,i_int_avg_err
  )
  SELECT icatid
        ,row_number() over()
        ,aorig_catsrcname 
        ,0
        ,0
        ,CAST(FLOOR(aDEJ2000) AS INTEGER)
        ,CAST(aRAJ2000 AS DOUBLE)
        ,CAST(aDEJ2000 AS DOUBLE)
        ,CAST(ae_RAJ2000 AS DOUBLE)
        ,CAST(ae_DEJ2000 AS DOUBLE)
        ,COS(radians(CAST(aDEJ2000 AS DOUBLE))) * COS(radians(CAST(aRAJ2000 AS DOUBLE)))
        ,COS(radians(CAST(aDEJ2000 AS DOUBLE))) * SIN(radians(CAST(aRAJ2000 AS DOUBLE)))
        ,SIN(radians(CAST(aDEJ2000 AS DOUBLE)))
        ,CAST(aFlux AS DOUBLE)
        ,CAST(aFlux_err AS DOUBLE)
    FROM aux_catalogedsources
  ;

DROP TABLE aux_catalogedsources;

--SELECT NOW();
