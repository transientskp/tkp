/**
 * This table contains the images that are being processed.
 * The only format for now is FITS. The HDF5 format will be implemented
 * later.
 * An image is characterised by
 *      - integration time (tau)
 *      - frequency band (band) 
 *      - timestamp (seq_nr).
 * A group of images that belong together (not specified any further)
 * are in the same data set (they have the same ds_id).
 * tau_time in seconds (ref. tau)
 * freq_eff in Hz (ref. band)
 * taustart_timestamp in YYYY-MM-DD-HH:mm:ss:nnnnnn, but without 
 *                    interpunctions (ref. seq_nr)
 */
CREATE TABLE images (
  imageid INT NOT NULL AUTO_INCREMENT,
  ds_id INT NOT NULL,
  tau INT NOT NULL,
  seq_nr INT NOT NULL,
  band INT NOT NULL,
  tau_time DOUBLE NOT NULL,
  freq_eff DOUBLE NOT NULL,
  taustart_ts TIMESTAMP NOT NULL, 
  url VARCHAR(120) NULL,
  PRIMARY KEY (ds_id
              ,tau
              ,seq_nr
              ,band
              ),
  UNIQUE INDEX (imageid),
  INDEX (taustart_ts),
  FOREIGN KEY (ds_id) REFERENCES datasets (dsid),
  FOREIGN KEY (band) REFERENCES frequencybands (freqbandid)
) ENGINE=InnoDB;
