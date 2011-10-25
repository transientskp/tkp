--DROP FUNCTION IF EXISTS ra2deg;

/**
 * This function converts ra in HHMMSS format into degrees.
 * The input format must be delimited by one char:
 * 03 45 23.2 is ok as well as
 * 03:45:23.22 is ok as well as
 */
CREATE or replace FUNCTION ra2degrees(iraHMS VARCHAR(12)) RETURNS double precision as $$
  DECLARE ss double precision;
  declare mm double precision;
declare hh double precision;
BEGIN

  RETURN 15 * (CAST(SUBSTRING(iraHMS, 1, 2) AS double precision) 
              + ((CAST(SUBSTRING(iraHMS, 4, 2) AS double precision) 
                 + (CAST(SUBSTRING(iraHMS, 7, 6) AS double precision) / 60)
                 ) / 60)
              ); 
  
END;
$$ language plpgsql;
