/**
 * This table stores representations of regions of sky. 
 * centre_ra, centre_decl, and xtr_radius should all be in degrees.
 * x,y,z are the cartesian representation of the central ra,decl.
 */

{% ifdb monetdb %}
CREATE SEQUENCE seq_skyregion AS INTEGER;
CREATE TABLE skyregion
  (id INTEGER NOT NULL DEFAULT NEXT VALUE FOR seq_skyregion
{% endifdb %}


{% ifdb postgresql %}
CREATE TABLE skyregion
  (id SERIAL
{% endifdb %}


  ,dataset INTEGER NOT NULL
  ,centre_ra DOUBLE PRECISION NOT NULL
  ,centre_decl DOUBLE PRECISION NOT NULL
  ,xtr_radius DOUBLE PRECISION NOT NULL
  ,x DOUBLE PRECISION NOT NULL
  ,y DOUBLE PRECISION NOT NULL
  ,z DOUBLE PRECISION NOT NULL
  ,PRIMARY KEY (id)
  ,FOREIGN KEY (dataset) REFERENCES dataset (id)
  )
;

{% ifdb postgresql %}
CREATE INDEX "skyregion_dataset" ON "skyregion" ("dataset");
{% endifdb %}