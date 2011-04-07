/**
 * distance in arcsec
 */
CREATE TABLE multiplecatalogassocs (
  multcatassocid INT NOT NULL AUTO_INCREMENT,
  src1_id INT NOT NULL,
  src2_id INT NOT NULL,
  weight DOUBLE NULL,
  distance DOUBLE NULL,
  active BOOLEAN NOT NULL DEFAULT 1,
  PRIMARY KEY (multcatassocid),
  INDEX (src1_id),
  FOREIGN KEY (src1_id) REFERENCES multiplecatalogsources (multcatsrcid),
  INDEX (src2_id),
  FOREIGN KEY (src2_id) REFERENCES multiplecatalogsources (multcatsrcid),
  INDEX (weight),
  INDEX (active)
) ENGINE=InnoDB;
