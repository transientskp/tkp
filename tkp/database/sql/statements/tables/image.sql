CREATE SEQUENCE seq_image AS INTEGER;

CREATE TABLE image 
  (id INT NOT NULL DEFAULT NEXT VALUE FOR seq_image
  ,dataset INT NOT NULL
  ,tau INT NULL
  ,band SMALLINT NOT NULL
  ,stokes TINYINT NOT NULL DEFAULT 1
  ,tau_time DOUBLE NULL
  ,freq_eff DOUBLE NOT NULL
  ,freq_bw DOUBLE NULL
  ,taustart_ts TIMESTAMP NOT NULL
  ,skyrgn INT NOT NULL
  ,rb_smaj DOUBLE NOT NULL
  ,rb_smin DOUBLE NOT NULL
  ,rb_pa DOUBLE NOT NULL
  ,deltax DOUBLE NOT NULL
  ,deltay DOUBLE NOT NULL
  ,fwhm_arcsec DOUBLE NULL
  ,fov_degrees DOUBLE NULL
  ,url VARCHAR(1024) NULL
  ,node TINYINT NOT NULL DEFAULT %NODE%
  ,nodes TINYINT NOT NULL DEFAULT %NODES%
  ,PRIMARY KEY (id)
  ,FOREIGN KEY (dataset) REFERENCES dataset (id)
  ,FOREIGN KEY (band) REFERENCES frequencyband (id)
  ,FOREIGN KEY (skyrgn) REFERENCES skyregion (id)
  );

