--DROP TABLE crosscatalogedsources;
CREATE TABLE crosscatalogedsources
  (catsrc_id INT NOT NULL
  ,datapoints INT NOT NULL
  ,zone INT NOT NULL
  ,wm_ra double precision NOT NULL
  ,wm_decl double precision NOT NULL
  ,wm_ra_err double precision NOT NULL
  ,wm_decl_err double precision NOT NULL
  ,avg_wra double precision NOT NULL
  ,avg_wdecl double precision NOT NULL
  ,avg_weight_ra double precision NOT NULL
  ,avg_weight_decl double precision NOT NULL
  ,x double precision NOT NULL
  ,y double precision NOT NULL
  ,z double precision NOT NULL
  ,margin boolean not null default false
  )
;

