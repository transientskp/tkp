UPDATE version
   SET value = 11
 WHERE name = 'revision'
   AND value = 10
; %SPLIT%

DROP FUNCTION insertImage; %SPLIT%

ALTER TABLE image ADD COLUMN rb_smaj DOUBLE NULL; %SPLIT%
ALTER TABLE image ADD COLUMN rb_smin DOUBLE NULL; %SPLIT%
ALTER TABLE image ADD COLUMN rb_pa DOUBLE NULL; %SPLIT%

ALTER TABLE image ADD COLUMN temp_deltax DOUBLE NULL; %SPLIT%
ALTER TABLE image ADD COLUMN temp_deltay DOUBLE NULL; %SPLIT%
/* 
Although we know that the old values were incorrect due to wrong 
units and no stored conversion parameters, we copy them into 
the new columns.
TODO: Can we set those to rejected?
*/
UPDATE image
   SET bmaj_syn = 0
 WHERE bmaj_syn IS NULL
; %SPLIT%

UPDATE image
   SET bmin_syn = 0
 WHERE bmin_syn IS NULL
; %SPLIT%

UPDATE image
   SET bpa_syn = 0
 WHERE bpa_syn IS NULL
; %SPLIT%

UPDATE image
   SET rb_smaj = bmaj_syn
      ,rb_smin = bmin_syn
      ,rb_pa = bpa_syn
; %SPLIT%

UPDATE image
   SET deltax = 0
 WHERE deltax IS NULL
; %SPLIT%

UPDATE image
   SET deltay = 0
 WHERE deltay IS NULL
; %SPLIT%

UPDATE image
   SET temp_deltax = deltax
      ,temp_deltay = deltay
; %SPLIT%

ALTER TABLE image ALTER COLUMN rb_smaj SET NOT NULL; %SPLIT%
ALTER TABLE image ALTER COLUMN rb_smin SET NOT NULL; %SPLIT%
ALTER TABLE image ALTER COLUMN rb_pa SET NOT NULL; %SPLIT%

ALTER TABLE image ALTER COLUMN temp_deltax SET NOT NULL; %SPLIT%
ALTER TABLE image ALTER COLUMN temp_deltay SET NOT NULL; %SPLIT%

ALTER TABLE image DROP COLUMN bmaj_syn; %SPLIT%
ALTER TABLE image DROP COLUMN bmin_syn; %SPLIT%
ALTER TABLE image DROP COLUMN bpa_syn; %SPLIT%

ALTER TABLE image DROP COLUMN deltax; %SPLIT%
ALTER TABLE image DROP COLUMN deltay; %SPLIT%

ALTER TABLE image ADD COLUMN deltax DOUBLE NULL; %SPLIT%
ALTER TABLE image ADD COLUMN deltay DOUBLE NULL; %SPLIT%

UPDATE image
   SET deltax = temp_deltax
      ,deltay = temp_deltay
; %SPLIT%

ALTER TABLE image DROP COLUMN temp_deltax; %SPLIT%
ALTER TABLE image DROP COLUMN temp_deltay; %SPLIT%

ALTER TABLE image ALTER COLUMN deltax SET NOT NULL; %SPLIT%
ALTER TABLE image ALTER COLUMN deltay SET NOT NULL; %SPLIT%

CREATE FUNCTION insertImage(idataset INT
                           ,itau_time DOUBLE
                           ,ifreq_eff DOUBLE
                           ,ifreq_bw DOUBLE
                           ,itaustart_ts TIMESTAMP
                           ,irb_smaj DOUBLE
                           ,irb_smin DOUBLE
                           ,irb_pa DOUBLE
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
    ,rb_smaj
    ,rb_smin
    ,rb_pa
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
    ,irb_smaj
    ,irb_smin
    ,irb_pa
    ,ideltax
    ,ideltay
    ,iurl
    )
  ;

  SET oimageid = iimageid;
  RETURN oimageid;

END;  %SPLIT%
