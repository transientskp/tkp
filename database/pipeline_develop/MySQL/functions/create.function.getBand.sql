DROP FUNCTION IF EXISTS getBand;

DELIMITER //

CREATE FUNCTION getBand(ifreq_eff DOUBLE
                       ,ibandwidth DOUBLE
                       ) RETURNS INT
DETERMINISTIC
BEGIN

  DECLARE ofreqbandid INT DEFAULT NULL;

  SELECT CASE WHEN COUNT(*) = 0
              THEN NULL
              ELSE freqbandid
         END
    INTO ofreqbandid
    FROM frequencybands
   WHERE ifreq_eff BETWEEN freq_low 
                       AND freq_high
  ;
  
  IF ofreqbandid IS NULL THEN
    INSERT INTO frequencybands
      (freq_low
      ,freq_central
      ,freq_high
      ) 
    VALUES
      (ifreq_eff - (ibandwidth / 2)
      ,ifreq_eff
      ,ifreq_eff + (ibandwidth / 2)
      )
    ;
    SELECT LAST_INSERT_ID() INTO ofreqbandid;
  END IF;

  RETURN ofreqbandid;

END;
//

DELIMITER ;
