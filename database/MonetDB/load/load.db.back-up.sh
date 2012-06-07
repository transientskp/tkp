#!/bin/sh
# This script loads the requested back-upped database into MonetDB.
# The input file, which is really th edump file used as database back-up,
# contains all the db definitions and db content.
#
# input arguments
# $1: database
# $2: database back-up file
# $3: username
# $4: password
#
# Run it f.ex. like:
# %> ./load.db.back-up.sh pipeline_develop dump.pipeline_develop.20110401-1952.sql lofar cs1
# 


echo "--------------------------------"
echo "Executing script                "
echo "--------------------------------"

./load.db.back-up.batch $1 $2 $3 $4> $HOME/log/back-ups/$1.`date +\%F`.log 2> $HOME/log/back-ups/$1.`date +\%F`.errlog

echo "--------------------------------"
echo "Script Executed                 "
echo "--------------------------------"

