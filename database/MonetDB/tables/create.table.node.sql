/**
 * This table keeps track of the versions and changes
 */

CREATE TABLE node 
  (node TINYINT NOT NULL DEFAULT %NODE%
  ,zone SMALLINT NOT NULL
  ,zone_min SMALLINT
  ,zone_max SMALLINT
  ,zone_min_incl BOOLEAN DEFAULT TRUE
  ,zone_max_incl BOOLEAN DEFAULT FALSE
  ,zoneheight DOUBLE DEFAULT 1.0
  ,nodes TINYINT NOT NULL DEFAULT %NODES%
  )
;
