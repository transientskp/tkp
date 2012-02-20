#!/bin/bash
#/**
# * This table contains the information about the dataset that is produced by LOFAR. 
# * A dataset has an integration time and consists of multiple frequency layers.
# * taustart_timestamp:  the start time of the integration
# */

host=$1
dbname=$2
port=$3
node=$4
nodes=$5

seq_query="
CREATE SEQUENCE \"seq_datasets\" AS INTEGER;
"

mclient -h$1 -d$2 -p$3 -s"$seq_query" || exit 1

tab_query="
CREATE TABLE datasets 
  (dsid INT DEFAULT NEXT VALUE FOR \"seq_datasets\"
  ,rerun INT NOT NULL DEFAULT '0'
  ,dstype TINYINT NOT NULL
  ,process_ts TIMESTAMP NOT NULL
  ,dsinname VARCHAR(64) NOT NULL
  ,dsoutname VARCHAR(64) DEFAULT NULL
  ,description VARCHAR(100) DEFAULT NULL
  ,node TINYINT NOT NULL DEFAULT $node
  ,nodes TINYINT NOT NULL DEFAULT $nodes
  ,PRIMARY KEY (dsid)
)
;
"

mclient -h$host -d$dbname -p$port -s"$tab_query" || exit 1

