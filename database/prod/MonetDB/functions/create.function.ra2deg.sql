--DROP FUNCTION IF EXISTS ra2deg;

/**
 * This function converts ra in HHMMSS format into degrees.
 * The input format must be delimited by one char:
 * 03 45 23.2 is ok as well as
 * 03:45:23.22 is ok as well as
 */
CREATE FUNCTION ra2deg(iraHMS VARCHAR(11)) RETURNS DOUBLE
BEGIN

  DECLARE idelim CHAR(1);
  SELECT ':'
    INTO idelim
  ;
  
  SET iraHMS = REPLACE(iraHMS, ' ', idelim);

  RETURN 15 * (CAST(SUBSTRING_INDEX(iraHMS
                                   ,idelim
                                   ,1) AS SIGNED) 
            + ((CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(iraHMS
                                                    ,idelim
                                                    ,2)
                                    ,idelim
                                    ,-1) AS SIGNED) 
            + (CAST(SUBSTRING_INDEX(iraHMS
                                   ,idelim
                                   ,-1) AS DECIMAL(4, 2)) / 60)) / 60));

END;
