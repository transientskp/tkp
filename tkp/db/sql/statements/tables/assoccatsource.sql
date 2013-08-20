CREATE TABLE assoccatsource
  (id SERIAL
  ,xtrsrc INT NOT NULL
  ,catsrc INT NOT NULL
  ,type SMALLINT NOT NULL
  ,distance_arcsec DOUBLE PRECISION NULL
  ,r DOUBLE PRECISION NULL
  ,loglr DOUBLE PRECISION NULL

  ,UNIQUE (xtrsrc, catsrc)
  ,FOREIGN KEY (xtrsrc) REFERENCES extractedsource (id)
  ,FOREIGN KEY (catsrc) REFERENCES catalogedsource (id)

{% ifdb postgresql %}
  ,PRIMARY KEY (id)
{% endifdb %}
);

{% ifdb postgresql %}
CREATE INDEX "assoccatsource_catsrc" ON "assoccatsource" ("catsrc");
{% endifdb %}