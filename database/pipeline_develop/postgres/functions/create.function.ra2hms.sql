--DROP FUNCTION ra2bbshms;

/**
 * This function converts ra from degrees into HHMMSS format.
 * The input format must be double precision:
 * The output is hms 00:00:00.00
 */
CREATE or replace FUNCTION ra2bbshms(iraDEG double precision) RETURNS VARCHAR(11) as $$

  DECLARE raHHnum double precision;
  declare raMMnum double precision;
  declare raSSnum double precision;
  DECLARE raHHstr varchar(2);
  declare raMMstr VARCHAR(2); 
  DECLARE raSSstr VARCHAR(6);

BEGIN
  
  IF iraDEG < 15 THEN
    raHHnum := 0;
    raMMnum := substring(cast(iraDEG*4 as varchar(80)) from 1 for 2);
    raSSnum := ROUND(cast(((iraDEG * 4) - raMMnum) * 60 as numeric), 2);
  ELSE
    raHHnum := substring(cast(iraDEG/15 as varchar(80)) from 1 for 2);
    raMMnum := substring(cast((iraDEG/15 - raHHnum)*60 as varchar(80)) from 1 for 2);
    raSSnum := ROUND(cast((((iraDEG / 15 - raHHnum) * 60) - raMMnum) * 60 as numeric), 2);
  END IF;

  IF raHHnum < 10 THEN
    raHHstr := '0' || raHHnum;
  ELSE 
    raHHstr := CAST(raHHnum AS VARCHAR(2));  
  END IF;

  IF raMMnum < 10 THEN
    raMMstr := CONCAT('0', raMMnum);
  ELSE 
    raMMstr := CAST(raMMnum AS VARCHAR(2));  
  END IF;

  IF raSSnum < 10 THEN
    raSSstr := CAST('0' || substring(cast(raSSnum as varchar(80)) from 1 for 4) AS VARCHAR(5));
  ELSE 
    raSSstr := CAST(substring(cast(raSSnum as varchar(80)) from 1 for 5) AS VARCHAR(5));
  END IF;

  return raHHstr || ':' || raMMstr || ':' || raSSstr;
  
END;
$$ language plpgsql;
