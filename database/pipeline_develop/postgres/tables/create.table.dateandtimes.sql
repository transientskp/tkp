/**
 * This table contains the information about the dataset that is produced by LOFAR. 
 * A dataset has an integration time and consists of multiple frequency layers.
 * taustart_timestamp:  the start time of the integration
 */
CREATE TABLE dateandtimes (
  dtid SERIAL PRIMARY KEY,
  txt VARCHAR(30) NULL,
  start_d DATE NULL, 
  start_ts TIMESTAMP NULL, 
  start_tstz TIMESTAMPTZ NULL, 
  start_t TIME NULL,
);
