--DROP FUNCTION getBand;

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

END;

