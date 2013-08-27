--DROP FUNCTION insertDataset;

/**
 * This function inserts a row in the datasets table,
 * and returns the value of the id under which it is known.
 * If the dataset name (description field) already exists, a new row is added
 * and the rerun value is incremented by 1. If not, it is set
 * to its default value 0.
 *
 * Note: To be able to create a function that modifies data 
 * (by insertion) we have to set the global bin log var:
 * mysql> SET GLOBAL log_bin_trust_function_creators = 1;
 *
 */
CREATE FUNCTION insertDataset(idescription VARCHAR(100)) RETURNS INT

{% ifdb monetdb %}
BEGIN

  DECLARE idsid INT;
  DECLARE odsid INT;
  DECLARE irerun INT;

  SELECT MAX(rerun)
    INTO irerun
    FROM dataset
   WHERE description = idescription
  ;

  IF irerun IS NULL THEN
    SET irerun = 0;
  ELSE
    SET irerun = irerun + 1;
  END IF;

  SELECT NEXT VALUE FOR seq_dataset INTO idsid;

  INSERT INTO dataset
    (id
    ,rerun
    ,process_start_ts
    ,description
    )
  VALUES
    (idsid
    ,irerun
    ,NOW()
    ,idescription
    )
  ;

  SET odsid = idsid;
  RETURN odsid;

END;
{% endifdb %}


{% ifdb postgresql %}
AS $$
  DECLARE idsid INT;
  DECLARE odsid INT;
  DECLARE irerun INT;
BEGIN
  SELECT MAX(rerun)
    INTO irerun
    FROM dataset
   WHERE description = idescription
  ;

  IF irerun IS NULL THEN
    irerun := 0;
  ELSE
    irerun := irerun + 1;
  END IF;

  INSERT INTO dataset
    (rerun
    ,process_start_ts
    ,description
    )
  VALUES
    (irerun
    ,NOW()
    ,idescription
    )
  ;

  RETURN lastval();

END;

$$ LANGUAGE plpgsql;
{% endifdb %}
