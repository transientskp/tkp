USE pipeline;

INSERT INTO catalogues
  (catid
  ,catname
  ,fullname
  ) VALUES 
  (2
  ,'wenss'
  ,'wenss'
  )
;

LOAD DATA INFILE '/scratch/bscheers/databases/catalogues/wenss/csv/wenss-all.csv'
INTO TABLE cataloguesources 
FIELDS TERMINATED BY ';' 
LINES TERMINATED BY '\n' 
  (@viz_RAJ2000
  ,@viz_DEJ2000
  ,@orig_catsrcid
  ,@name
  ,@f_name
  ,@dummy
  ,@dummy
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
  ,cat_id = 2
  ,band = 1
  ,freq_eff = 327000000
  ,ra = @viz_RAJ2000
  ,decl = @viz_DEJ2000
  ,zone = FLOOR(decl)
  ,ra_err = 54/7200
  ,decl_err = 54/(2*SIN(RADIANS(decl)))
  ,x = COS(RADIANS(decl)) * COS(RADIANS(ra))
  ,y = COS(RADIANS(decl)) * SIN(RADIANS(ra))
  ,z = SIN(RADIANS(decl))
  ,i_peak_avg = @I/1000
  ,i_peak_avg_err = @rms/1000
  ,i_int_avg = @S/1000
  ,i_int_avg_err = @rms/1000
;

