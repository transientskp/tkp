--DROP TABLE tempcrosscatalogedsources;
CREATE TABLE tempcrosscatalogedsources
  (catsrc_id INT NOT NULL
  ,assoc_catsrc_id INT NOT NULL
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
  )
;

