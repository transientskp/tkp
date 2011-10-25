DECLARE icatid INT;
DECLARE i_freq_eff DOUBLE;
DECLARE iband INT;
SET icatid = 7;

INSERT INTO catalogs
  (catid
  ,catname
  ,fullname
  ) 
VALUES 
  (icatid
  ,'SkyCat'
  ,'Sky Catalog'
  )
;

SET i_freq_eff = 60E6;
SET iband = getBand(i_freq_eff);

CREATE TABLE aux_catalogedsources
  (aorig_catsrcid INT
  ,aname VARCHAR(14)
  ,asrc_type VARCHAR(14)
  ,aRAJ2000 VARCHAR(12)
  ,aDEJ2000 VARCHAR(13)
  ,aI DOUBLE
  ,aQ DOUBLE
  ,aU DOUBLE
  ,aV DOUBLE
  ,aspectralindexdegree INT
  ,c0 DOUBLE
  ,c1 DOUBLE
  ,c2 DOUBLE
  ,c3 DOUBLE
  ,c4 DOUBLE
  ,c5 DOUBLE
  ,aMajAxis DOUBLE
  ,aMinAxis DOUBLE
  ,aPA DOUBLE
  ) 
;

COPY 9 RECORDS
INTO aux_catalogedsources
FROM '/home/scheers/tkp-code/pipe/database/catfiles/skycat/skycat-all.csv'
USING DELIMITERS ',', '\n'
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
  ,pa
  ,major
  ,minor
  ,i_int_avg
  /*,q_int_avg
  ,u_int_avg
  ,v_int_avg*/
  )
  SELECT aorig_catsrcid
        ,aname
        ,icatid
        ,iband
        ,ra2degrees(aRAJ2000)
        ,decl2degrees(aDEJ2000)
        ,CAST(FLOOR(aDEJ2000) AS INTEGER)
        ,0.01
        ,0.01
        ,i_freq_eff
        ,COS(radians(aDEJ2000)) * COS(radians(aRAJ2000))
        ,COS(radians(aDEJ2000)) * SIN(radians(aRAJ2000))
        ,SIN(radians(aDEJ2000))
        /*,asrc_type*/
        ,aPA
        ,aMajAxis
        ,aMinAxis
        ,aI
        /*,aQ
        ,aU
        ,aV*/
    FROM aux_catalogedsources
;

INSERT INTO spectralindices
  (catsrc_id
  ,spindx_degree
  ,c0
  ,c1
  ,c2
  ,c3
  ,c4
  ,c5
  )
  SELECT c1.catsrcid
        ,CASE WHEN ac1.aspectralindexdegree IS NULL
              THEN 0
              ELSE ac1.aspectralindexdegree
         END
        ,CASE WHEN ac1.c0 IS NULL 
              THEN 0
              ELSE ac1.c0
         END 
        ,ac1.c1
        ,ac1.c2
        ,ac1.c3
        ,ac1.c4
        ,ac1.c5
    FROM aux_catalogedsources ac1
        ,catalogedsources c1
   WHERE ac1.aorig_catsrcid = c1.orig_catsrcid
     AND c1.cat_id = icatid
;    


DROP TABLE aux_catalogedsources;

