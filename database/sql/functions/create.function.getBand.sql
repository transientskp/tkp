--DROP FUNCTION getBand;

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
    SELECT id
      INTO ifreqbandid
      FROM frequencyband
     WHERE freq_low <= ifreq_eff - (ibandwidth / 2)
       AND freq_high >= ifreq_eff + (ibandwidth / 2)
     LIMIT 1
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

