DECLARE i_freq_eff DOUBLE;
DECLARE iband INT;
DECLARE iname VARCHAR(50);

SET iname = 'EXO';

INSERT INTO catalog
  (name
  ,fullname
  ) 
VALUES 
  (iname
  ,'Exoplanets from exoplanet.eu and simbad (J.-M. Griessmeier)'
  )
;

CREATE TABLE aux_catalogedsource
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
INTO aux_catalogedsource
FROM 
'%EXO%'
USING DELIMITERS ';', '\n', '"'
NULL AS '""'
;

INSERT INTO catalogedsource
  (catalog
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
  ,avg_f_int
  ,avg_f_int_err
  )
  SELECT c0.id
        ,row_number() over()
        ,aorig_catsrcname 
        ,0
        ,0
        ,CAST(FLOOR(aDEJ2000) AS INTEGER)
        ,CAST(aRAJ2000 AS DOUBLE)
        ,CAST(aDEJ2000 AS DOUBLE)
        ,CAST(ae_RAJ2000 AS DOUBLE)
        ,CAST(ae_DEJ2000 AS DOUBLE)
        ,COS(RADIANS(CAST(aDEJ2000 AS DOUBLE))) * COS(RADIANS(CAST(aRAJ2000 AS DOUBLE)))
        ,COS(RADIANS(CAST(aDEJ2000 AS DOUBLE))) * SIN(RADIANS(CAST(aRAJ2000 AS DOUBLE)))
        ,SIN(RADIANS(CAST(aDEJ2000 AS DOUBLE)))
        ,CAST(aFlux AS DOUBLE)
        ,CAST(aFlux_err AS DOUBLE)
    FROM aux_catalogedsource c1
        ,catalog c0
   WHERE c0.name = iname
;

DROP TABLE aux_catalogedsource;

