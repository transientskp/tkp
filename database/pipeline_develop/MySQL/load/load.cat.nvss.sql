SET @catid = 3;

INSERT INTO catalogs
  (catid
  ,catname
  ,fullname
  ) 
VALUES 
  (@catid
  ,'NVSS'
  ,'1.4GHz NRAO VLA Sky Survey (NVSS)'
  )
;

SET @freq_eff = 1400000000;
SET @band = getBand(@freq_eff, 10000000);

/*LOAD DATA INFILE '/scratch/bscheers/databases/catalogs/nvss/csv/nvss-all.csv'*/
LOAD DATA INFILE '/home/bscheers/databases/catalogs/nvss/nvss-all.csv'
/*LOAD DATA LOCAL INFILE '/home/scheers/databases/catalogs/nvss/nvss-all.csv'*/
/*LOAD DATA INFILE '/Users/bart/databases/catalogs/nvss/nvss-all.csv'*/
INTO TABLE catalogedsources 
FIELDS TERMINATED BY ';' 
LINES TERMINATED BY '\n' 
  (@viz_RAJ2000
  ,@viz_DEJ2000
  ,@orig_catsrcid
  ,@field
  ,@xpos
  ,@ypos
  ,@name
  ,@RAJ2000
  ,@DEJ2000
  ,@e_RAJ2000
  ,@e_DEJ2000
  ,@S1400
  ,@e_S1400
  ,@l_MajAxis
  ,@MajAxis
  ,@l_MinAxis
  ,@MinAxis
  ,@PA
  ,@e_MajAxis
  ,@e_MinAxis
  ,@e_PA
  ,@f_resFlux
  ,@resFlux
  ,@polFlux
  ,@e_polFlux
  ,@e_polPA
  ,@Image
  ) 
SET 
   cat_id = @catid
  ,orig_catsrcid = @orig_catsrcid
  ,catsrcname = CONCAT('NVSS J', @name)
  ,band = @band
  ,freq_eff = @freq_eff
  ,ra = @viz_RAJ2000
  ,decl = @viz_DEJ2000
  ,zone = FLOOR(decl)
  ,ra_err = 15 * @e_RAJ2000
  ,decl_err = @e_DEJ2000
  ,x = COS(RADIANS(decl)) * COS(RADIANS(ra))
  ,y = COS(RADIANS(decl)) * SIN(RADIANS(ra))
  ,z = SIN(RADIANS(decl))
  ,PA = IF(@PA < 0, @PA + 180, @PA)
  ,PA_err = @e_PA
  ,major = @MajAxis
  ,major_err = @e_MajAxis
  ,minor = @MinAxis
  ,minor_err = @e_MinAxis
  ,i_int_avg = @S1400 / 1000
  ,i_int_avg_err = @e_S1400 / 1000
  ,frame = @Image
;

