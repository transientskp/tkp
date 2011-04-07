/**
 */
CREATE TABLE multiplecatalogsources (
  multcatsrcid INT NOT NULL AUTO_INCREMENT,
  zone INT NOT NULL,
  ra DOUBLE NOT NULL,
  decl DOUBLE NOT NULL,
  ra_err DOUBLE NOT NULL,
  decl_err DOUBLE NOT NULL,
  cat_id INT NULL,
  orig_catsrcid INT NULL,
  orig_src1_id INT NULL,
  orig_src2_id INT NULL,
  active BOOLEAN NOT NULL DEFAULT 1,
  PRIMARY KEY (multcatsrcid
              ,zone
              ,ra
              ),
  INDEX (cat_id),
  FOREIGN KEY (cat_id) REFERENCES catalogs (catid),
  INDEX (orig_catsrcid),
  FOREIGN KEY (orig_catsrcid) REFERENCES catalogedsources (orig_catsrcid)
) ENGINE=InnoDB;
