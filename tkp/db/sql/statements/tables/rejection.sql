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

{% ifdb postgresql %}
CREATE INDEX "rejection_image" ON "rejection" ("image");
CREATE INDEX "rejection_rejectreason" ON "rejection" ("rejectreason");
{% endifdb %}