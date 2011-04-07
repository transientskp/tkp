/**
 * This table stores the information about the catalogs that are
 * loaded into the pipeline database.
 */
CREATE SEQUENCE "seq_catalogs" AS INTEGER;

CREATE TABLE catalogs (
  catid INT DEFAULT NEXT VALUE FOR "seq_catalogs",
  catname VARCHAR(50) NOT NULL,
  fullname VARCHAR(250) NOT NULL,
  PRIMARY KEY (catid)
);
