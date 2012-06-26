/**
 * This table contains the information about the dataset that is produced by LOFAR. 
 * A dataset has an integration time and consists of multiple frequency layers.
 * taustart_timestamp:  the start time of the integration
 */
CREATE SEQUENCE "seq_dataset" AS INTEGER;

CREATE TABLE dataset
  (dsid INT DEFAULT NEXT VALUE FOR "seq_dataset"
  ,rerun INT NOT NULL DEFAULT '0'
  ,dstype TINYINT NOT NULL
  ,process_ts TIMESTAMP NOT NULL
  ,dsinname VARCHAR(64) NOT NULL
  ,dsoutname VARCHAR(64) DEFAULT NULL
  ,description VARCHAR(100) DEFAULT NULL
  ,node TINYINT NOT NULL DEFAULT %NODE%
  ,nodes TINYINT NOT NULL DEFAULT %NODES%
  ,PRIMARY KEY (dsid)
  )
;

