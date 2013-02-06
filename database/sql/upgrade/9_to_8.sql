UPDATE version
   SET value = 8
 WHERE name = 'revision'
   AND value = 9
; %SPLIT%

DROP FUNCTION insertImage; %SPLIT%
DROP FUNCTION getSkyRgn; %SPLIT%
DROP FUNCTION updateSkyRgnMembers; %SPLIT%
DROP FUNCTION cartesian; %SPLIT%

ALTER TABLE IMAGE DROP CONSTRAINT "image_skyrgn_fkey"; %SPLIT%
ALTER TABLE IMAGE DROP COLUMN skyrgn; %SPLIT%

DROP TABLE assocskyrgn; %SPLIT%
DROP TABLE skyregion; %SPLIT%
DROP SEQUENCE seq_skyregion; %SPLIT%


CREATE FUNCTION insertImage(idataset INT
                           ,itau_time DOUBLE
                           ,ifreq_eff DOUBLE
                           ,ifreq_bw DOUBLE
                           ,itaustart_ts TIMESTAMP
                           ,ibeam_maj DOUBLE
                           ,ibeam_min DOUBLE
                           ,ibeam_pa DOUBLE
                           ,iurl VARCHAR(1024)
                           ,icentre_ra DOUBLE
                           ,icentre_decl DOUBLE
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
    ,centre_ra
    ,centre_decl
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
    ,icentre_ra
    ,icentre_decl
    )
  ;

  SET oimageid = iimageid;
  RETURN oimageid;

END;


