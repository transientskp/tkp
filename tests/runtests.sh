#!/bin/bash

export TKP_TESTPATH=/data2/repos/tkp-data/unittests/tkp_lib 
export TKP_DBNAME=testdb

#echo "****************************"
#echo "MONETDB:"
#echo "****************************"
#export TKP_DBENGINE=monetdb
#python ./runtests.py $*


echo "****************************"
echo "POSTGRES:"
echo "****************************"
export TKP_DBENGINE=postgresql
export TKP_DBUSER=postgres
python ./runtests.py $*

