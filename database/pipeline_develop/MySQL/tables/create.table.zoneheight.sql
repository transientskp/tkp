/**
 * Use of zoneheight drives the parameters of all the other tables.
 * Invoke BuildZones(zoneheight, theta) to change height 
 * and rebuild the indices.
 * zoneheight:  in degrees
 */
CREATE TABLE zoneheight ( 
  zoneheight DOUBLE NOT NULL
) ENGINE=InnoDB;
