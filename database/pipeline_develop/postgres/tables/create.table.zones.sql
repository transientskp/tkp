/**
 * Zone table has a row for each zone.
 * It is used to force the query optimizer to pick the right plan
 * zone:        FLOOR(latMin/zoneHeight)', 
 * decl_min:    min declination of this zone (in degrees)', 
 * decl_max:    max declination of this zone (in degrees)', 
 */
CREATE TABLE zones (
  zone PRIMARY KEY, 
  decl_min double precision, 
  decl_max double precision, 
);
