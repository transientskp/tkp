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
 *+-------------------------------------------------------------------+
 */
SET @catid = 5;

INSERT INTO catalogs
  (catid
  ,catname
  ,fullname
  ) VALUES 
  (@catid
  ,'WENSS'
  ,'WEsterbork Nortern Sky Survey'
  )
;

SET @freq_eff_main = 325000000;
SET @band_main = getBand(@freq_eff_main, 10000000);
SET @freq_eff_pole = 352000000;
SET @band_pole = getBand(@freq_eff_pole, 10000000);

/*LOAD DATA INFILE '/scratch/bscheers/databases/catalogs/wenss/csv/wenss-all.csv'*/
LOAD DATA INFILE '/home/bscheers/databases/catalogs/wenss/wenss-all.csv'
/*LOAD DATA INFILE '/Users/bart/databases/catalogs/wenss/wenss-all.csv'*/
INTO TABLE catalogedsources 
FIELDS TERMINATED BY ';' 
LINES TERMINATED BY '\n' 
  (@viz_RAJ2000
  ,@viz_DEJ2000
  ,@orig_catsrcid
  ,@name
  ,@f_name
  ,@wsrt_RAB1950
  ,@wsrt_DEB1950
  ,@dummy
  ,@dummy
  ,@dummy
  ,@dummy
  ,@I
  ,@S
  ,@major
  ,@minor
  ,@PA
  ,@rms
  ,@frame
  ) 
SET 
   orig_catsrcid = @orig_catsrcid
  ,catsrcname = CONCAT(TRIM(@name), @f_name)
  ,cat_id = @catid
  ,band = IF(@frame LIKE 'WNH%', @band_main, @band_pole)
  ,ra = @viz_RAJ2000
  ,decl = @viz_DEJ2000
  ,zone = FLOOR(decl)
  ,ra_err = 27
  ,decl_err = 27 / SIN(RADIANS(decl))
  ,freq_eff = IF(@frame LIKE 'WNH%', @freq_eff_main, @freq_eff_pole)
  ,x = COS(RADIANS(decl)) * COS(RADIANS(ra))
  ,y = COS(RADIANS(decl)) * SIN(RADIANS(ra))
  ,z = SIN(RADIANS(decl))
  ,pa = @pa
  ,major = @major
  ,minor = @minor 
  ,i_peak_avg = @I/1000
  ,i_peak_avg_err = @rms / 1000
  ,i_int_avg = @S/1000
  ,i_int_avg_err = @rms / 1000
  ,frame = @frame
;

