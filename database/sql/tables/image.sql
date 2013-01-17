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
  ,centre_ra DOUBLE NULL
  ,centre_decl DOUBLE NULL
  ,x DOUBLE NULL
  ,y DOUBLE NULL
  ,z DOUBLE NULL
  ,bmaj_syn DOUBLE NULL
  ,bmin_syn DOUBLE NULL
  ,bpa_syn DOUBLE NULL
  ,fwhm_arcsec DOUBLE NULL
  ,fov_degrees DOUBLE NULL
  ,rejected BOOLEAN NOT NULL DEFAULT FALSE
  ,url VARCHAR(1024) NULL
  ,node TINYINT NOT NULL DEFAULT %NODE%
  ,nodes TINYINT NOT NULL DEFAULT %NODES%
  ,PRIMARY KEY (id)
  ,FOREIGN KEY (dataset) REFERENCES dataset (id)
  ,FOREIGN KEY (band) REFERENCES frequencyband (id)
  );

