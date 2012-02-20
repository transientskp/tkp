#!/bin/bash

/**
 * This table keeps track of the versions and changes
 */

host=$1
dbname=$2
port=$3
node=$4
nodes=$5

seq_query="
CREATE SEQUENCE \"seq_versions\" AS INTEGER;
"

mclient -h$host -d$dbname -p$port -s"$seq_query" || exit 1

tab_query="
CREATE TABLE versions 
  (versionid INT DEFAULT NEXT VALUE FOR \"seq_versions\"
  ,version VARCHAR(32) NULL
  ,creation_ts TIMESTAMP NOT NULL
  ,monet_version VARCHAR(8) NOT NULL
  ,monet_release VARCHAR(32) NOT NULL
  ,node TINYINT NOT NULL DEFAULT $node
  ,nodes TINYINT NOT NULL DEFAULT $nodes
  ,scriptname VARCHAR(256) NULL
  ,PRIMARY KEY (versionid)
  )
;
"

mclient -h$host -d$dbname -p$port -s"$tab_query" || exit 1

