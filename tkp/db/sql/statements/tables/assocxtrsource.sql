CREATE TABLE assocxtrsource
  (runcat INT NOT NULL
  ,xtrsrc INT NULL
  ,type SMALLINT NOT NULL
  ,distance_arcsec DOUBLE PRECISION NULL
  ,r DOUBLE PRECISION NULL
  ,loglr DOUBLE PRECISION NULL
  ,PRIMARY KEY (runcat, xtrsrc)
  ,FOREIGN KEY (runcat) REFERENCES runningcatalog (id)
  ,FOREIGN KEY (xtrsrc) REFERENCES extractedsource (id)
);

{% ifdb postgresql %}
CREATE INDEX "assocxtrsource_xtrsrc" ON "assocxtrsource" ("xtrsrc");
{% endifdb %}