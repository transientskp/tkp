/**
 * This table contains the information about the dataset that is produced by LOFAR. 
 * A dataset has an integration time and consists of multiple frequency layers.
 * taustart_timestamp:  the start time of the integration
 */

CREATE TABLE dataset
  (id INT AUTO_INCREMENT
  ,rerun INT NOT NULL DEFAULT '0'
  ,"type" TINYINT NOT NULL
  ,process_ts TIMESTAMP NOT NULL
  ,inname VARCHAR(64) NOT NULL
  ,outname VARCHAR(64) DEFAULT NULL
  ,description VARCHAR(100) DEFAULT NULL
  ,node TINYINT NOT NULL DEFAULT %NODE%
  ,nodes TINYINT NOT NULL DEFAULT %NODES%
  ,PRIMARY KEY (id)
  )
;

