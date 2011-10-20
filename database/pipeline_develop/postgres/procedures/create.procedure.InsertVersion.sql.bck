--DROP PROCEDURE InsertVersion;

/**
 */
CREATE PROCEDURE InsertVersion()
BEGIN

  INSERT INTO versions
    (version
    ,creation_date
    ,monet_version
    ,scriptname
    ) 
  VALUES
    ('0.0.1'
    ,(SELECT now())
    ,(SELECT value FROM sys.env() WHERE name = 'monet_version')
    ,'/pipe/database/pipeline_develop/MonetDB/'
    )
  ;

END;
