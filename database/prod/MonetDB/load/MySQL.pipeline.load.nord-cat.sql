USE pipeline;

LOAD DATA INFILE 'nord-1-241.txt'
INTO TABLE cataloguesources 
FIELDS TERMINATED BY ';' 
LINES TERMINATED BY '\n' 
  (@orig_catsrcid
  ,@catsrcname
  ,@RAh
  ,@RAm
  ,@RAs
  ,@DEd
  ,@DEm
  ,@DEs
  ,@I
  ,@rms
  ,@S
  ,@theta
  ,@offset
  ,@dummy
  ,@dummy
  ) 
SET 
   orig_catsrcid = @orig_catsrcid
  ,cat_id = 7
  ,band = 1
  ,freq_eff = 330000000
  ,ra = (((@RAs/60 + @RAm)/60 + @RAh) * 15) /*- 0.004163844713  Nord used NVSS to calibrate positions*/
  ,decl = (@DEd - ((@DEs/60 + @DEm)/60)) /*- 0.0059645023805 We know all @DEd in file are negative, quick and dirty*/
  ,zone = FLOOR(decl)
  ,ra_err = 0
  ,decl_err = 0
  ,x = COS(RADIANS(decl)) * COS(RADIANS(ra))
  ,y = COS(RADIANS(decl)) * SIN(RADIANS(ra))
  ,z = SIN(RADIANS(decl))
  ,i_peak_avg = @I
  ,i_peak_avg_err = @rms
  ,i_int_avg = @S
  ,i_int_avg_err = @rms
;

