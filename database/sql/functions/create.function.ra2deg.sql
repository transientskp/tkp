--DROP FUNCTION IF EXISTS ra2deg;

/**
 * This function converts ra in HHMMSS format into degrees.
 * The input format must be delimited by one char:
 * 03 45 23.2 is ok as well as
 * 03:45:23.22 is ok as well as
 */
CREATE FUNCTION ra2deg(iraHMS VARCHAR(12)) RETURNS DOUBLE
BEGIN

  DECLARE ss, mm, hh DOUBLE;
  DECLARE idelim CHAR(1);
  SELECT ':'
    INTO idelim
  ;
  
  SET iraHMS = REPLACE(iraHMS, ' ', idelim);

  RETURN 15 * (CAST(SUBSTRING(iraHMS, 1, 2) AS DOUBLE) 
              + ((CAST(SUBSTRING(iraHMS, 4, 2) AS DOUBLE) 
                 + (CAST(SUBSTRING(iraHMS, 7, 6) AS DOUBLE) / 60)
                 ) / 60)
              ); 
  
END;
