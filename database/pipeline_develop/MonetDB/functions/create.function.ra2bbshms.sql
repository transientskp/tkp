--DROP FUNCTION ra2bbshms;

/**
 * This function converts ra from degrees into HHMMSS format.
 * The input format must be DOUBLE:
 * The output is hms 00:00:00.00
 */
CREATE FUNCTION ra2bbshms(iraDEG DOUBLE) RETURNS VARCHAR(11)

BEGIN

  DECLARE raHHnum, raMMnum, raSSnum DOUBLE;
  DECLARE raHHstr, raMMstr VARCHAR(2); 
  DECLARE raSSstr VARCHAR(6);
  
  IF iraDEG < 15 THEN
    SET raHHnum = 0;
    SET raMMnum = TRUNCATE(iraDEG  * 4, 2);
    SET raSSnum = ROUND(((iraDEG * 4) - raMMnum) * 60, 2);
  ELSE
    SET raHHnum = TRUNCATE(iraDEG / 15, 2);
    SET raMMnum = TRUNCATE((iraDEG / 15 - raHHnum) * 60, 2);
    SET raSSnum = ROUND((((iraDEG / 15 - raHHnum) * 60) - raMMnum) * 60, 2);
  END IF;

  IF raHHnum < 10 THEN
    SET raHHstr = CONCAT('0', raHHnum);
  ELSE 
    SET raHHstr = CAST(raHHnum AS VARCHAR(2));  
  END IF;

  IF raMMnum < 10 THEN
    SET raMMstr = CONCAT('0', raMMnum);
  ELSE 
    SET raMMstr = CAST(raMMnum AS VARCHAR(2));  
  END IF;

  IF raSSnum < 10 THEN
    SET raSSstr = CAST(CONCAT('0', TRUNCATE(raSSnum, 4)) AS VARCHAR(5));
  ELSE 
    SET raSSstr = CAST(TRUNCATE(raSSnum,5) AS VARCHAR(5));  
  END IF;

  RETURN CONCAT(raHHstr, CONCAT(':', CONCAT(raMMstr, CONCAT(':', raSSstr))));
  
END;

