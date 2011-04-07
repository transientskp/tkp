/*+-------------------------------------------------------------------+
 *| This script loads the pipeline.catalogues and -.cataloguesources  |
 *| tables with WENSS data.                                           |
 *| All WENSS data was subtracted as csv file from the vizier website.|
 *| The wenss-header.txt gives a description of the columns in the csv|
 *| file.                                                             |
 *+-------------------------------------------------------------------+
 *| Bart Scheers                                                      |
 *| 2008-09-24                                                        |
 *+-------------------------------------------------------------------+
 *| Open Questions:                                                   |
 *| (1) If we dump the default wenss data into a file, we can use that|
 *}     for even faster load.                                         |
 *+-------------------------------------------------------------------+
 */
DECLARE icatid INT;
DECLARE ifreq_eff_main, ifreq_eff_pole DOUBLE;
DECLARE iband_main, iband_pole INT;
SET icatid = 5;

--SELECT NOW();

INSERT INTO catalogs
  (catid
  ,catname
  ,fullname
  ) VALUES 
  (icatid
  ,'WENSS'
  ,'WEsterbork Nortern Sky Survey'
  )
;

SET ifreq_eff_main = 325000000.0;
SET iband_main = getBand(ifreq_eff_main, 10000000.0);
SET ifreq_eff_pole = 352000000.0;
SET iband_pole = getBand(ifreq_eff_pole, 10000000.0);


/*DROP TABLE aux_catalogedsources;*/

CREATE TABLE aux_catalogedsources
  (aviz_RAJ2000 DOUBLE
  ,aviz_DEJ2000 DOUBLE
  ,aorig_catsrcid INT
  ,aname VARCHAR(16)
  ,af_name VARCHAR(8)
  ,awsrt_RAB1950 VARCHAR(12)
  ,awsrt_DEB1950 VARCHAR(12)
  ,adummy1 VARCHAR(20)
  ,adummy2 VARCHAR(20)
  ,adummy3 VARCHAR(20)
  ,adummy4 VARCHAR(20)
  ,a_I DOUBLE
  ,a_S DOUBLE
  ,amajor DOUBLE
  ,aminor DOUBLE
  ,aPA DOUBLE
  ,arms DOUBLE
  ,aframe VARCHAR(20)
  )
;

COPY 229420 RECORDS 
INTO aux_catalogedsources 
/*FROM '/scratch/bscheers/databases/catalogs/wenss/csv/wenss-all.csv'*/
FROM '/home/bscheers/tkp-code/pipe/database/catfiles/wenss/wenss-all.csv'
/*FROM '/Users/bart/databases/catalogs/wenss/wenss-all.csv'*/
USING DELIMITERS ';', '\n' 
;

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
  ,major
  ,minor
  ,i_peak_avg
  ,i_peak_avg_err
  ,i_int_avg
  ,i_int_avg_err
  ,frame
  )
  SELECT aorig_catsrcid
        ,CONCAT(TRIM(aname), af_name)
        ,icatid
        ,CASE WHEN aframe LIKE 'WNH%'
              THEN iband_main
              ELSE iband_pole
         END
        ,aviz_RAJ2000
        ,aviz_DEJ2000
        ,CAST(FLOOR(aviz_DEJ2000) AS INTEGER)
        ,CASE WHEN a_I / arms >= 10 
              THEN 1.5
              ELSE CASE WHEN amajor <> 0
                        THEN SQRT(2.25 + arms * arms * (amajor * amajor * SIN(RADIANS(apa)) * SIN(RADIANS(apa)) + aminor * aminor * COS(RADIANS(apa)) * COS(RADIANS(apa))) / (1.69 * a_I * a_I))
                        ELSE SQRT(2.25 + arms * arms * 2916 / (1.69 * a_I * a_I))
                   END
         END
        ,CASE WHEN a_I / arms >= 10 
              THEN 1.5
              ELSE CASE WHEN amajor <> 0
                        THEN SQRT(2.25 + arms * arms * (amajor * amajor * COS(RADIANS(apa)) * COS(RADIANS(apa)) + aminor * aminor * SIN(RADIANS(apa)) * SIN(RADIANS(apa))) / (1.69 * a_I * a_I)) 
                        ELSE SQRT(2.25 + arms * arms * 2916 / (1.69 * a_I * a_I * SIN(RADIANS(aviz_DEJ2000)) * SIN(RADIANS(aviz_DEJ2000))))
                   END
         END
        ,CASE WHEN aframe LIKE 'WNH%'
              THEN ifreq_eff_main
              ELSE ifreq_eff_pole
         END
        ,COS(radians(aviz_DEJ2000)) * COS(radians(aviz_RAJ2000))
        ,COS(radians(aviz_DEJ2000)) * SIN(radians(aviz_RAJ2000))
        ,SIN(radians(aviz_DEJ2000))
        ,apa
        ,amajor
        ,aminor
        ,a_I / 1000
        ,arms / 1000
        ,a_S / 1000
        ,arms / 1000
        ,aframe
    FROM aux_catalogedsources
;

DROP TABLE aux_catalogedsources;

