/* 
 * TODO: The resolution element (from images table) is not implemented yet
*/

CREATE TABLE runningcatalog
  (id SERIAL
  ,xtrsrc INT NOT NULL
  ,dataset INT NOT NULL
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
{% ifdb postgresql %}
  ,PRIMARY KEY(id)
{% endifdb %}
  ,UNIQUE (xtrsrc)
  ,FOREIGN KEY (xtrsrc) REFERENCES extractedsource (id)
  ,FOREIGN KEY (dataset) REFERENCES dataset (id)
  )
;

