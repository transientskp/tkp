DECLARE icatid INT;
DECLARE i_freq_eff DOUBLE;
DECLARE iband INT;
SET icatid = 4;

INSERT INTO catalog
  (catid
  ,catname
  ,fullname
  ) 
VALUES 
  (icatid
  ,'VLSS'
  ,'The VLA Low-frequency Sky Survey at 73.8MHz, The VLSS Catalog, Version 2007-06-26'
  )
;

SET i_freq_eff = 73800000;
/*SET iband = getBand(i_freq_eff, 2000000);*/
SET iband = getBand(i_freq_eff);

CREATE TABLE aux_catalogedsource
  (aviz_RAJ2000 DOUBLE
  ,aviz_DEJ2000 DOUBLE
  ,aorig_catsrcid INT
  ,aname VARCHAR(12)
  ,aRAJ2000 VARCHAR(11)
  ,ae_RAJ2000 DOUBLE
  ,aDEJ2000 VARCHAR(11)
  ,ae_DEJ2000 DOUBLE
  ,aSi DOUBLE
  ,ae_Si DOUBLE
  ,al_MajAx CHAR(1)
  ,aMajAx DOUBLE
  ,ae_MajAx DOUBLE
  ,al_MinAx CHAR(1)
  ,aMinAx DOUBLE
  ,ae_MinAx DOUBLE
  ,aPA DOUBLE
  ,ae_PA DOUBLE
  ,aField VARCHAR(8)
  ,aXpos INT
  ,aYpos INT
  ,aSPECFIND VARCHAR(8)
  )
;

COPY 68311 RECORDS
INTO aux_catalogedsource
FROM
'%VLSS%'
USING DELIMITERS ';', '\n'
NULL AS ''
;

/* So we can put our FoV conditions in here...*/
INSERT INTO catalogedsource
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
  ,avg_f_int
  ,avg_f_int_err
  ,frame
  )
  SELECT aorig_catsrcid
        ,TRIM(aname)
        ,icatid
        ,iband
        ,aviz_RAJ2000
        ,aviz_DEJ2000
        ,CAST(FLOOR(aviz_DEJ2000) AS INTEGER)
        ,15 * ae_RAJ2000 * COS(RADIANS(aviz_DEJ2000))
        ,ae_DEJ2000 
        ,i_freq_eff
        ,COS(RADIANS(aviz_DEJ2000)) * COS(RADIANS(aviz_RAJ2000))
        ,COS(RADIANS(aviz_DEJ2000)) * SIN(RADIANS(aviz_RAJ2000))
        ,SIN(RADIANS(aviz_DEJ2000))
        ,aPA
        ,ae_PA
        ,aMajAx
        ,ae_MajAx
        ,aMinAx
        ,ae_MinAx
        ,aSi
        ,ae_Si
        ,aSPECFIND
    FROM aux_catalogedsource
  ;

DROP TABLE aux_catalogedsource;

