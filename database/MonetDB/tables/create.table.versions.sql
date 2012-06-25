/**
 * This table keeps track of the versions and changes
 */
CREATE SEQUENCE "seq_versions" AS INTEGER;

CREATE TABLE versions 
  (versionid INT DEFAULT NEXT VALUE FOR "seq_versions"
  ,version VARCHAR(32) NULL
  ,creation_ts TIMESTAMP NOT NULL
  ,monet_version VARCHAR(8) NOT NULL
  ,monet_release VARCHAR(32) NOT NULL
  ,node TINYINT NOT NULL DEFAULT %NODE%
  ,nodes TINYINT NOT NULL DEFAULT %NODES%
  ,scriptname VARCHAR(256) NULL
  ,PRIMARY KEY (versionid)
  );

