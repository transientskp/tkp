SET @catid = 4;

INSERT INTO catalogs
  (catid
  ,catname
  ,fullname
  ) 
VALUES 
  (@catid
  ,'VLSS'
  ,'The VLA Low-frequency Sky Survey at 74MHz, The VLSS Catalog, Version 2007-06-26'
  )
;

SET @freq_eff = 74000000;
SET @band = getBand(@freq_eff, 2000000);

/*LOAD DATA INFILE '/scratch/bscheers/databases/catalogs/vlss/csv/vlss-all.csv'*/
LOAD DATA INFILE '/home/bscheers/databases/catalogs/vlss/vlss-all.csv'
/*LOAD DATA INFILE '/Users/bart/databases/catalogs/vlss/vlss-all.csv'*/
INTO TABLE catalogedsources 
FIELDS TERMINATED BY ';' 
LINES TERMINATED BY '\n' 
  (@viz_RAJ2000
  ,@viz_DEJ2000
  ,@orig_catsrcid
  ,@name
  ,@RA
  ,@e_RA
  ,@decl
  ,@e_decl
  ,@Si
  ,@e_Si
  ,@l_MajAx
  ,@MajAx
  ,@e_MajAx
  ,@l_MinAx
  ,@MinAx
  ,@e_MinAx
  ,@PA
  ,@e_PA
  ,@dummy
  ,@dummy
  ,@dummy
  ,@dummy
  ) 
SET 
   orig_catsrcid = @orig_catsrcid
  ,catsrcname = TRIM(@name) 
  ,cat_id = @catid
  ,band = @band
  ,freq_eff = @freq_eff
  ,ra = @viz_RAJ2000
  ,decl = @viz_DEJ2000
  ,zone = FLOOR(decl)
  ,ra_err = 15 * @e_ra -- errors are given in sec (h:m:s), and NOT in arcsec
  ,decl_err = @e_decl 
  ,x = COS(RADIANS(decl)) * COS(RADIANS(ra))
  ,y = COS(RADIANS(decl)) * SIN(RADIANS(ra))
  ,z = SIN(RADIANS(decl))
  ,i_int_avg = @Si
  ,i_int_avg_err = @e_Si
  ,pa = @PA
  ,pa_err = @e_PA
  ,major = @MajAx 
  ,major_err = @e_MajAx
  ,minor = @MinAx
  ,minor_err = @e_MinAx 
;

