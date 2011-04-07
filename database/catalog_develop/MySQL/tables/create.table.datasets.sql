/*
 * This table contains the information about the dataset that is produced by LOFAR. 
 * A dataset has an integration time and consists of multiple frequency layers.
 * taustart_timestamp:  the start time of the integration
 */
CREATE TABLE datasets (
  dsid INT NOT NULL,
  obs_id INT NOT NULL,
  dstype TINYINT NOT NULL,
  taustart_timestamp BIGINT NOT NULL, 
  dsinname CHAR(15) NOT NULL,
  dsoutname CHAR(15) DEFAULT NULL,
  desription VARCHAR(100) DEFAULT NULL,
  PRIMARY KEY (dsid),
  INDEX (obs_id),
  FOREIGN KEY (obs_id) REFERENCES observations(obsid),
  INDEX (taustart_timestamp)
) ENGINE=InnoDB;
