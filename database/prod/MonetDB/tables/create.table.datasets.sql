/**
 * This table contains the information about the dataset that is produced by LOFAR. 
 * A dataset has an integration time and consists of multiple frequency layers.
 * taustart_timestamp:  the start time of the integration
 */
CREATE SEQUENCE "seq_datasets" AS INTEGER;

CREATE TABLE datasets (
  dsid INT DEFAULT NEXT VALUE FOR "seq_datasets",
  rerun INT NOT NULL DEFAULT '0',
  dstype TINYINT NOT NULL,
  process_ts TIMESTAMP NOT NULL, 
  dsinname VARCHAR(64) NOT NULL,
  dsoutname VARCHAR(64) DEFAULT NULL,
  description VARCHAR(100) DEFAULT NULL,
  PRIMARY KEY (dsid)
);
