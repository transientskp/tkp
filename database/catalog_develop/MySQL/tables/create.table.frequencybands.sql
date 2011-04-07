CREATE TABLE frequencybands (
  freqbandid INT NOT NULL,
  freqband1_low DOUBLE NULL,
  freqband1_high DOUBLE NULL,
  freqband_n_low DOUBLE NULL,
  freqband_n_high DOUBLE NULL,
  freqband20_low DOUBLE NULL,
  freqband20_high DOUBLE NULL,
  PRIMARY KEY (freqbandid)
) ENGINE=InnoDB;
