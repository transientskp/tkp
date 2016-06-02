--DROP FUNCTION getBand;

CREATE FUNCTION getBand(ifreq_eff DOUBLE PRECISION, ifreq_bw DOUBLE PRECISION, ifreq_bw_max DOUBLE PRECISION)
RETURNS SMALLINT

{% ifdb monetdb %}

BEGIN

  DECLARE nfreqbandid INT;
  DECLARE ifreqbandid SMALLINT;
  DECLARE ofreqbandid SMALLINT;
  DECLARE ifreq_bw_final DOUBLE PRECISION;

  --  a max bandwitdh can be specifief with ifreq_bw_max. If non zero ifreq_bw_max will override ifreq_bw which is
  --- used to deterimine which band the image is in.
  IF ifreq_bw_max == 0.0 THEN
    SELECT ifreq_bw INTO ifreq_bw_final;
  ELSE
    SELECT ifreq_bw_max INTO ifreq_bw_final;
  END IF;


  -- We allow a small tolerance (of 1.0) to allow for rounding errors.
  SELECT COUNT(*)
    INTO nfreqbandid
    FROM frequencyband
   WHERE ABS(freq_central - ifreq_eff) <= 1.0
     AND ABS(freq_high - freq_low - ifreq_bw_max) <= 1.0
  ;

  -- Due to the small tolerance above, in a corner case we might have two very
  -- similar bands which match our criteria. We arbitrarily choose one of
  -- them.
  IF nfreqbandid >= 1 THEN
    SELECT MAX(id)
      INTO ifreqbandid
      FROM frequencyband
     WHERE ABS(freq_central - ifreq_eff) <= 1.0
       AND ABS(freq_high - freq_low - ifreq_bw_max) <= 1.0
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
      ,ifreq_eff - (ifreq_bw_max / 2)
      ,ifreq_eff + (ifreq_bw_max / 2)
      )
    ;
  END IF;

  SET ofreqbandid = ifreqbandid;
  RETURN ofreqbandid;

END;

{% endifdb %}



{% ifdb postgresql %}

AS $$

  DECLARE nfreqbandid INT;
  DECLARE ifreqbandid SMALLINT;
  DECLARE ifreq_bw_final DOUBLE PRECISION;

BEGIN


  --  a max bandwitdh can be specifief with ifreq_bw_max. If non zero ifreq_bw_max will override ifreq_bw which is
  --- used to deterimine which band the image is in.
  IF ifreq_bw_max <= 0.01 THEN
    SELECT ifreq_bw INTO ifreq_bw_final;
  ELSE
    SELECT ifreq_bw_max INTO ifreq_bw_final;
  END IF;



  -- We allow a small tolerance (of 1.0) to allow for rounding errors.
  SELECT COUNT(*)
    INTO nfreqbandid
    FROM frequencyband
   WHERE ABS(freq_central - ifreq_eff) <= 1.0
     AND ABS(freq_high - freq_low - ifreq_bw_final) <= 1.0
  ;


  -- Due to the small tolerance above, in a corner case we might have two very
  -- similar bands which match our criteria. We arbitrarily choose one of
  -- them.
  IF nfreqbandid >= 1 THEN
    SELECT MAX(id)
      INTO ifreqbandid
      FROM frequencyband
     WHERE ABS(freq_central - ifreq_eff) <= 1.0
       AND ABS(freq_high - freq_low - ifreq_bw_final) <= 1.0
    ;
  ELSE
    INSERT INTO frequencyband
      (freq_central
      ,freq_low
      ,freq_high
      )
    VALUES
      (ifreq_eff
      ,ifreq_eff - (ifreq_bw_final / 2)
      ,ifreq_eff + (ifreq_bw_final / 2)
      )
    RETURNING id into ifreqbandid
    ;
  END IF;

  RETURN ifreqbandid;
END;

$$ LANGUAGE plpgsql;

{% endifdb %}