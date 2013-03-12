/* TODO: The resolution element (from images table) is not implemented yet
*/

CREATE TABLE temprunningcatalog 
  (runcat INT NOT NULL
  ,xtrsrc INT NOT NULL
  ,distance_arcsec DOUBLE PRECISION NOT NULL
  ,r DOUBLE PRECISION NOT NULL
  ,dataset INT NOT NULL
  ,band SMALLINT NOT NULL
  ,stokes SMALLINT NOT NULL DEFAULT 1
  ,datapoints INT NOT NULL
  ,zone INT NOT NULL
  ,wm_ra DOUBLE PRECISION NOT NULL
  ,wm_decl DOUBLE PRECISION NOT NULL
  ,wm_ra_err DOUBLE PRECISION NOT NULL
  ,wm_decl_err DOUBLE PRECISION NOT NULL
  ,avg_wra DOUBLE PRECISION NOT NULL
  ,avg_wdecl DOUBLE PRECISION NOT NULL
  ,avg_weight_ra DOUBLE PRECISION NOT NULL
  ,avg_weight_decl DOUBLE PRECISION NOT NULL
  ,x DOUBLE PRECISION NOT NULL
  ,y DOUBLE PRECISION NOT NULL
  ,z DOUBLE PRECISION NOT NULL
  ,margin BOOLEAN NOT NULL DEFAULT FALSE
  ,inactive BOOLEAN NOT NULL DEFAULT FALSE
  ,beam_semimaj DOUBLE PRECISION NULL
  ,beam_semimin DOUBLE PRECISION NULL
  ,beam_pa DOUBLE PRECISION NULL
  ,f_datapoints INT NULL
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
  ,FOREIGN KEY (runcat) REFERENCES runningcatalog (id)
  ,FOREIGN KEY (xtrsrc) REFERENCES extractedsource (id)
  ,FOREIGN KEY (dataset) REFERENCES dataset (id)
  ,FOREIGN KEY (band) REFERENCES frequencyband (id)
  )

;

