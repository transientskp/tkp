--DROP PROCEDURE InsertVersion;

/**
 */
CREATE or replace function InsertVersion() returns void as $$
BEGIN

  INSERT INTO versions
    (version
    ,creation_date
    ,postgres_version
    ,scriptname
    ) 
  VALUES
    ('0.0.1'
    ,(SELECT now())
    ,(SELECT version())
    ,'/database/trunk/database/pipeline_develop/postgres/'
    )
  ;

END;
$$ LANGUAGE plpgsql;
