--DROP FUNCTION decl2bbsdms;

/**
 * This function converts decl from degrees into ddMMSS format.
 * The input format must be double precision:
 * The output in dms
 * +54.00.09.03
 */
CREATE FUNCTION decl2bbsdms(ideclDEG double precision) RETURNS varchar(12) as $$
declare
  declDD double precision;
  declMM double precision;
  declSS double precision;
  declDDstr varchar(2);
  declMMstr VARCHAR(2);
  declSSstr VARCHAR(5);
  odecldms VARCHAR(12);
BEGIN

  IF ABS(ideclDEG) < 10 THEN
    /* This check is necessary because doubles less than 1e-3 
     * will be converted to exp notation
     * for which truncation doesn't work.
     */
    IF ABS(ideclDEG) < 1 THEN
      declDD := 0;
      SET declDDstr = '00';
    ELSE 
      SET declDD = CAST(TRUNCATE(ABS(ideclDEG), 1) AS double precision);
      SET declDDstr = CONCAT('0', declDD);
    END IF;
  ELSE
    SET declDD = CAST(TRUNCATE(ABS(ideclDEG), 2) AS double precision);
    SET declDDstr = CAST(declDD AS VARCHAR(2));
  END IF;
  
  IF ABS(ideclDEG) < 1 THEN
    SET declMM = CAST(TRUNCATE((ABS(ideclDEG) * 60), 2) AS double precision);
  ELSE
    SET declMM = CAST(TRUNCATE((ABS(ideclDEG) - declDD) * 60, 2) AS double precision);
  END IF;
  IF declMM < 10 THEN
    SET declMMstr = CONCAT('0', declMM);
  ELSE 
    SET declMMstr = CAST(declMM AS VARCHAR(2));
  END IF;
  
  IF ABS(ideclDEG) < 1 THEN
    SET declSS = ROUND(((ABS(ideclDEG) * 60) - declMM) * 60, 2);
  ELSE
    SET declSS = ROUND((((ABS(ideclDEG) - declDD) * 60) - declMM) * 60, 2);
  END IF;
  IF declSS < 10 THEN
    SET declSSstr = CAST(CONCAT('0', TRUNCATE(declSS, 4)) AS VARCHAR(5));
  ELSE
    SET declSSstr = CAST(TRUNCATE(declSS, 5) AS VARCHAR(5));
  END IF;

  IF ideclDEG < 0 THEN
    SET odecldms = CONCAT('-', CONCAT(declDDstr, CONCAT('.', CONCAT(declMMstr, CONCAT('.', declSSstr))))); 
  ELSE
    SET odecldms = CONCAT('+', CONCAT(declDDstr, CONCAT('.', CONCAT(declMMstr, CONCAT('.', declSSstr))))); 
  END IF;
  
  RETURN odecldms;

END;
$$ language plpgsql;
