CREATE TABLE config
  (id SERIAL
  ,dataset INT NOT NULL
  ,section VARCHAR(100)
  ,key VARCHAR(100)
  ,value VARCHAR(500)
  ,type VARCHAR(5)

  ,UNIQUE (dataset, section, key)
  ,FOREIGN KEY (dataset) REFERENCES dataset (id)

{% ifdb postgresql %}
  ,PRIMARY KEY (id)
{% endifdb %}

)
;
