CREATE SEQUENCE "seq_multiplecatalogsources" AS INTEGER;

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
  FOREIGN KEY (cat_id) REFERENCES catalogs (catid)
  /* Can't set this foreign key:
   * ERROR = !CONSTRAINT FOREIGN KEY: could not find referenced PRIMARY KEY in table 'catalogedsources'
                   Creating MonetDB pipeline_develop table multiplecatalogassocs
  FOREIGN KEY (orig_catsrcid) REFERENCES catalogedsources (orig_catsrcid)*/
);
