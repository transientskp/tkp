SET SCHEMA pipeline;

DROP FUNCTION InsertGetDataset;
DROP FUNCTION GetDatasetId;

CREATE FUNCTION GetDatasetId() RETURNS INT
BEGIN
  RETURN SELECT NEXT VALUE FOR seq_datasets;
END;

CREATE FUNCTION InsertGetDataset(idsinname VARCHAR(50)) RETURNS INT
BEGIN

  DECLARE idsid INT;
  DECLARE odsid INT;
  /* For now this is set to 1 */
  DECLARE irerun INT;
  DECLARE iobs_id INT;
  DECLARE ires_id INT;
  DECLARE idstype TINYINT;
  SELECT NULL
        ,1
        ,1
        ,1
    INTO irerun
        ,iobs_id
        ,ires_id
        ,idstype
  ;
  DECLARE itaustart_timestamp BIGINT;

  SET itaustart_timestamp = REPLACE(REPLACE(REPLACE(NOW(), '-', ''), ' ', ''), ':', '');

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

  SELECT GetDatasetId() INTO idsid;

  INSERT INTO datasets
    (dsid
    ,rerun
    ,obs_id
    ,res_id
    ,dstype
    ,taustart_timestamp
    ,dsinname
    ) VALUES
    (idsid
    ,irerun
    ,iobs_id
    ,ires_id
    ,idstype
    ,itaustart_timestamp
    ,idsinname
    )
  ;
  
  RETURN idsid;

END;

