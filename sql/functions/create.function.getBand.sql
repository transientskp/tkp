--DROP FUNCTION getBand;

CREATE FUNCTION getBand(ifreq_eff DOUBLE) RETURNS INT

BEGIN
  
  DECLARE nfreqbandid, ifreqbandid, ofreqbandid INT;
  DECLARE ibandwidth DOUBLE;

  /* For now, we default the bandwidth of a new band to 10MHz */
  SET ibandwidth = 10000000;

  SELECT COUNT(*)
    INTO nfreqbandid
    FROM frequencyband
   WHERE freq_low <= ifreq_eff
     AND freq_high >= ifreq_eff
  ;
  
  IF nfreqbandid = 1 THEN
    SELECT freqbandid
      INTO ifreqbandid
      FROM frequencyband
     WHERE freq_low <= ifreq_eff
       AND freq_high >= ifreq_eff
    ;
  ELSE
    SELECT NEXT VALUE FOR seq_frequencyband INTO ifreqbandid;
    INSERT INTO frequencyband
      (freqbandid
      ,freq_central
      ,freq_low
      ,freq_high
      ) VALUES
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

