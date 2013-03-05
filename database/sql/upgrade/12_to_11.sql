UPDATE version
   SET value = 11
 WHERE name = 'revision'
   AND value = 12
; %SPLIT%

DROP FUNCTION insertImage; %SPLIT%
DROP FUNCTION getBand; %SPLIT%



CREATE FUNCTION getBand(ifreq_eff DOUBLE
                       ,ibandwidth DOUBLE
                       ) RETURNS SMALLINT

BEGIN

  DECLARE nfreqbandid INT;
  DECLARE ifreqbandid, ofreqbandid SMALLINT;

  SELECT COUNT(*)
    INTO nfreqbandid
    FROM frequencyband
   WHERE freq_low <= ifreq_eff - (ibandwidth / 2)
     AND freq_high >= ifreq_eff + (ibandwidth /2)
  ;

  IF nfreqbandid = 1 THEN
    SELECT id
      INTO ifreqbandid
      FROM frequencyband
     WHERE freq_low <= ifreq_eff - (ibandwidth / 2)
       AND freq_high >= ifreq_eff + (ibandwidth / 2)
    ;
  ELSE
    SELECT NEXT VALUE FOR seq_frequencyband INTO ifreqbandid;
    INSERT INTO frequencyband
      (id
      ,freq_central
      ,freq_low
      ,freq_high
      )
    VALUES
      (ifreqbandid
      ,ifreq_eff
      ,ifreq_eff - (ibandwidth / 2)
      ,ifreq_eff + (ibandwidth / 2)
      )
    ;
  END IF;

  SET ofreqbandid = ifreqbandid;
  RETURN ofreqbandid;

END;  %SPLIT%


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

