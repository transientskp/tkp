/*
 * Entries in this table signify that a runningcatalog source location 
 * lies within a skyregion.
*/
CREATE TABLE assocskyrgn
  (runcat INT NOT NULL
  ,skyrgn INT NOT NULL
  ,distance_deg DOUBLE 
  ,FOREIGN KEY (runcat) REFERENCES runningcatalog (id)
  ,FOREIGN KEY (skyrgn) REFERENCES skyregion (id)
);

