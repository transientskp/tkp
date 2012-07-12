/* TODO: The resolution element (from images table) is not implemented yet
*/

CREATE TABLE temprunningcatalog 
  (runcat INT NOT NULL
  ,xtrsrc INT NOT NULL
  ,dataset INT NOT NULL
  ,band INT NOT NULL
  ,stokes TINYINT NOT NULL DEFAULT 1
  ,datapoints INT NOT NULL
  ,zone INT NOT NULL
  ,wm_ra DOUBLE NOT NULL
  ,wm_decl DOUBLE NOT NULL
  ,wm_ra_err DOUBLE NOT NULL
  ,wm_decl_err DOUBLE NOT NULL
  ,avg_wra DOUBLE NOT NULL
  ,avg_wdecl DOUBLE NOT NULL
  ,avg_weight_ra DOUBLE NOT NULL
  ,avg_weight_decl DOUBLE NOT NULL
  ,x DOUBLE NOT NULL
  ,y DOUBLE NOT NULL
  ,z DOUBLE NOT NULL
  ,margin BOOLEAN NOT NULL DEFAULT 0
  ,beam_semimaj DOUBLE NULL
  ,beam_semimin DOUBLE NULL
  ,beam_pa DOUBLE NULL
  ,avg_f_peak DOUBLE NULL
  ,avg_f_peak_sq DOUBLE NULL
  ,avg_weight_peak DOUBLE NULL
  ,avg_weighted_f_peak DOUBLE NULL
  ,avg_weighted_f_peak_sq DOUBLE NULL
  ,FOREIGN KEY (runcat) REFERENCES runningcatalog (id)
  ,FOREIGN KEY (xtrsrc) REFERENCES extractedsource (id)
  ,FOREIGN KEY (dataset) REFERENCES dataset (id)
  ,FOREIGN KEY (band) REFERENCES frequencyband (id)
  )

;

