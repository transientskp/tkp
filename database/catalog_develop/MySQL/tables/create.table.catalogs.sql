CREATE TABLE catalogs (
  catid INT NOT NULL,
  catname VARCHAR(20) NOT NULL,
  decl_min DOUBLE NULL,
  decl_max DOUBLE NULL,
  fullname VARCHAR(250) NOT NULL,
  PRIMARY KEY (catid)
) ENGINE=InnoDB;
