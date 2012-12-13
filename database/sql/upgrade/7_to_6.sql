<<<<<<< HEAD
UPDATE version 
   SET value = 5
 WHERE name = 'revision'
   AND value = 6
;

ALTER TABLE extractedsource DROP COLUMN ra_fit_err;
ALTER TABLE extractedsource DROP COLUMN decl_fit_err;
ALTER TABLE extractedsource DROP COLUMN ra_sys_err;
ALTER TABLE extractedsource DROP COLUMN decl_sys_err;
=======
DROP FUNCTION insertImage; %SPLIT%

CREATE FUNCTION insertImage(idataset INT
                           ,itau_time DOUBLE
                           ,ifreq_eff DOUBLE
                           ,ifreq_bw DOUBLE
                           ,itaustart_ts TIMESTAMP
                           ,ibeam_maj DOUBLE
                           ,ibeam_min DOUBLE
                           ,ibeam_pa DOUBLE
                           ,iurl VARCHAR(1024)
                           ) RETURNS INT
BEGIN

  DECLARE iimageid INT;
  DECLARE oimageid INT;
  DECLARE iband SMALLINT;
  DECLARE itau INT;

  SET iband = getBand(ifreq_eff, ifreq_bw);

  SELECT NEXT VALUE FOR seq_image INTO iimageid;

  INSERT INTO image
    (id
    ,dataset
    ,band
    ,tau_time
    ,freq_eff
    ,freq_bw
    ,taustart_ts
    ,bmaj_syn
    ,bmin_syn
    ,bpa_syn
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
    ,ibeam_maj
    ,ibeam_min
    ,ibeam_pa
    ,iurl
    )
  ;

  SET oimageid = iimageid;
  RETURN oimageid;

END; %SPLIT%

>>>>>>> 0b0be59... adjusted insertImage function to support phasecentre
