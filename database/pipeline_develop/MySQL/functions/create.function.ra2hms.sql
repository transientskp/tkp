DROP FUNCTION IF EXISTS ra2hms;

DELIMITER //

/**
 * This function converts ra from degrees into HHMMSS format.
 * The input format must be DOUBLE:
 */
CREATE FUNCTION ra2hms(iraDEG DOUBLE) RETURNS VARCHAR(11)
DETERMINISTIC
BEGIN

  DECLARE raHH, raMM, raSS DOUBLE DEFAULT NULL;
  SET raHH = TRUNCATE(iraDEG / 15, 0);
  SET raMM = TRUNCATE((iraDEG / 15 - raHH) * 60, 0);
  SET raSS = ROUND((((iraDEG / 15 - raHH) * 60) - raMM) * 60, 2);

  RETURN CONCAT_WS(':', raHH, raMM, raSS); 

END;
//

DELIMITER ;
