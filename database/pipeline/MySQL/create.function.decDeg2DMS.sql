USE pipeline;

DROP FUNCTION IF EXISTS decDeg2DMS;

DELIMITER //

CREATE FUNCTION decDeg2DMS(idec DOUBLE) RETURNS VARCHAR(12)
DETERMINISTIC
BEGIN
  DECLARE odec VARCHAR(12) DEFAULT NULL;
  DECLARE deg INT DEFAULT NULL;
  DECLARE min INT DEFAULT NULL;
  DECLARE sec DOUBLE DEFAULT NULL;

  DECLARE odeg CHAR(2) DEFAULT NULL;
  DECLARE omin CHAR(2) DEFAULT NULL;
  DECLARE osec CHAR(5) DEFAULT NULL;

  SET deg = FLOOR(idec);
  SET min = FLOOR((idec - deg) * 60);
  SET sec = ROUND(((((idec - deg) * 60) - min) * 60), 2);
  
  IF deg < 10 THEN
    SET odeg = CONCAT('0', deg);
  ELSE
    SET odeg = CONCAT(deg);
  END IF;
  IF min < 10 THEN
    SET omin = CONCAT('0', min);
  ELSE
    SET omin = CONCAT(min);
  END IF;
  IF sec < 10 THEN
    SET osec = CONCAT('0', sec);
  ELSE
    SET osec = CONCAT(sec);
  END IF;

  SET odec = CONCAT(odeg, ':', omin, ':', osec);

  RETURN odec;

END;
//

DELIMITER ;

