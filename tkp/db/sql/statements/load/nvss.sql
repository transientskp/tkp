{% ifdb monetdb %}
DECLARE i_freq_eff_nvss DOUBLE PRECISION;
DECLARE iband INT;
DECLARE iname VARCHAR(50);
SET iname = 'NVSS';
SET i_freq_eff_nvss = 1400000000.0;
SET iband = getBand(i_freq_eff_nvss, 26000000);
{% endifdb %}


{% ifdb postgresql %}
DO $$
DECLARE i_freq_eff_nvss DOUBLE PRECISION;
DECLARE iband INT;
DECLARE iname VARCHAR(50);
BEGIN
iname := 'NVSS';
i_freq_eff_nvss := 1400000000.0;
iband := getBand(i_freq_eff_nvss, 26000000);
{% endifdb %}


INSERT INTO catalog
  (name
  ,fullname
  ) 
VALUES 
  (iname
  ,'The NRAO VLA Sky Survey at 1.4 GHz'
  )
;

CREATE TABLE aux_catalogedsource
  (aviz_RAJ2000 DOUBLE PRECISION
  ,aviz_DEJ2000 DOUBLE PRECISION
  ,aorig_catsrcid INT
  ,afield VARCHAR(8)
  ,axpos DOUBLE PRECISION
  ,aypos DOUBLE PRECISION
  ,aname VARCHAR(14)
  ,aRAJ2000 VARCHAR(11)
  ,aDEJ2000 VARCHAR(11)
  ,ae_RAJ2000 DOUBLE PRECISION
  ,ae_DEJ2000 DOUBLE PRECISION
  ,aS1400 DOUBLE PRECISION
  ,ae_S1400 DOUBLE PRECISION
  ,al_MajAxis CHAR(1)
  ,aMajAxis DOUBLE PRECISION
  ,al_MinAxis CHAR(1)
  ,aMinAxis DOUBLE PRECISION
  ,aPA DOUBLE PRECISION
  ,ae_MajAxis DOUBLE PRECISION
  ,ae_MinAxis DOUBLE PRECISION
  ,ae_PA DOUBLE PRECISION
  ,af_resFlux VARCHAR(2)
  ,aresFlux DOUBLE PRECISION
  ,apolFlux DOUBLE PRECISION
  ,apolPA DOUBLE PRECISION
  ,ae_polFlux DOUBLE PRECISION
  ,ae_polPA DOUBLE PRECISION
  ,aImage VARCHAR(5)
  ) 
;


{% ifdb monetdb %}
COPY 1773484 RECORDS
INTO aux_catalogedsource
FROM
'%NVSS%'
USING DELIMITERS ';', '\n'
NULL AS ''
;
{% endifdb %}


{% ifdb postgresql %}
COPY
aux_catalogedsource
FROM
'%NVSS%'
USING DELIMITERS ';'
NULL AS ''
;
{% endifdb %}


/* So we can put our FoV conditions in here...*/
INSERT INTO catalogedsource
  (orig_catsrcid
  ,catsrcname
  ,catalog
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
  ,avg_f_int
  ,avg_f_int_err
  ,frame
  )
  SELECT aorig_catsrcid
        ,CONCAT('J', aname)
        ,c0.id
        ,iband
        ,aviz_RAJ2000
        ,aviz_DEJ2000
        ,CAST(FLOOR(aviz_DEJ2000) AS INTEGER)
        ,15 * ae_RAJ2000 * COS(RADIANS(aviz_DEJ2000))
        ,ae_DEJ2000 
        ,i_freq_eff_nvss
        ,COS(RADIANS(aviz_DEJ2000)) * COS(RADIANS(aviz_RAJ2000))
        ,COS(RADIANS(aviz_DEJ2000)) * SIN(RADIANS(aviz_RAJ2000))
        ,SIN(RADIANS(aviz_DEJ2000))
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
    FROM aux_catalogedsource c1
        ,catalog c0
   WHERE c0.name = 'NVSS'
  ;

DROP TABLE aux_catalogedsource;



{% ifdb postgresql %}
END;
$$;
{% endifdb %}