/**
 * This table stores the information about the catalogs that are
 * loaded into the pipeline database.
 */
CREATE TABLE catalogs (
  catid INT NOT NULL AUTO_INCREMENT,
  catname VARCHAR(50) NOT NULL,
  fullname VARCHAR(250) NOT NULL,
  PRIMARY KEY (catid)
) ENGINE=InnoDB;
