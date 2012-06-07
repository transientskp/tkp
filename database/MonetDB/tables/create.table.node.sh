/**
 * This table keeps track of the versions and changes
 */
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
  ,zone_min_incl DEFAULT TRUE
  ,zone_max_incl DEFAULT FALSE
  ,zoneheight DOUBLE DEFAULT 1.0
  ,nodes TINYINT NOT NULL DEFAULT $nodes
  )
;
"

mclient -h$host -d$dbname -p$port -s"$tab_query" || exit 1

