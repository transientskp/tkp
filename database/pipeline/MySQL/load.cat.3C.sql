USE pipeline_develop;

INSERT INTO catalogues
  (catid
  ,catname
  ,fullname
  ) VALUES 
  (3
  ,'3C'
  ,'3C'
  )
;

LOAD DATA INFILE '/home/bscheers/databases/catalogues/3C/3C-all.csv'
INTO TABLE cataloguesources 
FIELDS TERMINATED BY ';' 
LINES TERMINATED BY '\n' 
  (@viz_RAJ2000
  ,@viz_DEJ2000
  ,@orig_catsrcid
  ,@name
  ,@dummy
  ,@dummy
  ,@dummy
  ,@dummy
  ,@dummy
  ,@dummy
  ,@ra_err
  ,@dummy
  ,@dummy
  ,@decl_err
  ,@dummy
  ,@S159
  ,@S159_err
  ,@dummy
  ,@dummy
  ,@majaxis
  ,@majaxis_err
  ,@dummy
  ,@dummy
  ) 
SET 
   orig_catsrcid = @orig_catsrcid
  ,cat_id = 3
  ,band = 1
  ,freq_eff = 159000000
  ,ra = @viz_RAJ2000
  ,decl = @viz_DEJ2000
  ,zone = FLOOR(decl)
  ,ra_err = @ra_err/240
  ,decl_err = @decl_err/60
  ,x = COS(RADIANS(decl)) * COS(RADIANS(ra))
  ,y = COS(RADIANS(decl)) * SIN(RADIANS(ra))
  ,z = SIN(RADIANS(decl))
  ,i_int_avg = @S159
  ,i_int_avg_err = @S159_err
;

