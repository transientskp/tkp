CREATE TABLE newsource
  (id SERIAL
  ,runcat INT NOT NULL
  ,trigger_xtrsrc INT NOT NULL
  ,newsource_type SMALLINT NOT NULL
  ,previous_limits_image INT NOT NULL
{% ifdb postgresql %}
  ,PRIMARY KEY (id)
{% endifdb %}
  ,FOREIGN KEY (runcat) REFERENCES runningcatalog (id)
  ,FOREIGN KEY (trigger_xtrsrc) REFERENCES extractedsource (id)
  ,FOREIGN KEY (previous_limits_image) REFERENCES image (id)
);

{% ifdb postgresql %}
CREATE INDEX "newsource_runcat" ON "newsource" ("runcat");
CREATE INDEX "newsource_trigger_xtrsrc" ON "newsource" ("trigger_xtrsrc");
{% endifdb %}
