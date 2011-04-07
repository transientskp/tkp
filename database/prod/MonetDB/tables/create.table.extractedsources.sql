/**
 * This table contains all the extracted sources during an observation.
 * To check whether a source is new, transient or variable comparisons 
 * with the catalogsources table must be made.
 *
 * This table is empty BEFORE an observation
 * DURING an observation new sources are inserted into this table
 * AFTER an observation this table is dumped and transported to the 
 * catalog database
 *
 * tau:             The integration time (one out of the logarithmic series)
 * band:            The frequency band (freq_eff)
 * seq_nr:          Stream of images with same tau are ordered by 
 *                  sequence number
 * ds_id:           Determines the dataset from which this source comes
 * zone:            The declination zone (decl)
 * assoc_xtrsrcid:  To which src (in this table) this xtrsrcid is associated
 * assoc_catsrcid:  To which src (in the catalogsource table) this xtrsrcid 
 *                  is associated
 * x, y, z:         Cartesian coordinates
 * det_sigma:       The sigma level of the detection,
 *                  20*(I_peak/det_sigma) gives the rms of the detection.
 * Fluxes are in Jy, ra, decl, ra_err and decl_err in degrees.
 * 
 */
CREATE SEQUENCE "seq_extractedsources" AS INTEGER;

CREATE TABLE extractedsources (
  xtrsrcid INT DEFAULT NEXT VALUE FOR "seq_extractedsources",
  image_id INT NOT NULL, 
  zone INT NOT NULL,
  ra DOUBLE NOT NULL,
  decl DOUBLE NOT NULL,
  ra_err DOUBLE NOT NULL,
  decl_err DOUBLE NOT NULL,
  x DOUBLE NOT NULL,
  y DOUBLE NOT NULL,
  z DOUBLE NOT NULL,
  margin BOOLEAN NOT NULL DEFAULT 0,
  det_sigma DOUBLE NOT NULL,
  I_peak DOUBLE NULL,
  I_peak_err DOUBLE NULL,
  Q_peak DOUBLE NULL,
  Q_peak_err DOUBLE NULL,
  U_peak DOUBLE NULL,
  U_peak_err DOUBLE NULL,
  V_peak DOUBLE NULL,
  V_peak_err DOUBLE NULL,
  I_int DOUBLE NULL,
  I_int_err DOUBLE NULL,
  Q_int DOUBLE NULL,
  Q_int_err DOUBLE NULL,
  U_int DOUBLE NULL,
  U_int_err DOUBLE NULL,
  V_int DOUBLE NULL,
  V_int_err DOUBLE NULL,
  PRIMARY KEY (xtrsrcid),
  FOREIGN KEY (image_id) REFERENCES images (imageid)
);
