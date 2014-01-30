CREATE TABLE assocxtrsource
  (id SERIAL
  ,runcat INT NOT NULL
  ,xtrsrc INT NULL
  ,type SMALLINT NOT NULL
  ,distance_arcsec DOUBLE PRECISION NULL
  ,r DOUBLE PRECISION NULL
  ,loglr DOUBLE PRECISION NULL
  ,v_int DOUBLE PRECISION NOT NULL
  ,eta_int DOUBLE PRECISION NOT NULL
  ,UNIQUE (runcat, xtrsrc)
  ,FOREIGN KEY (runcat) REFERENCES runningcatalog (id)
  ,FOREIGN KEY (xtrsrc) REFERENCES extractedsource (id)

{% ifdb postgresql %}
  ,PRIMARY KEY (id)
{% endifdb %}
);

{% ifdb postgresql %}
CREATE INDEX "assocxtrsource_xtrsrc" ON "assocxtrsource" ("xtrsrc");
{% endifdb %}
