/**
 * Zones table has a row for each zone.
 * This table is used in the sharded databases environment, where each
 * node has its own zone(s). 
 * 
 * zone:        FLOOR(decl_min/zoneheight),
 *              where zoneheight is set to 1 degree (for now)
 * decl_min:    min declination of this zone (in degrees) 
 * decl_max:    max declination of this zone (in degrees)
 */
CREATE TABLE zones 
  (zone INT NOT NULL
  ,zoneheight DOUBLE NOT NULL
  ,decl_min DOUBLE NOT NULL
  ,decl_max DOUBLE NOT NULL
  ,PRIMARY KEY (zone)
  )
;

