/**
 * This table stores the information about the catalogs that are
 * loaded into the pipeline database.
 */
CREATE TABLE catalogs (
  catid serial primary key,
  catname VARCHAR(50) NOT NULL,
  fullname VARCHAR(250) NOT NULL
);
