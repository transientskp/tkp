CREATE TABLE transient 
  (id SERIAL
  ,runcat INT NOT NULL
  ,band SMALLINT NOT NULL
  ,siglevel DOUBLE PRECISION DEFAULT 0
  ,v_int DOUBLE PRECISION
  ,eta_int DOUBLE PRECISION
  ,detection_level DOUBLE PRECISION DEFAULT 0
  ,trigger_xtrsrc INT NOT NULL
  ,status INT DEFAULT 0
  ,t_start TIMESTAMP
{% ifdb postgresql %}
  ,PRIMARY KEY (id)
{% endifdb %}
  ,FOREIGN KEY (runcat) REFERENCES runningcatalog (id)
  ,FOREIGN KEY (band) REFERENCES frequencyband (id)
  ,FOREIGN KEY (trigger_xtrsrc) REFERENCES extractedsource (id)
);

