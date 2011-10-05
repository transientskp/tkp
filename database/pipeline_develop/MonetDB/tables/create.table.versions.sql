/**
 * This table keeps track of the versions and changes
 */
CREATE SEQUENCE "seq_versions" AS INTEGER;

CREATE TABLE versions 
  (versionid INT DEFAULT NEXT VALUE FOR "seq_versions"
  ,version VARCHAR(32) NULL
  ,creation_date DATE NOT NULL
  ,monet_version VARCHAR(8) NOT NULL
  ,scriptname VARCHAR(256) NULL
  ,PRIMARY KEY (versionid)
);

