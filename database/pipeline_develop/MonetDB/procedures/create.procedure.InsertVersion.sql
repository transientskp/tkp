--DROP PROCEDURE InsertVersion;

/**
 */
CREATE PROCEDURE InsertVersion()
BEGIN

  INSERT INTO versions
    (version
    ,creation_date
    ,scriptname
    ) 
  VALUES
    ('0.0.1'
    ,(SELECT now())
    ,'/pipe/database/pipeline_develop/MonetDB/'
    )
  ;

END;
