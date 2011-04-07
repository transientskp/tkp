/**
 * This table stores information about the size of a source.
 * size_type determines whether the source is represented by a:
 * G    Gaussian, defined by
 *      pa, a, b
 * B    Bessel
 * ?
 */
CREATE TABLE sourcesizes (
  srcsizeid INT NOT NULL AUTO_INCREMENT,
  xtrsrc_id INT NULL,
  size_type CHAR(1),
  pa DOUBLE NULL,
  a DOUBLE NULL,
  b DOUBLE NULL,
  more_params_here DOUBLE NULL,
  PRIMARY KEY (srcsizeid),
  INDEX (xtrsrc_id),
  FOREIGN KEY (xtrsrc_id) REFERENCES extractedsources (xtrsrcid),
  INDEX (size_type)
) ENGINE = InnoDB
;
