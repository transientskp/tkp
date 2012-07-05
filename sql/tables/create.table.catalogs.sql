/**
 * This table stores the information about the catalogs that are
 * loaded into the pipeline database.
 */
CREATE SEQUENCE "seq_catalog" AS INTEGER;

CREATE TABLE catalog (
  catid INT DEFAULT NEXT VALUE FOR "seq_catalog",
  catname VARCHAR(50) NOT NULL,
  fullname VARCHAR(250) NOT NULL,
  PRIMARY KEY (catid)
);
