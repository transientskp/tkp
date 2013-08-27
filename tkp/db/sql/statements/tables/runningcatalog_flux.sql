CREATE TABLE runningcatalog_flux
  (id SERIAL
  ,runcat INT NOT NULL
  ,band SMALLINT NOT NULL
  ,stokes SMALLINT NOT NULL DEFAULT 1
  ,f_datapoints INT NOT NULL
  ,resolution DOUBLE PRECISION NULL
  ,avg_f_peak DOUBLE PRECISION NULL
  ,avg_f_peak_sq DOUBLE PRECISION NULL
  ,avg_f_peak_weight DOUBLE PRECISION NULL
  ,avg_weighted_f_peak DOUBLE PRECISION NULL
  ,avg_weighted_f_peak_sq DOUBLE PRECISION NULL
  ,avg_f_int DOUBLE PRECISION NULL
  ,avg_f_int_sq DOUBLE PRECISION NULL
  ,avg_f_int_weight DOUBLE PRECISION NULL
  ,avg_weighted_f_int DOUBLE PRECISION NULL
  ,avg_weighted_f_int_sq DOUBLE PRECISION NULL
  ,UNIQUE (runcat, band, stokes)
  ,FOREIGN KEY (runcat) REFERENCES runningcatalog (id)
  ,FOREIGN KEY (band) REFERENCES frequencyband (id)

{% ifdb postgresql %}
  ,PRIMARY KEY (id)
{% endifdb %}
);

{% ifdb postgresql %}
CREATE INDEX "runningcatalog_flux_band" ON "runningcatalog_flux" ("band");
{% endifdb %}