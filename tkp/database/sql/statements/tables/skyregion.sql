/**
 * This table stores representations of regions of sky. 
 * centre_ra, centre_decl, and xtr_radius should all be in degrees.
 * x,y,z are the cartesian representation of the central ra,decl.
 */
CREATE TABLE skyregion 
  (id SERIAL
  ,dataset INTEGER NOT NULL
  ,centre_ra DOUBLE PRECISION NOT NULL
  ,centre_decl DOUBLE PRECISION NOT NULL
  ,xtr_radius DOUBLE PRECISION NOT NULL
  ,x DOUBLE PRECISION NOT NULL
  ,y DOUBLE PRECISION NOT NULL
  ,z DOUBLE PRECISION NOT NULL
{% ifdb postgresql %}
  ,PRIMARY KEY (id)
{% endifdb %}
  ,FOREIGN KEY (dataset) REFERENCES dataset (id)
  )
;

