--DROP FUNCTION getBand;

CREATE FUNCTION getBand(ifreq_eff DOUBLE) RETURNS INT

BEGIN
  
  DECLARE nfreqbandid, ifreqbandid, ofreqbandid INT;
  DECLARE ibandwidth DOUBLE;

  /*Does not work properly
  SELECT CASE WHEN COUNT(*) = 0
              THEN NULL
              ELSE freqbandid
              END
    INTO ifreqbandid
    FROM frequencybands
   WHERE freq_low <= ifreq_eff
     AND freq_high >= ifreq_eff
  GROUP BY freqbandid
  ;
  */
  
  /* For now, we default the bandwidth of a new band to 10MHz */
  SET ibandwidth = 10000000;

  SELECT COUNT(*)
    INTO nfreqbandid
    FROM frequencybands
   WHERE freq_low <= ifreq_eff
     AND freq_high >= ifreq_eff
  ;
  
  IF nfreqbandid = 1 THEN
    SELECT freqbandid
      INTO ifreqbandid
      FROM frequencybands
     WHERE freq_low <= ifreq_eff
       AND freq_high >= ifreq_eff
    ;
  ELSE
    SELECT NEXT VALUE FOR seq_frequencybands INTO ifreqbandid;
    INSERT INTO frequencybands
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

