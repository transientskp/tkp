CREATE TABLE rejection
  (id SERIAL
  ,image INT
  ,rejectreason INT
  ,comment VARCHAR(512)
{% ifdb postgresql %}
  ,PRIMARY KEY (id)
{% endifdb %}
  ,FOREIGN KEY (image) REFERENCES image(id)
  ,FOREIGN KEY (rejectreason) REFERENCES rejectreason(id)
);
