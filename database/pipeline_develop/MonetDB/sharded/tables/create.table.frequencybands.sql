/**
 * This table contains the frequencies at which the extracted sources 
 * were detected. It might also be preloaded with the frequencies 
 * at which the stokes of the catalog sources were measured.
 */
CREATE SEQUENCE "seq_frequencybands" AS INTEGER;

CREATE TABLE frequencybands (
  freqbandid INT NOT NULL DEFAULT NEXT VALUE FOR "seq_frequencybands",
  freq_central DOUBLE DEFAULT NULL,
  freq_low DOUBLE DEFAULT NULL,
  freq_high DOUBLE DEFAULT NULL,
  PRIMARY KEY (freqbandid)
);
