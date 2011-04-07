CREATE TABLE effectivefrequency (
  freqeffid INT NOT NULL,
  band INT NULL,
  freq_eff1 DOUBLE NULL,
  freq_eff_n DOUBLE NULL,
  freq_eff20 DOUBLE NULL,
  PRIMARY KEY (freqeffid),
  INDEX (band),
  FOREIGN KEY (band) REFERENCES frequencybands(freqbandid)  
) ENGINE=InnoDB;
