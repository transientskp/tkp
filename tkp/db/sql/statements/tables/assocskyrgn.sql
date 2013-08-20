/*
 * Entries in this table signify that a runningcatalog source location
 * lies within a skyregion.
*/
CREATE TABLE assocskyrgn
  (id SERIAL
  ,runcat INT NOT NULL
  ,skyrgn INT NOT NULL
  ,distance_deg DOUBLE PRECISION
  ,FOREIGN KEY (runcat) REFERENCES runningcatalog (id)
  ,FOREIGN KEY (skyrgn) REFERENCES skyregion (id)

{% ifdb postgresql %}
  ,PRIMARY KEY (id)
{% endifdb %}
);

{% ifdb postgresql %}
CREATE INDEX "assocskyrgn_runcat" ON "assocskyrgn" ("runcat");
CREATE INDEX "assocskyrgn_skyrgn" ON "assocskyrgn" ("skyrgn");
{% endifdb %}