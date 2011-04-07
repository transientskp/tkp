/**
 * cattype:     'L': source exists in measurements
 *              'C': source exists in cataloguesources
 *              'B': source exists in both
 */
CREATE TABLE sources (
  srcid INT NOT NULL AUTO_INCREMENT,
  src_name VARCHAR(50) NULL,
  cattype CHAR(1) NULL,
  class_id INT NULL,
  zone INT NOT NULL,
  ra DOUBLE NOT NULL,
  decl DOUBLE NOT NULL,
  ra_err DOUBLE NOT NULL,
  decl_err DOUBLE NOT NULL,
  x DOUBLE NOT NULL,
  y DOUBLE NOT NULL,
  z DOUBLE NOT NULL,
  spectral_params_id INT NULL,
  PRIMARY KEY (srcid),
  INDEX (src_name),
  INDEX (cattype),
  INDEX (class_id),
  FOREIGN KEY (class_id) REFERENCES classification(classid),
  INDEX (zone),
  INDEX (cattype
        ,zone
        ,ra
        ,srcid
        ),
  INDEX (cattype
        ,class_id
        ,zone
        ,ra
        ,srcid),
  FOREIGN KEY (spectral_params_id) REFERENCES spectralparameters(spectral_paramsid)
) ENGINE=InnoDB;
