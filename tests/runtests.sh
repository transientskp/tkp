#!/bin/bash

THIS_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)"

export TKP_TESTPATH=${THIS_SCRIPT_DIR}/data
export TKP_DBNAME=testdb
export TKP_MAXTESTDURATION=5
#export TKP_TESTDBMANAGEMENT=1

#echo "****************************"
#echo "MONETDB:"
#echo "****************************"
#export TKP_DBENGINE=monetdb
#export TKP_DBUSER=monetdb
#export TKP_DBPASSWORD=monetdb
#python ./runtests.py $*


echo "****************************"
echo "POSTGRES:"
echo "****************************"
export TKP_DBENGINE=postgresql
export TKP_DBUSER=postgres
python ./runtests.py $*

