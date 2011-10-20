/**
 * This table keeps track of the versions and changes
 */
CREATE TABLE versions 
  (versionid SERIAL PRIMARY KEY
  ,version VARCHAR(32) NULL
  ,creation_date DATE NOT NULL
  ,postgres_version VARCHAR(120) NOT NULL
  ,scriptname VARCHAR(256) NULL
);

