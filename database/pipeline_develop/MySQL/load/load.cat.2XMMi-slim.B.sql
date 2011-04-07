/*+-------------------------------------------------------------------+
 *| This script loads the 2XMMi slim version of the catalog.          |
 *| http://xmmssc-www.star.le.ac.uk/Catalogue/xcat_public_2XMMi.html  |
 *+-------------------------------------------------------------------+
 *| Bart Scheers                                                      |
 *| 2008-03-03                                                        |
 *+-------------------------------------------------------------------+
 *| Open Questions:                                                   |
 *+-------------------------------------------------------------------+
 */
--SELECT NOW();

SET @catid = 5;

INSERT INTO catalogs
  (catid
  ,catname
  ,fullname
  ) VALUES 
  (@catid
  ,'2XMMi slim'
  ,'2XMMi slim'
  )
;

LOAD DATA INFILE '/home/bscheers/databases/catalogues/2XMMi/2XMMicat_slim_v1.0.csv'
INTO TABLE catalogedsources 
FIELDS TERMINATED BY ',' 
LINES TERMINATED BY '\n' 
  (@SRCID
  ,@IAUNAME
  ,@SC_RA
  ,@SC_DEC
  ,@SC_POSERR
  ,@SC_EP_1_FLUX
  ,@SC_EP_1_FLUX_ERR
  ,@SC_EP_2_FLUX
  ,@SC_EP_2_FLUX_ERR
  ,@SC_EP_3_FLUX
  ,@SC_EP_3_FLUX_ERR
  ,@SC_EP_4_FLUX
  ,@SC_EP_4_FLUX_ERR
  ,@SC_EP_5_FLUX
  ,@SC_EP_5_FLUX_ERR
  ,@SC_EP_8_FLUX
  ,@SC_EP_8_FLUX_ERR
  ,@SC_EP_9_FLUX
  ,@SC_EP_9_FLUX_ERR
  ,@SC_HR1
  ,@SC_HR1_ERR
  ,@SC_HR2
  ,@SC_HR2_ERR
  ,@SC_HR3
  ,@SC_HR3_ERR
  ,@SC_HR4
  ,@SC_HR4_ERR
  ,@SC_DET_ML
  ,@SC_EXT_ML
  ,@SC_CHI2PROB
  ,@SC_VAR_FLAG
  ,@SC_SUM_FLAG
  ,@SC_CHFLAG1
  ,@N_DETECTIONS
  ,@MATCH_1XMM
  ,@SEP_1XMM
  ,@LEDAS_URL
  ) 
SET 
   orig_catsrcid = @SRCID
  ,catsrcname = @IAUNAME 
  ,cat_id = @catid
  ,band = 1
  ,freq_eff = 169E15  -- 0.2 - 12.0 keV
  ,ra = @SC_RA
  ,decl = @SC_DEC
  ,zone = FLOOR(decl)
  ,ra_err = @SC_POSERR/1800
  ,decl_err = ra_err
  ,x = COS(RADIANS(decl)) * COS(RADIANS(ra))
  ,y = COS(RADIANS(decl)) * SIN(RADIANS(ra))
  ,z = SIN(RADIANS(decl))
  ,i_int_avg = @SC_EP_8_FLUX / 1E-23
  ,i_int_avg_err = @SC_EP_8_FLUX_ERR / 1E-23
;

