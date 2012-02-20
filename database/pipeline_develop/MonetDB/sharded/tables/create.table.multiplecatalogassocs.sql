CREATE SEQUENCE "seq_multiplecatalogassocs" AS INTEGER;

CREATE TABLE multiplecatalogassocs (
  multcatassocid INT NOT NULL AUTO_INCREMENT,
  src1_id INT NOT NULL,
  src2_id INT NOT NULL,
  weight DOUBLE NULL,
  distance DOUBLE NULL,
  active BOOLEAN NOT NULL DEFAULT 1,
  PRIMARY KEY (multcatassocid)
  /* Can't set foreign keys:
   * QUERY = CREATE TABLE multiplecatalogassocs (
   ERROR = !CONSTRAINT FOREIGN KEY: could not find referenced PRIMARY KEY in table 'multiplecatalogsources'
  FOREIGN KEY (src1_id) REFERENCES multiplecatalogsources (multcatsrcid),
  FOREIGN KEY (src2_id) REFERENCES multiplecatalogsources (multcatsrcid)*/
);
