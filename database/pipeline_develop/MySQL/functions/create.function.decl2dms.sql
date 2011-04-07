DROP FUNCTION IF EXISTS decl2dms;

DELIMITER //

/**
 * This function converts decl from degrees into ddMMSS format.
 * The input format must be DOUBLE:
 */
CREATE FUNCTION decl2dms(ideclDEG DOUBLE) RETURNS VARCHAR(11)
DETERMINISTIC
BEGIN

  DECLARE declDD, declMM, declSS DOUBLE DEFAULT NULL;
  SET declDD = TRUNCATE(ideclDEG, 0);
  SET declMM = TRUNCATE((ideclDEG - declDD) * 60, 0);
  SET declSS = ROUND((((ideclDEG - declDD) * 60) - declMM) * 60, 2);

  RETURN CONCAT_WS(':', declDD, declMM, declSS); 

END;
//

DELIMITER ;
