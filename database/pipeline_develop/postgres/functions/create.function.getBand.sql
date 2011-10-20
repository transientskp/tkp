--DROP FUNCTION getBand;

drop sequence seq_frequencybands;
create sequence seq_frequencybands;
CREATE or replace FUNCTION getBand(ifreq_eff double precision) RETURNS INT as $$

  DECLARE nfreqbandid int;
declare ifreqbandid int;
declare ofreqbandid INT;
  DECLARE ibandwidth double precision;
BEGIN
  

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
  ibandwidth := 10000000;

  SELECT COUNT(*)
    INTO nfreqbandid
    FROM frequencybands
   WHERE freq_low <= ifreq_eff
     AND freq_high >= ifreq_eff
  ;
  
  IF nfreqbandid <> 1
  THEN
    INSERT INTO frequencybands
      (
      freq_central
      ,freq_low
      ,freq_high
      ) VALUES
      (
      ifreq_eff
      ,ifreq_eff - (ibandwidth / 2)
      ,ifreq_eff + (ibandwidth / 2)
      )
    ;
  END IF;

    SELECT freqbandid
      INTO ifreqbandid
      FROM frequencybands
     WHERE freq_low <= ifreq_eff
       AND freq_high >= ifreq_eff
    ;

  ofreqbandid := ifreqbandid;
  RETURN ofreqbandid;

END;
$$ language plpgsql
;