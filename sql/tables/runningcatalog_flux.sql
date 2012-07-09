CREATE TABLE runningcatalog_flux
  (runcat INT NOT NULL
  ,band INT NOT NULL
  ,stokes TINYINT NOT NULL DEFAULT 1
  ,f_datapoints INT NOT NULL
  ,resolution DOUBLE NULL
  ,avg_f_peak DOUBLE NULL
  ,avg_f_peak_sq DOUBLE NULL
  ,avg_f_peak_weight DOUBLE NULL
  ,avg_weighted_f_peak DOUBLE NULL
  ,avg_weighted_f_peak_sq DOUBLE NULL
  ,avg_f_int DOUBLE NULL
  ,avg_f_int_sq DOUBLE NULL
  ,avg_f_int_weight DOUBLE NULL
  ,avg_weighted_f_int DOUBLE NULL
  ,avg_weighted_f_int_sq DOUBLE NULL
  ,PRIMARY KEY (runcat_id
               ,band
               ,stokes
               )
  ,FOREIGN KEY (runcat) REFERENCES runningcatalog (id)
  ,FOREIGN KEY (band) REFERENCES frequencyband (id)
  )
;

