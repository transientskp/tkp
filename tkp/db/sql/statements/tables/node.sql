CREATE TABLE node
  (id SERIAL
  ,node SMALLINT NOT NULL DEFAULT %NODE%
  ,zone SMALLINT NOT NULL
  ,zone_min SMALLINT
  ,zone_max SMALLINT
  ,zone_min_incl BOOLEAN DEFAULT TRUE
  ,zone_max_incl BOOLEAN DEFAULT FALSE
  ,zoneheight DOUBLE PRECISION DEFAULT 1.0
  ,nodes SMALLINT NOT NULL DEFAULT %NODES%
  ,UNIQUE (node, zone)

{% ifdb postgresql %}
  ,PRIMARY KEY (id)
{% endifdb %}
  )
;
