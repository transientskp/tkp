--DROP FUNCTION decl2bbsdms;

/**
 * This function converts decl from degrees into dd:MM:SS format.
 * The input format must be double precision:
 * The output in dms
 * +54:00:09:03
 */
CREATE or replace FUNCTION decl2bbsdms(ideclDEG double precision) RETURNS varchar(12) as $$
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
      declDDstr := '00';
    ELSE 
      declDD := cast(substring(cast(abs(ideclDEG) as varchar(80)) from 1 for 1) as double precision);
      declDDstr := '0' || declDD;
    END IF;
  ELSE
    declDD := cast(substring(cast(abs(ideclDEG) as varchar(80)) from 1 for 2) as double precision);
    declDDstr := CAST(declDD AS VARCHAR(2));
  END IF;
  
  IF ABS(ideclDEG) < 1 THEN
    declMM := cast(substring(cast(abs(ideclDEG) * 60 as varchar(80)) from 1 for 2) as double precision);
  ELSE
    declMM := cast(substring(cast((abs(ideclDEG) - declDD) * 60 as varchar(80)) from 1 for 2) as double precision);
  END IF;
  IF declMM < 10 THEN
    declMMstr := '0' || declMM;
  ELSE 
    declMMstr := CAST(declMM AS VARCHAR(2));
  END IF;
  
  IF ABS(ideclDEG) < 1 THEN
    declSS := ROUND(cast(((ABS(ideclDEG) * 60) - declMM) * 60 as numeric), 2);
  ELSE
    declSS := ROUND(cast((((ABS(ideclDEG) - declDD) * 60) - declMM) * 60 as numeric), 2);
  END IF;
  IF declSS < 10 THEN
    declSSstr := CAST('0' || substring(cast(declSS as varchar(80)) from 1 for 4) AS VARCHAR(5));
  ELSE
    declSSstr := CAST(substring(cast(declSS as varchar(80)) from 1 for 5) AS VARCHAR(5));
  END IF;

  IF ideclDEG < 0 THEN
    odecldms := '-' || declDDstr || ':' || declMMstr || ':' || declSSstr;
  ELSE
    odecldms := '+' || declDDstr || ':' || declMMstr || ':' || declSSstr;
  END IF;
  
  RETURN odecldms;

END;
$$ language plpgsql;
