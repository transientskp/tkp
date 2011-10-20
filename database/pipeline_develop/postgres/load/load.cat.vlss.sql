INSERT INTO catalogs
  (catid
  ,catname
  ,fullname
  ) 
VALUES 
  (4
  ,'VLSS'
  ,'The VLA Low-frequency Sky Survey at 73.8MHz, The VLSS Catalog, Version 2007-06-26'
  )
;

CREATE TABLE aux_catalogedsources
  (aviz_RAJ2000 double precision
  ,aviz_DEJ2000 double precision
  ,aorig_catsrcid INT
  ,aname VARCHAR(12)
  ,aRAJ2000 VARCHAR(11)
  ,ae_RAJ2000 double precision
  ,aDEJ2000 VARCHAR(11)
  ,ae_DEJ2000 double precision
  ,aSi double precision
  ,ae_Si double precision
  ,al_MajAx CHAR(1)
  ,aMajAx double precision
  ,ae_MajAx double precision
  ,al_MinAx CHAR(1)
  ,aMinAx double precision
  ,ae_MinAx double precision
  ,aPA double precision
  ,ae_PA double precision
  ,aField VARCHAR(8)
  ,aXpos INT
  ,aYpos INT
  ,aSPECFIND VARCHAR(8)
  )
;

COPY  aux_catalogedsources
FROM
/* '/scratch/scheers/tkp-code/pipe/database/catfiles/vlss/vlss-all_strip.csv' */
/* '/home/scheers/tkp-code/pipe/database/catfiles/vlss/VLSS-all_strip.csv' */
'/zfs/heastro-plex/scratch/evert/catfiles/VLSS-all_strip.csv'
/* '/export/scratch1/bscheers/code/pipe/database/catfiles/vlss/VLSS-all_strip.csv' */
/* '/data/scratch/rol/catalogs/VLSS-all_strip.csv' */
/* '/Users/evert/lofar/data/catalogs/VLSS-all_strip.csv' */
WITH delimiter as ';'
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
        ,TRIM(aname)
        ,4
        ,getBand(73800000)
        ,aviz_RAJ2000
        ,aviz_DEJ2000
        ,CAST(FLOOR(aviz_DEJ2000) AS INTEGER)
        /*,3600 * DEGREES(2 * ASIN(SQRT((COS(rad(aviz_DEJ2000)) * COS(rad(aviz_RAJ2000 + ae_RAJ2000 / 480)) - COS(rad(aviz_DEJ2000)) * COS(rad(aviz_RAJ2000)))
                                      *
                                      (COS(rad(aviz_DEJ2000)) * COS(rad(aviz_RAJ2000 + ae_RAJ2000 / 480)) - COS(rad(aviz_DEJ2000)) * COS(rad(aviz_RAJ2000)))
                                     +
                                      (COS(rad(aviz_DEJ2000)) * SIN(rad(aviz_RAJ2000 + ae_RAJ2000 / 480)) - COS(rad(aviz_DEJ2000)) * SIN(rad(aviz_RAJ2000)))
                                      *
                                      (COS(rad(aviz_DEJ2000)) * SIN(rad(aviz_RAJ2000 + ae_RAJ2000 / 480)) - COS(rad(aviz_DEJ2000)) * SIN(rad(aviz_RAJ2000)))
                                     ) / 2
                                )
                       )*/
        ,15 * ae_RAJ2000 * COS(rad(aviz_DEJ2000))
        ,ae_DEJ2000 
        ,73800000
        ,COS(rad(aviz_DEJ2000)) * COS(rad(aviz_RAJ2000))
        ,COS(rad(aviz_DEJ2000)) * SIN(rad(aviz_RAJ2000))
        ,SIN(rad(aviz_DEJ2000))
        ,aPA
        ,ae_PA
        ,aMajAx
        ,ae_MajAx
        ,aMinAx
        ,ae_MinAx
        ,aSi
        ,ae_Si
        ,aSPECFIND
    FROM aux_catalogedsources
  ;

DROP TABLE aux_catalogedsources;

