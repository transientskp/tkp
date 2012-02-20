#!/bin/bash
#/**
# * This table is node specific. 
# * It contains the zones of the sources that are
# * stored on its node.
# */

host=$1
dbname=$2
port=$3
node=$4
nodes=$5

tab_query="
CREATE TABLE node 
  (node TINYINT NOT NULL DEFAULT $node
  ,zone SMALLINT NOT NULL
  ,zone_min SMALLINT
  ,zone_max SMALLINT
  ,zone_min_incl BOOLEAN DEFAULT TRUE
  ,zone_max_incl BOOLEAN DEFAULT FALSE
  ,zoneheight DOUBLE DEFAULT 1.0
  ,nodes TINYINT NOT NULL DEFAULT $nodes
  )
;
"

mclient -h$host -d$dbname -p$port -s"$tab_query" || exit 1

