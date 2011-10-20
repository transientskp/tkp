--DROP FUNCTION decl2deg;

/**
 * This function converts decl in DD:MM:SS.ss format into degrees.
 * The input format must be delimited by one char:
 * 03 45 23.2 is ok as well as
 * -03:45:23.22 is ok as well as
 */
CREATE FUNCTION decl2deg(ideclDMS VARCHAR(12)) RETURNS double precision as $$
BEGIN

  DECLARE decldeg double precision;

  /* 
  DECLARE idelim CHAR(1);
  DECLARE declDD,declMM INT;
  DECLARE declSS double precision;
  SET idelim = ':';
  SET ideclDMS = REPLACE(ideclDMS, '.', idelim);
  SET declDD = CAST(SUBSTRING(ideclDMS, 2, 2) AS double precision);
  SET declMM = CAST(SUBSTRING(ideclDMS, 5, 2) AS double precision);
  SET declSS = CAST(SUBSTRING(ideclDMS, 8, 6) AS double precision);
  */
  
  IF SUBSTRING(ideclDMS, 1, 1) = '-' THEN
    SET decldeg = CAST(SUBSTRING(ideclDMS, 2, 2) AS double precision)
                  + (CAST(SUBSTRING(ideclDMS, 5, 2) AS double precision) 
                    + CAST(SUBSTRING(ideclDMS, 8, 4) AS double precision) / 60
                    ) / 60;
    SET decldeg =  -1 * decldeg;
  ELSE
    SET decldeg = CAST(SUBSTRING(ideclDMS, 1, 2) AS double precision)
                  + (CAST(SUBSTRING(ideclDMS, 4, 2) AS double precision) 
                    + CAST(SUBSTRING(ideclDMS, 7, 4) AS double precision) / 60
                    ) / 60;
  END IF;
  
  RETURN decldeg;

END;
$$ language plpgsql;
