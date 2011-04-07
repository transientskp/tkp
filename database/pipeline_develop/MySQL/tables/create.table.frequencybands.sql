/**
 * This table contains the frequencies at which the extracted sources 
 * were detected. It might also be preloaded with the frequencies 
 * at which the stokes of the catalog sources were measured.
 */
CREATE TABLE frequencybands (
  freqbandid INT NOT NULL AUTO_INCREMENT,
  freq_low DOUBLE DEFAULT NULL,
  /*freq_central DOUBLE DEFAULT NULL,*/
  freq_high DOUBLE DEFAULT NULL,
  PRIMARY KEY (freqbandid)
) ENGINE=InnoDB;

