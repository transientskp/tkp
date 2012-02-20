/**
 * This table contains the known sources that were detected previously, 
 * either by LOFAR itself or other instruments. 
 * It is a selection from the table containing all the catalog 
 * sources (in the catlogue area). 
 * Every observation has its field(s) of view and for this all the 
 * known sources are collected. This table will be loaded from the 
 * catalog table in the catalog database before every observation.
 * This table will be used to load the sources table 
 * and will not be touched any more during an observation.
 * Fluxes are in Jy, ra, decl, ra_err and decl_err in degrees.
 * PA, major, minor in degrees
 *
 * TODO: Probably it is better not te set catsrcid to auto_incr,
 * because we will copy them from the catalog database.
 */
CREATE SEQUENCE "seq_catalogedsources" AS INTEGER;

CREATE TABLE catalogedsources (
  catsrcid INT DEFAULT NEXT VALUE FOR "seq_catalogedsources",
  cat_id INT NOT NULL,
  orig_catsrcid INT NOT NULL,
  catsrcname VARCHAR(120) NULL,
  tau INT NULL,
  band INT NOT NULL,
  freq_eff DOUBLE NOT NULL,
  zone INT NOT NULL,
  ra DOUBLE NOT NULL,
  decl DOUBLE NOT NULL,
  ra_err DOUBLE NOT NULL,
  decl_err DOUBLE NOT NULL,
  x DOUBLE NOT NULL,
  y DOUBLE NOT NULL,
  z DOUBLE NOT NULL,
  margin BOOLEAN NOT NULL DEFAULT 0,
  det_sigma DOUBLE NOT NULL DEFAULT 0,
  src_type VARCHAR(1) NULL,
  fit_probl VARCHAR(2) NULL,
  ell_a DOUBLE NULL,
  ell_b DOUBLE NULL,
  PA DOUBLE NULL,
  PA_err DOUBLE NULL,
  major DOUBLE NULL,
  major_err DOUBLE NULL,
  minor DOUBLE NULL,
  minor_err DOUBLE NULL,
  I_peak_avg DOUBLE NULL,
  I_peak_avg_err DOUBLE NULL,
  I_peak_min DOUBLE NULL,
  I_peak_min_err DOUBLE NULL,
  I_peak_max DOUBLE NULL,
  I_peak_max_err DOUBLE NULL,
  I_int_avg DOUBLE NULL,
  I_int_avg_err DOUBLE NULL,
  I_int_min DOUBLE NULL,
  I_int_min_err DOUBLE NULL,
  I_int_max DOUBLE NULL,
  I_int_max_err DOUBLE NULL,
  frame VARCHAR(20) NULL,
  PRIMARY KEY (catsrcid),
  /*UNIQUE (cat_id
         ,orig_catsrcid),*/
  FOREIGN KEY (cat_id) REFERENCES catalogs (catid),
  FOREIGN KEY (band) REFERENCES frequencybands (freqbandid)
);
