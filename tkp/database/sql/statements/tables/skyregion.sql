CREATE SEQUENCE seq_skyregion AS INTEGER;
/**
 * This table stores representations of regions of sky. 
 * centre_ra, centre_decl, and xtr_radius should all be in degrees.
 * x,y,z are the cartesian representation of the central ra,decl.
 */
CREATE TABLE skyregion 
  (id INTEGER NOT NULL DEFAULT NEXT VALUE FOR seq_skyregion
  ,dataset INTEGER NOT NULL
  ,centre_ra DOUBLE NOT NULL
  ,centre_decl DOUBLE NOT NULL
  ,xtr_radius DOUBLE NOT NULL
  ,x DOUBLE NOT NULL
  ,y DOUBLE NOT NULL
  ,z DOUBLE NOT NULL
  ,PRIMARY KEY (id)
  ,FOREIGN KEY (dataset) REFERENCES dataset (id)
  )
;

