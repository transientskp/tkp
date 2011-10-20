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

SET @catid = 4;

INSERT INTO catalogues
  (catid
  ,catname
  ,fullname
  ) VALUES 
  (@catid
  ,'FEW WENSS'
  ,'few wenss in B1950 coordinates'
  )
;

LOAD DATA INFILE '/home/bscheers/databases/catalogues/wenss/wenss-few.csv'
INTO TABLE cataloguedsources 
FIELDS TERMINATED BY ';' 
LINES TERMINATED BY '\n' 
  (@dummy
  ,@dummy
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
  ,@dummy
  ) 
SET 
   orig_catsrcid = @orig_catsrcid
  ,catsrcname = CONCAT(@name, @f_name)
  ,cat_id = @catid
  ,band = 1
  ,freq_eff = 327000000
  ,ra = ra2deg(@wsrt_RAB1950)
  ,decl = decl2deg(@wsrt_DEB1950)
  ,zone = FLOOR(decl)
  ,ra_err = 54/7200
  ,decl_err = 54/(7200*SIN(RADIANS(decl)))
  ,x = COS(RADIANS(decl)) * COS(RADIANS(ra))
  ,y = COS(RADIANS(decl)) * SIN(RADIANS(ra))
  ,z = SIN(RADIANS(decl))
  ,i_peak_avg = @I/1000
  ,i_peak_avg_err = @rms/1000
  ,i_int_avg = @S/1000
  ,i_int_avg_err = @rms/1000
;

