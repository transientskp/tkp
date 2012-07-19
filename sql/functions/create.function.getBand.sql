--DROP FUNCTION getBand;

CREATE FUNCTION getBand(ifreq_eff DOUBLE) RETURNS SMALLINT

BEGIN
  
  DECLARE nfreqbandid INT;
  DECLARE ifreqbandid, ofreqbandid SMALLINT;
  DECLARE ibandwidth DOUBLE;

  /* For now, we default the bandwidth of a new band to 2MHz */
  SET ibandwidth = 2000000;

  SELECT COUNT(*)
    INTO nfreqbandid
    FROM frequencyband
   WHERE freq_low <= ifreq_eff
     AND freq_high >= ifreq_eff
  ;
  
  IF nfreqbandid = 1 THEN
    SELECT id
      INTO ifreqbandid
      FROM frequencyband
     WHERE freq_low <= ifreq_eff
       AND freq_high >= ifreq_eff
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

END;

