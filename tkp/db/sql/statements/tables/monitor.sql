CREATE TABLE monitor
  (id SERIAL
  ,dataset INT NOT NULL
  ,ra DOUBLE PRECISION NOT NULL
  ,decl DOUBLE PRECISION NOT NULL
  ,runcat INT NULL
  ,name VARCHAR(100) NULL

{% ifdb postgresql %}
  ,PRIMARY KEY (id)
{% endifdb %}
  ,FOREIGN KEY (dataset) REFERENCES dataset (id)
  ,FOREIGN KEY (runcat) REFERENCES runningcatalog (id)
);

{% ifdb postgresql %}
CREATE INDEX "monitor_dataset" ON "monitor" ("dataset");
{% endifdb %}

