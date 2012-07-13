/**
 * TODO: Probably it is better not te set catsrcid to auto_incr,
 * because we will copy them from the catalog database.
 */

CREATE TABLE catalogedsource 
  (id INT AUTO_INCREMENT
  ,catalog TINYINT NOT NULL
  ,orig_catsrcid INT NOT NULL
  ,catsrcname VARCHAR(120) NULL
  ,tau INT NULL
  ,band SMALLINT NOT NULL
  ,stokes TINYINT NOT NULL DEFAULT 1 
  ,freq_eff DOUBLE NOT NULL
  ,zone INT NOT NULL
  ,ra DOUBLE NOT NULL
  ,decl DOUBLE NOT NULL
  ,ra_err DOUBLE NOT NULL
  ,decl_err DOUBLE NOT NULL
  ,x DOUBLE NOT NULL
  ,y DOUBLE NOT NULL
  ,z DOUBLE NOT NULL
  ,margin BOOLEAN NOT NULL DEFAULT 0
  ,det_sigma DOUBLE NOT NULL DEFAULT 0
  ,src_type VARCHAR(1) NULL
  ,fit_probl VARCHAR(2) NULL
  ,PA DOUBLE NULL
  ,PA_err DOUBLE NULL
  ,major DOUBLE NULL
  ,major_err DOUBLE NULL
  ,minor DOUBLE NULL
  ,minor_err DOUBLE NULL
  ,avg_f_peak DOUBLE NULL
  ,avg_f_peak_err DOUBLE NULL
  ,avg_f_int DOUBLE NULL
  ,avg_f_int_err DOUBLE NULL
  ,frame VARCHAR(20) NULL
  ,PRIMARY KEY (id)
  ,FOREIGN KEY (catalog) REFERENCES catalog (id)
  ,FOREIGN KEY (band) REFERENCES frequencyband (id)
  )
;

