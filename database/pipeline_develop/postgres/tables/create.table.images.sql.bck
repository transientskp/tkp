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
CREATE TABLE images 
  (imageid SERIAL PRIMARY KEY
  ,ds_id INT NOT NULL
  ,tau INT NOT NULL
  ,band INT NOT NULL
  ,tau_time double precision NOT NULL
  ,freq_eff double precision NOT NULL
  ,freq_bw double precision NULL
  ,taustart_ts TIMESTAMP NOT NULL
  /*,beam_maj double precision NOT NULL
  ,beam_min double precision NOT NULL
  ,beam_pa double precision NOT NULL*/
  ,url VARCHAR(120) NULL
  ,FOREIGN KEY (ds_id) REFERENCES datasets (dsid)
  ,FOREIGN KEY (band) REFERENCES frequencybands (freqbandid)
  )
;

