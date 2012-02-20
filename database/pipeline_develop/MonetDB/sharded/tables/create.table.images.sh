#!/bin/bash
#/**
# * This table contains the images that are being processed.
# * The only format for now is FITS. The HDF5 format will be implemented
# * later.
# * An image is characterised by
# *      - integration time (tau)
# *      - frequency band (band) 
# *      - timestamp (seq_nr).
# * A group of images that belong together (not specified any further)
# * are in the same data set (they have the same ds_id).
# * tau_time in seconds (ref. tau)
# * freq_eff in Hz (ref. band)
# * taustart_timestamp in YYYY-MM-DD-HH:mm:ss:nnnnnn, but without 
# *                    interpunctions (ref. seq_nr)
# */

host=$1
dbname=$2
port=$3
node=$4
nodes=$5

seq_query="
CREATE SEQUENCE \"seq_images\" AS INTEGER;
"

mclient -h$host -d$dbname -p$port -s"$seq_query" || exit 1

tab_query="
CREATE TABLE images 
  (imageid INT DEFAULT NEXT VALUE FOR \"seq_images\"
  ,ds_id INT NOT NULL
  ,tau INT NOT NULL
  ,band INT NOT NULL
  ,stokes CHAR(1) NOT NULL DEFAULT 'I'
  ,tau_time DOUBLE NOT NULL
  ,freq_eff DOUBLE NOT NULL
  ,freq_bw DOUBLE NULL
  ,taustart_ts TIMESTAMP NOT NULL
  ,bmaj_syn DOUBLE NULL
  ,bmin_syn DOUBLE NULL
  ,bpa_syn DOUBLE NULL
  ,url VARCHAR(120) NULL
  ,node TINYINT NOT NULL DEFAULT $node
  ,nodes TINYINT NOT NULL DEFAULT $nodes
  ,PRIMARY KEY (imageid)
  ,FOREIGN KEY (ds_id) REFERENCES datasets (dsid)
  ,FOREIGN KEY (band) REFERENCES frequencybands (freqbandid)
  )
;
"

mclient -h$host -d$dbname -p$port -s"$tab_query" || exit 1

