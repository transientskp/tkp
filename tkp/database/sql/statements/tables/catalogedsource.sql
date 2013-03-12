/**
 * TODO: Probably it is better not te set catsrcid to auto_incr,
 * because we will copy them from the catalog database.
 */

CREATE TABLE catalogedsource 
  (id SERIAL
  ,catalog SMALLINT NOT NULL
  ,orig_catsrcid INT NOT NULL
  ,catsrcname VARCHAR(120) NULL
  ,tau INT NULL
  ,band SMALLINT NOT NULL
  ,stokes SMALLINT NOT NULL DEFAULT 1
  ,freq_eff DOUBLE PRECISION NOT NULL
  ,zone INT NOT NULL
  ,ra DOUBLE PRECISION NOT NULL
  ,decl DOUBLE PRECISION NOT NULL
  ,ra_err DOUBLE PRECISION NOT NULL
  ,decl_err DOUBLE PRECISION NOT NULL
  ,x DOUBLE PRECISION NOT NULL
  ,y DOUBLE PRECISION NOT NULL
  ,z DOUBLE PRECISION NOT NULL
  ,margin BOOLEAN NOT NULL DEFAULT FALSE
  ,det_sigma DOUBLE PRECISION NOT NULL DEFAULT 0
  ,src_type VARCHAR(1) NULL
  ,fit_probl VARCHAR(2) NULL
  ,PA DOUBLE PRECISION NULL
  ,PA_err DOUBLE PRECISION NULL
  ,major DOUBLE PRECISION NULL
  ,major_err DOUBLE PRECISION NULL
  ,minor DOUBLE PRECISION NULL
  ,minor_err DOUBLE PRECISION NULL
  ,avg_f_peak DOUBLE PRECISION NULL
  ,avg_f_peak_err DOUBLE PRECISION NULL
  ,avg_f_int DOUBLE PRECISION NULL
  ,avg_f_int_err DOUBLE PRECISION NULL
  ,frame VARCHAR(20) NULL
{% ifdb postgresql %}
  ,PRIMARY KEY (id)
{% endifdb %}
  ,FOREIGN KEY (catalog) REFERENCES catalog (id)
  ,FOREIGN KEY (band) REFERENCES frequencyband (id)
  )
;

