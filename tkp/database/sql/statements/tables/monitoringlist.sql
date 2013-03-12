CREATE TABLE monitoringlist
  (id SERIAL
  ,runcat INTEGER NULL
  ,ra DOUBLE PRECISION DEFAULT 0
  ,decl DOUBLE PRECISION DEFAULT 0
  ,dataset INTEGER NOT NULL
  ,userentry BOOLEAN DEFAULT FALSE
{% ifdb postgresql %}
  ,PRIMARY KEY (id)
{% endifdb %}
  ,FOREIGN KEY (runcat) REFERENCES runningcatalog (id)
  ,FOREIGN KEY (dataset) REFERENCES dataset (id)
  )
;
