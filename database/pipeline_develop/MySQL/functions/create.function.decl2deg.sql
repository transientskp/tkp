DROP FUNCTION IF EXISTS decl2deg;

DELIMITER //

/**
 * This function converts decl in DDMMSS format into degrees.
 * The input format must be delimited by one char:
 * 03 45 23.2 is ok as well as
 * 03:45:23.22 is ok as well as
 */
CREATE FUNCTION decl2deg(ideclDMS VARCHAR(11)) RETURNS DOUBLE
DETERMINISTIC
BEGIN

  DECLARE idelim CHAR(1) DEFAULT ':';
  DECLARE ideclDD INT DEFAULT NULL;
  DECLARE ideclMM INT DEFAULT NULL;
  DECLARE ideclSS DOUBLE DEFAULT NULL;
  DECLARE ideclMS DOUBLE DEFAULT NULL;

  SET ideclDMS = REPLACE(ideclDMS, ' ', idelim);

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
//

DELIMITER ;
