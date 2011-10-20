/*+-------------------------------------------------------------------+
 *| This script loads the external WENSS catalogue into the DB        |
 *| All WENSS data were subtracted from the csv file from the vizier  |
 *| website.The wenss-header.txt gives a description of the columns   |
 *| in the csv file.                                                  |
 *| The WENSS catalogue consists of two surveys:                      |
 *| (1) the main part, at 325 MHz, which contains the sources between |
 *|     28 < decl < 76                                                |
 *| (2) the polar part, at 352 MHz, which contains the sources with   |
 *|     decl > 72.                                                    |
 *| Therefore, we will create two separate WENSS catalogues, a main   |
 *| and polar part.                                                   |
 *+-------------------------------------------------------------------+
 *| Bart Scheers                                                      |
 *| 2011-02-16                                                        |
 *+-------------------------------------------------------------------+
 *| Open Questions/TODOs:                                             |
 *| (1) If we dump the default wenss data into a file, we can use that|
 *}     for even faster load.                                         |
 *+-------------------------------------------------------------------+
 */

INSERT INTO catalogs
  (catid
  ,catname
  ,fullname
  ) VALUES 
  (5
  ,'WENSSm'
  ,'WEsterbork Nortern Sky Survey, Main Catalogue @ 325 MHz'
  )
  ,
  (6
  ,'WENSSp'
  ,'WEsterbork Nortern Sky Survey, Polar Catalogue @ 352 MHz'
  )
;


/*DROP TABLE aux_catalogedsources;*/

CREATE TABLE aux_catalogedsources
  (aviz_RAJ2000 double precision
  ,aviz_DEJ2000 double precision
  ,aorig_catsrcid INT
  ,aname VARCHAR(16)
  ,af_name VARCHAR(8)
  ,awsrt_RAB1950 VARCHAR(12)
  ,awsrt_DEB1950 VARCHAR(12)
  ,adummy1 VARCHAR(20)
  ,adummy2 VARCHAR(20)
  ,aflg1 VARCHAR(2)
  ,aflg2 VARCHAR(1)
  ,a_I double precision
  ,a_S double precision
  ,amajor double precision
  ,aminor double precision
  ,aPA double precision
  ,arms double precision
  ,aframe VARCHAR(20)
  )
;

COPY  aux_catalogedsources 
FROM
/* '/scratch/scheers/tkp-code/pipe/database/catfiles/wenss/wenss-all_strip.csv' */
/* '/home/scheers/tkp-code/pipe/database/catfiles/wenss/WENSS-all_strip.csv' */
/* '/export/scratch1/bscheers/code/pipe/database/catfiles/wenss/WENSS-all_strip.csv' */
'/zfs/heastro-plex/scratch/evert/catfiles/WENSS-all_strip.csv'
/* '/data/scratch/rol/catalogs/WENSS-all_strip.csv' */
/* '/Users/evert/lofar/data/catalogs/WENSS-all_strip.csv' */
WITH DELIMITER as ';'
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
  ,src_type
  ,fit_probl
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
        ,TRIM(aname) || af_name
        ,CASE WHEN aframe LIKE 'WNH%'
              THEN 5
              ELSE 6
         END
        ,CASE WHEN aframe LIKE 'WNH%'
              THEN getBand(325000000.0)
              ELSE getBand(325000000.0)
         END
        ,aviz_RAJ2000
        ,aviz_DEJ2000
        ,CAST(FLOOR(aviz_DEJ2000) AS INTEGER)
        ,CASE WHEN a_I / arms >= 10 
              THEN 1.5
              ELSE CASE WHEN amajor <> 0
                        THEN SQRT(2.25 + arms * arms * (amajor * amajor * SIN(rad(apa)) * SIN(rad(apa)) 
                                                       + aminor * aminor * COS(rad(apa)) * COS(rad(apa))
                                                       ) / (1.69 * a_I * a_I))
                        ELSE SQRT(2.25 + arms * arms * 2916 / (1.69 * a_I * a_I))
                   END
         END
        ,CASE WHEN a_I / arms >= 10 
              THEN 1.5
              ELSE CASE WHEN amajor <> 0
                        THEN SQRT(2.25 + arms * arms * (amajor * amajor * COS(rad(apa)) * COS(rad(apa)) 
                                                       + aminor * aminor * SIN(rad(apa)) * SIN(rad(apa))
                                                       ) / (1.69 * a_I * a_I)) 
                        ELSE SQRT(2.25 + arms * arms * 2916 
                                 / (1.69 * a_I * a_I * SIN(rad(aviz_DEJ2000)) * SIN(rad(aviz_DEJ2000)))
                                 )
                   END
         END
        ,CASE WHEN aframe LIKE 'WNH%'
              THEN 325000000.0
              ELSE 325000000.0
         END
        ,COS(rad(aviz_DEJ2000)) * COS(rad(aviz_RAJ2000))
        ,COS(rad(aviz_DEJ2000)) * SIN(rad(aviz_RAJ2000))
        ,SIN(rad(aviz_DEJ2000))
        ,aflg1
        ,CASE WHEN aflg2 = '*'
              THEN aflg2
              ELSE NULL
         END
        ,apa
        ,amajor
        ,aminor
        ,a_I / 1000
        ,SQRT(0.0016 + 1.69 * (arms / a_I) * (arms / a_I)) * a_I / 1000
        ,a_S / 1000
        ,SQRT(0.0016 + 1.69 * (arms / a_S) * (arms / a_S)) * a_S / 1000
        ,aframe
    FROM aux_catalogedsources
   WHERE a_S > 0
--     AND af_name a_S > 0
;

DROP TABLE aux_catalogedsources;

