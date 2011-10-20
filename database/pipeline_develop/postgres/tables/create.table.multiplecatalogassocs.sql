CREATE TABLE multiplecatalogassocs (
  multcatassocid SERIAL PRIMARY KEY,
  src1_id INT NOT NULL,
  src2_id INT NOT NULL,
  weight double precision NULL,
  distance double precision NULL,
  active BOOLEAN NOT NULL DEFAULT 1,
  /* Can't set foreign keys:
   * QUERY = CREATE TABLE multiplecatalogassocs (
   ERROR = !CONSTRAINT FOREIGN KEY: could not find referenced PRIMARY KEY in table 'multiplecatalogsources'
  FOREIGN KEY (src1_id) REFERENCES multiplecatalogsources (multcatsrcid),
  FOREIGN KEY (src2_id) REFERENCES multiplecatalogsources (multcatsrcid)*/
);
