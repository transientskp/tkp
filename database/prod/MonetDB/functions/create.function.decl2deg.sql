--DROP FUNCTION decl2deg;

/**
 * This function converts decl in DDMMSS format into degrees.
 * The input format must be delimited by one char:
 * 03 45 23.2 is ok as well as
 * 03:45:23.22 is ok as well as
 */
CREATE FUNCTION decl2deg(ideclDMS VARCHAR(11)) RETURNS DOUBLE
BEGIN

  DECLARE idelim CHAR(1);
  DECLARE ideclDD,ideclMM INT;
  DECLARE ideclSS,ideclMS DOUBLE;
  SET idelim = ':';

  SET ideclDMS = REPLACE(ideclDMS, ' ', idelim);

  /* This is non-standard MonetDB-SQL */
  SET ideclDD = CAST(SUBSTRING_INDEX(ideclDMS, idelim, 1) AS SIGNED);
  SET ideclMS = (CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(ideclDMS, idelim, 2), idelim, -1) AS SIGNED) 
                + 
                (CAST(SUBSTRING_INDEX(ideclDMS, idelim, -1) AS DECIMAL(4, 2)) / 60)
                ) / 60;

  IF ideclDMS LIKE '-%' THEN
    RETURN ideclDD - ideclMS;
  ELSE
    RETURN ideclDD + ideclMS;
  END IF;

END;
