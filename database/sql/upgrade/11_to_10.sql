UPDATE version
   SET value = 10
 WHERE name = 'revision'
   AND value = 11
; %SPLIT%

DROP FUNCTION insertImage; %SPLIT%

ALTER TABLE image ADD COLUMN bmaj_syn DOUBLE NULL; %SPLIT%
ALTER TABLE image ADD COLUMN bmin_syn DOUBLE NULL; %SPLIT%
ALTER TABLE image ADD COLUMN bpa_syn DOUBLE NULL; %SPLIT%

UPDATE image
   SET bmaj_syn = rb_smaj 
      ,bmin_syn = rb_smin
      ,bpa_syn = rb_pa
; %SPLIT%

UPDATE image
   SET bmaj_syn = NULL
 WHERE bmaj_syn = 0
; %SPLIT%

UPDATE image
   SET bmin_syn = NULL
 WHERE bmin_syn = 0
; %SPLIT%

UPDATE image
   SET bpa_syn = NULL
 WHERE bpa_syn = 0
; %SPLIT%

ALTER TABLE image DROP COLUMN rb_smaj; %SPLIT%
ALTER TABLE image DROP COLUMN rb_smin; %SPLIT%
ALTER TABLE image DROP COLUMN rb_pa; %SPLIT%

CREATE FUNCTION insertImage(idataset INT
                           ,itau_time DOUBLE
                           ,ifreq_eff DOUBLE
                           ,ifreq_bw DOUBLE
                           ,itaustart_ts TIMESTAMP
                           ,ibeam_maj DOUBLE
                           ,ibeam_min DOUBLE
                           ,ibeam_pa DOUBLE
                           ,ideltax DOUBLE
                           ,ideltay DOUBLE
                           ,iurl VARCHAR(1024)
                           ,icentre_ra DOUBLE
                           ,icentre_decl DOUBLE
                           ,ixtr_radius DOUBLE
                           ) RETURNS INT
BEGIN

  DECLARE iimageid INT;
  DECLARE oimageid INT;
  DECLARE iband SMALLINT;
  DECLARE itau INT;
  DECLARE iskyrgn INT;

  SET iband = getBand(ifreq_eff, ifreq_bw);
  SET iskyrgn = getSkyRgn(idataset, icentre_ra, icentre_decl, ixtr_radius);
  
  SELECT NEXT VALUE FOR seq_image INTO iimageid;

  INSERT INTO image
    (id
    ,dataset
    ,band
    ,tau_time
    ,freq_eff
    ,freq_bw
    ,taustart_ts
    ,skyrgn
    ,bmaj_syn
    ,bmin_syn
    ,bpa_syn
    ,deltax
    ,deltay
    ,url
    )
  VALUES
    (iimageid
    ,idataset
    ,iband
    ,itau_time
    ,ifreq_eff
    ,ifreq_bw
    ,itaustart_ts
    ,iskyrgn
    ,ibeam_maj
    ,ibeam_min
    ,ibeam_pa
    ,ideltax
    ,ideltay
    ,iurl
    )
  ;

  SET oimageid = iimageid;
  RETURN oimageid;

END;  %SPLIT%
