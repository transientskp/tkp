{% ifdb monetdb %}
CREATE SEQUENCE seq_image AS INTEGER;
CREATE TABLE image
  (id INTEGER NOT NULL DEFAULT NEXT VALUE FOR seq_image
{% endifdb %}


{% ifdb postgresql %}
CREATE TABLE image
  (id SERIAL
{% endifdb %}


  ,dataset INT NOT NULL
  ,tau INT NULL
  ,band SMALLINT NOT NULL
  ,stokes SMALLINT NOT NULL DEFAULT 1
  ,tau_time DOUBLE PRECISION NULL
  ,freq_eff DOUBLE PRECISION NOT NULL
  ,freq_bw DOUBLE PRECISION NULL
  ,taustart_ts TIMESTAMP NOT NULL
  ,skyrgn INT NOT NULL
  ,rb_smaj DOUBLE PRECISION NOT NULL
  ,rb_smin DOUBLE PRECISION NOT NULL
  ,rb_pa DOUBLE PRECISION NOT NULL
  ,deltax DOUBLE PRECISION NOT NULL
  ,deltay DOUBLE PRECISION NOT NULL
  ,fwhm_arcsec DOUBLE PRECISION NULL
  ,fov_degrees DOUBLE PRECISION NULL
  ,url VARCHAR(1024) NULL
  ,rms_avg DOUBLE PRECISION NOT NULL
  ,node SMALLINT NOT NULL DEFAULT %NODE%
  ,nodes SMALLINT NOT NULL DEFAULT %NODES%
  ,PRIMARY KEY (id)
  ,FOREIGN KEY (dataset) REFERENCES dataset (id)
  ,FOREIGN KEY (band) REFERENCES frequencyband (id)
  ,FOREIGN KEY (skyrgn) REFERENCES skyregion (id)
  );

{% ifdb postgresql %}
CREATE INDEX "image_dataset" ON "image" ("dataset");
CREATE INDEX "image_band" ON "image" ("band");
CREATE INDEX "image_skyrgn" ON "image" ("skyrgn");
CREATE INDEX "image_taustart_ts" ON "image" ("taustart_ts");
{% endifdb %}

