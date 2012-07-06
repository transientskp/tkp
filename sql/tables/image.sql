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
 * bsmaj, bsmin, bpa are the semimajor, semiminor axes of the synthesized beam in degrees
 *                 NOTE that these *ARE* the semimajor axes.
 * centr_ra and _decl are the central coordinates (J2000) of the image in degrees.
 */

CREATE TABLE image 
  (id INT AUTO_INCREMENT
  ,dataset INT NOT NULL
  ,tau INT NOT NULL
  ,band INT NOT NULL
  ,stokes CHAR(1) NOT NULL DEFAULT 'I'
  ,tau_time DOUBLE NOT NULL
  ,freq_eff DOUBLE NOT NULL
  ,freq_bw DOUBLE NULL
  ,taustart_ts TIMESTAMP NOT NULL
  ,bmaj_syn DOUBLE NULL
  ,bmin_syn DOUBLE NULL
  ,bpa_syn DOUBLE NULL
  ,url VARCHAR(120) NULL
  ,node TINYINT NOT NULL DEFAULT %NODE%
  ,nodes TINYINT NOT NULL DEFAULT %NODES%
  ,PRIMARY KEY (id)
  ,FOREIGN KEY (dataset) REFERENCES dataset (id)
  ,FOREIGN KEY (band) REFERENCES frequencyband (id)
  );

