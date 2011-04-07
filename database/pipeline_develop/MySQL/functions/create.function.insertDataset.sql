DROP FUNCTION IF EXISTS insertDataset;

DELIMITER //

/**
 * This function inserts a row in the datasets table,
 * and returns the value of the id under which it is known.
 * If the dataset name (dsinname) already exists, a new row is added
 * and the rerun value is incremented by 1. If not, it is set
 * to its default value 0.
 *
 * Note: To be able to create a function that modifies data 
 * (by insertion) we have to set the global bin log var:
 * mysql> SET GLOBAL log_bin_trust_function_creators = 1;
 *
 */
CREATE FUNCTION insertDataset(idsinname VARCHAR(50)) RETURNS INT
MODIFIES SQL DATA
BEGIN

  DECLARE irerun INT DEFAULT NULL;
  DECLARE idstype SMALLINT DEFAULT 1;

  SELECT IFNULL(MAX(rerun), -1)
    INTO irerun
    FROM datasets
   WHERE dsinname = idsinname
  ;

  SET irerun = irerun + 1;

  INSERT INTO datasets
    (rerun
    ,dstype
    ,process_ts
    ,dsinname
    ) 
  VALUES
    (irerun
    ,idstype
    ,NOW()
    ,idsinname
    )
  ;

  RETURN LAST_INSERT_ID();

END;
//

DELIMITER ;
