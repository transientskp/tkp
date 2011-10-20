CREATE TABLE multiplecatalogsources (
  multcatsrcid SERIAL,
  zone INT NOT NULL,
  ra double precision NOT NULL,
  decl double precision NOT NULL,
  ra_err double precision NOT NULL,
  decl_err double precision NOT NULL,
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
