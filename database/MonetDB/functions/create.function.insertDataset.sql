--DROP FUNCTION insertDataset;

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
BEGIN

  DECLARE idsid INT;
  DECLARE odsid INT;
  DECLARE irerun INT;
  DECLARE idstype SMALLINT;
  SELECT 1
    INTO idstype
  ;

  SELECT MAX(rerun)
    INTO irerun
    FROM datasets
   WHERE dsinname = idsinname
  ;

  IF irerun IS NULL THEN
    SET irerun = 0;
  ELSE
    SET irerun = irerun + 1;
  END IF;

  SELECT NEXT VALUE FOR seq_datasets INTO idsid;

  INSERT INTO datasets
    (dsid
    ,rerun
    ,dstype
    ,process_ts
    ,dsinname
    ) 
  VALUES
    (idsid
    ,irerun
    ,idstype
    ,NOW()
    ,idsinname
    )
  ;

  SET odsid = idsid;
  RETURN odsid;

END;
