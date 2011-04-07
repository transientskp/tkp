/**
 * This table keeps track of the versions and changes
 */
CREATE TABLE versions (
  versionid INT NOT NULL AUTO_INCREMENT,
  version VARCHAR(32) NULL,
  creation_date DATE NOT NULL,
  scriptname VARCHAR(256) NULL,
  PRIMARY KEY (versionid)
) Engine=InnoDB;

INSERT INTO versions 
  (version
  ,creation_date
  ,scriptname
  ) VALUES 
  ('0.0.1'
  ,(SELECT NOW())
  ,'/pipe/database/catalog/tables/create.tables.sql'
  )
;

