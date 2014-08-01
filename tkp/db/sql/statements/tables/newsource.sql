CREATE TABLE newsource
  (id SERIAL
  ,runcat INT NOT NULL
  ,band SMALLINT NOT NULL
  ,siglevel DOUBLE PRECISION DEFAULT 0
  ,v_int DOUBLE PRECISION NOT NULL
  ,eta_int DOUBLE PRECISION NOT NULL
  ,detection_level DOUBLE PRECISION DEFAULT 0
  ,trigger_xtrsrc INT NOT NULL
  ,newsource_type SMALLINT NOT NULL
  ,previous_limits_image INT NOT NULL
  ,status INT DEFAULT 0
  ,t_start TIMESTAMP
{% ifdb postgresql %}
  ,PRIMARY KEY (id)
{% endifdb %}
  ,FOREIGN KEY (runcat) REFERENCES runningcatalog (id)
  ,FOREIGN KEY (band) REFERENCES frequencyband (id)
  ,FOREIGN KEY (trigger_xtrsrc) REFERENCES extractedsource (id)
  ,FOREIGN KEY (previous_limits_image) REFERENCES image (id)
);

{% ifdb postgresql %}
CREATE INDEX "newsource_runcat" ON "newsource" ("runcat");
CREATE INDEX "newsource_band" ON "newsource" ("band");
CREATE INDEX "newsource_trigger_xtrsrc" ON "newsource" ("trigger_xtrsrc");
{% endifdb %}
