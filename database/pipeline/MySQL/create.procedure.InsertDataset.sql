USE pipeline;

DROP PROCEDURE IF EXISTS InsertDataset;

DELIMITER //

/**
 * 
 */
CREATE PROCEDURE InsertDataset(IN idsinname VARCHAR(50)
                              ,OUT odsid INT
                              )
BEGIN

  /* For now this is set to 1 */
  DECLARE irerun INT DEFAULT NULL;
  DECLARE iobs_id INT DEFAULT 1;
  DECLARE ires_id INT DEFAULT 1;
  DECLARE idstype TINYINT DEFAULT 1;
  DECLARE itaustart_timestamp BIGINT;

  SET itaustart_timestamp = REPLACE(REPLACE(REPLACE(NOW(), '-', ''), ' ', ''), ':', '');

  SELECT IFNULL(MAX(rerun), -1)
    INTO irerun
    FROM datasets
   WHERE dsinname = idsinname
  ;

  SET irerun = irerun + 1;

  INSERT INTO datasets
    (rerun
    ,obs_id
    ,res_id
    ,dstype
    ,taustart_timestamp
    ,dsinname
    ) 
  VALUES
    (irerun
    ,iobs_id
    ,ires_id
    ,idstype
    ,itaustart_timestamp
    ,idsinname
    )
  ;

  SET odsid = LAST_INSERT_ID();

END;
//

DELIMITER ;

