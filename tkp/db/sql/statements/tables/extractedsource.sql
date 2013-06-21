CREATE TABLE extractedsource
  (id SERIAL
  ,image INT NOT NULL
  ,zone INT NOT NULL
  ,ra DOUBLE PRECISION NOT NULL
  ,decl DOUBLE PRECISION NOT NULL
  ,ra_err DOUBLE PRECISION NOT NULL
  ,decl_err DOUBLE PRECISION NOT NULL
  ,ra_fit_err DOUBLE PRECISION NOT NULL
  ,decl_fit_err DOUBLE PRECISION NOT NULL
  ,ra_sys_err DOUBLE PRECISION NOT NULL
  ,decl_sys_err DOUBLE PRECISION NOT NULL
  ,x DOUBLE PRECISION NOT NULL
  ,y DOUBLE PRECISION NOT NULL
  ,z DOUBLE PRECISION NOT NULL
  ,racosdecl DOUBLE PRECISION NOT NULL
  ,margin BOOLEAN NOT NULL DEFAULT FALSE
  ,det_sigma DOUBLE PRECISION NOT NULL
  ,semimajor DOUBLE PRECISION NULL
  ,semiminor DOUBLE PRECISION NULL
  ,pa DOUBLE PRECISION NULL
  ,f_peak DOUBLE PRECISION NULL
  ,f_peak_err DOUBLE PRECISION NULL
  ,f_int DOUBLE PRECISION NULL
  ,f_int_err DOUBLE PRECISION NULL
  ,extract_type SMALLINT NULL
  ,node SMALLINT NOT NULL DEFAULT %NODE%
  ,nodes SMALLINT NOT NULL DEFAULT %NODES%
{% ifdb postgresql %}
  ,PRIMARY KEY (id)
{% endifdb %}
  ,FOREIGN KEY (image) REFERENCES image (id)
  )
;

{% ifdb postgresql %}
CREATE INDEX "extractedsource_image" ON "extractedsource" ("image");
CREATE INDEX "extractedsource_decl" ON "extractedsource" ("decl");
CREATE INDEX "extractedsource_ra" ON "extractedsource" ("ra");
CREATE INDEX "extractedsource_x" ON "extractedsource" ("x");
CREATE INDEX "extractedsource_y" ON "extractedsource" ("y");
CREATE INDEX "extractedsource_z" ON "extractedsource" ("z");
CREATE INDEX "extractedsource_ra_err" ON "extractedsource" ("ra_err");
CREATE INDEX "extractedsource_decl_err" ON "extractedsource" ("decl_err");
{% endifdb %}

