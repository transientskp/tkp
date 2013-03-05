UPDATE version
   SET value = 12
 WHERE name = 'revision'
   AND value = 11
; %SPLIT%

DROP FUNCTION insertImage; %SPLIT%
DROP FUNCTION getBand; %SPLIT%


CREATE FUNCTION getBand(ifreq_eff DOUBLE
                       ,ibandwidth DOUBLE
                       ) RETURNS SMALLINT

BEGIN

  DECLARE nfreqbandid INT;
  DECLARE ifreqbandid, ofreqbandid SMALLINT;

  -- We allow a small tolerance (of 1.0) to allow for rounding errors.
  SELECT COUNT(*)
    INTO nfreqbandid
    FROM frequencyband
   WHERE ABS(freq_central - ifreq_eff) <= 1.0
     AND ABS(freq_high - freq_low - ibandwidth) <= 1.0
  ;

  -- Due to the small tolerance above, in a corner case we might have two very
  -- similar bands which match our criteria. We arbitrarily choose one of
  -- them.
  IF nfreqbandid >= 1 THEN
    SELECT MAX(id)
      INTO ifreqbandid
      FROM frequencyband
     WHERE ABS(freq_central - ifreq_eff) <= 1.0
       AND ABS(freq_high - freq_low - ibandwidth) <= 1.0
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
