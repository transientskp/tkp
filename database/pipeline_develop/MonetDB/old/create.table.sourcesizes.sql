/**
 * This table stores information about the size of a source.
 * size_type determines whether the source is represented by a:
 * G    Gaussian, defined by
 *      pa, a, b
 * B    Bessel
 * ?
 */
CREATE SEQUENCE "seq_sourcesizes" AS INTEGER;

CREATE TABLE sourcesizes (
  srcsizeid INT DEFAULT NEXT VALUE FOR "seq_sourcesizes",
  xtrsrc_id INT NULL,
  src_id INT NULL,
  size_type CHAR(1),
  pa DOUBLE NULL,
  a DOUBLE NULL,
  b DOUBLE NULL,
  more_params_here DOUBLE NULL,
  PRIMARY KEY (srcsizeid),
  FOREIGN KEY (xtrsrc_id) REFERENCES extractedsources (xtrsrcid),
  FOREIGN KEY (src_id) REFERENCES sourcelist (srcid)
);
