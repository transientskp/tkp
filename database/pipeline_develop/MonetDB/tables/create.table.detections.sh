/**
 * This is a temporary table, used to load
 * the detections from the sources extracted
 * from an image.
 */

host=$1
dbname=$2
port=$3
node=$4
nodes=$5

tab_query="
CREATE TABLE detections 
  (lra DOUBLE NOT NULL 
  ,ldecl DOUBLE NOT NULL 
  ,lra_err DOUBLE NOT NULL 
  ,ldecl_err DOUBLE NOT NULL 
  ,lI_peak DOUBLE NULL 
  ,lI_peak_err DOUBLE NULL 
  ,lI_int DOUBLE NULL 
  ,lI_int_err DOUBLE NULL 
  ,ldet_sigma DOUBLE NOT NULL
  ,lsemimajor DOUBLE 
  ,lsemiminor DOUBLE 
  ,lpa DOUBLE 
  ,lnode TINYINT NOT NULL DEFAULT $node
  ,lnodes TINYINT NOT NULL DEFAULT $nodes
  )
;
"
mclient -h$host -d$dbname -p$port -s"$tab_query" || exit 1

