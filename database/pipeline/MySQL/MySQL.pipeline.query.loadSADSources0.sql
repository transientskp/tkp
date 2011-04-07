USE pipeline;

/**
 * Because a stored procedure can not contain LOAD statements,
 * we have to create it here.
 * To test the source extraction algorithms we created fits files
 * in which sources where inserted with true position and flux.
 * These generated fits files all have a source in the middle, 
 * but a different (random) flux.
 * Every fits file gets his own cat_id 
 * (see MySQL.pipeline.procedure.CreateTrueCatalogues.sql).
 */
LOAD DATA INFILE 'SAD_test_reformatted_fin_def.csv'
INTO TABLE cataloguesources 
FIELDS TERMINATED BY ',' 
LINES TERMINATED BY '\n' 
  (@orig_catsrcid
  ,@i_peak_avg
  ,@i_peak_avg_err
  ,@i_peak_max
  ,@i_peak_max_err
  ,@ra
  ,@decl
  ,@ra_err
  ,@decl_err
  ,@dummy
  ,@dummy
  ,@dummy
  ,@dummy
  ,@dummy
  ,@dummy
  ) 
SET 
   orig_catsrcid = @orig_catsrcid
  ,cat_id = 4
  ,band = 1
  ,zone = FLOOR(@decl)
  ,freq_eff = 330000000
  ,ra = @ra
  ,decl = @decl
  ,ra_err = @ra_err
  ,decl_err = @decl_err
  ,x = COS(RADIANS(@decl)) * COS(RADIANS(@ra))
  ,y = COS(RADIANS(@decl)) * SIN(RADIANS(@ra))
  ,z = SIN(RADIANS(@decl))
  ,i_peak_avg = @i_peak_avg
  ,i_peak_avg_err = @i_peak_avg_err
  ,i_peak_max = @i_peak_max
  ,i_peak_max_err = @i_peak_max_err
;

