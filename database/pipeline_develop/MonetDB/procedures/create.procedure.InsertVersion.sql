--DROP PROCEDURE InsertVersion;

/**
 */
CREATE PROCEDURE InsertVersion()
BEGIN

  INSERT INTO versions
    (version
    ,creation_ts
    ,monet_version
    ,monet_release
    ,scriptname
    ) 
  VALUES
    ('0.0.1'
    ,(SELECT CAST(NOW() AS TIMESTAMP))
    ,(SELECT value FROM sys.env() WHERE name = 'monet_version')
    ,(SELECT value FROM sys.env() WHERE name = 'monet_release')
    ,'/pipe/database/pipeline_develop/MonetDB/'
    )
  ;

END;
