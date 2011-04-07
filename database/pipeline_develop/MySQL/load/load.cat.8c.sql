SET @catid = 6;

INSERT INTO catalogs
  (catid
  ,catname
  ,fullname
  ) 
VALUES 
  (@catid
  ,'8C'
  ,'The revised Rees 38-MHz survey (Rees 1990, catalogue revised Hales et. al 1995).'
  )
;

LOAD DATA INFILE '/home/bscheers/databases/catalogues/8C/8C-all.csv'
INTO TABLE catalogedsources 
FIELDS TERMINATED BY ';' 
LINES TERMINATED BY '\n' 
  (@viz_Glon
  ,@viz_Glat
  ,@viz_RAJ2000
  ,@viz_DEJ2000
  ,@orig_catsrcid
  ,@RAB1950
  ,@DEB1950
  ,@SType
  /**
   * NOTE:
   * Speak is in Jy/bm and not in Jy
   */
  ,@Speak
  ,@Sinteg
  ,@Size
  ,@SN
  ,@AtlasNum
  ) 
SET 
   cat_id = @catid
  ,orig_catsrcid = @orig_catsrcid
  ,band = 3
  ,freq_eff = 38000000
  ,ra = @viz_RAJ2000
  ,decl = @viz_DEJ2000
  ,zone = FLOOR(decl)
  ,ra_err = 4.5 / 60
  ,decl_err = ra_err / SIN(RADIANS(decl))
  ,x = COS(RADIANS(decl)) * COS(RADIANS(ra))
  ,y = COS(RADIANS(decl)) * SIN(RADIANS(ra))
  ,z = SIN(RADIANS(decl))
--  ,det_sigma = @SN
  ,i_peak_avg = @Speak
  ,i_peak_avg_err = 1
  ,i_int_avg = @Sinteg
  ,i_int_avg_err = 1
;

