/**
 * Zone table has a row for each zone.
 * It is used to force the query optimizer to pick the right plan
 * zone:        FLOOR(latMin/zoneHeight)', 
 * decl_min:    min declination of this zone (in degrees)', 
 * decl_max:    max declination of this zone (in degrees)', 
 */
CREATE TABLE zones (
  zone INT NOT NULL, 
  decl_min DOUBLE, 
  decl_max DOUBLE, 
  PRIMARY KEY(zone)
) ENGINE=InnoDB;
