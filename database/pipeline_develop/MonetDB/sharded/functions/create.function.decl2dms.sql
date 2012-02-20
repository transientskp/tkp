--DROP FUNCTION decl2dms;

/**
 * This function converts decl from degrees into ddMMSS format.
 * The input format must be DOUBLE:
 */
CREATE FUNCTION decl2dms(ideclDEG DOUBLE) RETURNS VARCHAR(13)
BEGIN

  DECLARE declDD, declMM, declSS DOUBLE;
  DECLARE declDDstr, declMMstr VARCHAR(2);
  DECLARE declSSstr VARCHAR(6);
  DECLARE odecldms VARCHAR(13);
  
  IF ABS(ideclDEG) < 10 THEN
    SET declDD = CAST(TRUNCATE(ABS(ideclDEG), 1) AS DOUBLE);
    SET declDDstr = CONCAT('0', declDD);
  ELSE
    SET declDD = CAST(TRUNCATE(ABS(ideclDEG), 2) AS DOUBLE);
    SET declDDstr = CAST(declDD AS VARCHAR(2));
  END IF;
  
  SET declMM = CAST(TRUNCATE((ABS(ideclDEG) - declDD) * 60, 2) AS DOUBLE);
  IF declMM < 10 THEN
    SET declMMstr = CONCAT('0', declMM);
  ELSE 
    SET declMMstr = CAST(declMM AS VARCHAR(2));
  END IF;
  
  SET declSS = ROUND((((ABS(ideclDEG) - declDD) * 60) - declMM) * 60, 3);
  IF declSS < 10 THEN
    SET declSSstr = CAST(CONCAT('0', TRUNCATE(declSS, 5)) AS VARCHAR(6));
  ELSE
    SET declSSstr = CAST(TRUNCATE(declSS, 6) AS VARCHAR(6));
  END IF;

  IF ideclDEG < 0 THEN
    SET odecldms = CONCAT('-', CONCAT(declDDstr, CONCAT(':', CONCAT(declMMstr, CONCAT(':', declSSstr))))); 
  ELSE
    SET odecldms = CONCAT('+', CONCAT(declDDstr, CONCAT(':', CONCAT(declMMstr, CONCAT(':', declSSstr))))); 
  END IF;

  RETURN odecldms;

END;

