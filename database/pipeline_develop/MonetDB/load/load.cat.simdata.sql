DECLARE icatid INT;
DECLARE i_freq_eff DOUBLE;
DECLARE iband INT;
--SET icatid = 6;
SET icatid = 11;

--SELECT NOW();

INSERT INTO catalogs
  (catid
  ,catname
  ,fullname
  ) 
VALUES 
  (icatid
  ,'SIMDATA'
  ,'325MHz VLA GCRT Sim. data ch3'
  )
;

SET i_freq_eff = 325000000.0;
/*SET iband = getBand(i_freq_eff, 10000000.0);*/
SET iband = getBand(i_freq_eff);

CREATE TABLE aux_catalogedsources
  (aorig_catsrcid INT
  ,aRA DOUBLE
  ,aDEC DOUBLE
  ,aFlux DOUBLE
  ,aFlux_sig DOUBLE
  ) 
;

COPY 64 RECORDS
INTO aux_catalogedsources
/*
FROM '/scratch/bscheers/tkp-code/pipe/database/catfiles/simcat/simdata-all.csv'
*/
FROM '/home/scheers/tkp-code/pipe/database/catfiles/simcat/simdata-all.csv'
USING DELIMITERS ';', '\n'
NULL AS ''
;

/* So we can put our FoV conditions in here...*/
INSERT INTO catalogedsources
  (orig_catsrcid
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
  ,i_int_avg
  ,i_int_avg_err
  )
  SELECT aorig_catsrcid
        ,icatid
        ,iband
        ,aRA
        ,aDEC
        ,CAST(FLOOR(aDEC) AS INTEGER)
        ,1
        ,1
        ,i_freq_eff
        ,COS(radians(aDEC)) * COS(radians(aRA))
        ,COS(radians(aDEC)) * SIN(radians(aRA))
        ,SIN(radians(aDEC))
        ,aFlux
        ,aFlux_sig
    FROM aux_catalogedsources
  ;

DROP TABLE aux_catalogedsources;

--SELECT NOW();
