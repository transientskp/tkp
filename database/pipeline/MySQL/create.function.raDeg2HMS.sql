USE pipeline;

DROP FUNCTION IF EXISTS raDeg2HMS;

DELIMITER //

CREATE FUNCTION raDeg2HMS(ira DOUBLE) RETURNS VARCHAR(12)
DETERMINISTIC
BEGIN
  DECLARE ora VARCHAR(12) DEFAULT NULL;
  DECLARE hh INT DEFAULT NULL;
  DECLARE mm INT DEFAULT NULL;
  DECLARE ss DOUBLE DEFAULT NULL;

  DECLARE ohh CHAR(2) DEFAULT NULL;
  DECLARE omm CHAR(2) DEFAULT NULL;
  DECLARE oss CHAR(5) DEFAULT NULL;

  SET hh = FLOOR(ira / 15);
  SET mm = FLOOR((ira / 15 - hh) * 60);
  SET ss = ROUND(((((ira / 15 - hh) * 60) - mm) * 60), 2);
  
  IF hh < 10 THEN
    SET ohh = CONCAT('0', hh);
  ELSE
    SET ohh = CONCAT(hh);
  END IF;
  IF mm < 10 THEN
    SET omm = CONCAT('0', mm);
  ELSE
    SET omm = CONCAT(mm);
  END IF;
  IF ss < 10 THEN
    SET oss = CONCAT('0', ss);
  ELSE
    SET oss = CONCAT(ss);
  END IF;

  SET ora = CONCAT(ohh, ':', omm, ':', oss);

  RETURN ora;

END;
//

DELIMITER ;

