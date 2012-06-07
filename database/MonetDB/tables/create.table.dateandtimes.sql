/**
 * This table contains the information about the dataset that is produced by LOFAR. 
 * A dataset has an integration time and consists of multiple frequency layers.
 * taustart_timestamp:  the start time of the integration
 */
CREATE SEQUENCE "seq_dateandtimes" AS INTEGER;

CREATE TABLE dateandtimes (
  dtid INT DEFAULT NEXT VALUE FOR "seq_dateandtimes",
  txt VARCHAR(30) NULL,
  start_d DATE NULL, 
  start_ts TIMESTAMP NULL, 
  start_tstz TIMESTAMPTZ NULL, 
  start_t TIME NULL,
  PRIMARY KEY (dtid)
);
