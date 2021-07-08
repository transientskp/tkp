#!/bin/bash

THIS_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)"

export TKP_TESTPATH=${THIS_SCRIPT_DIR}/data
export TKP_DBNAME=testdb
export TKP_MAXTESTDURATION=5

echo "****************************"
echo "POSTGRES:"
echo "****************************"
export TKP_DBENGINE=postgresql
export TKP_DBUSER=$USER
export TKP_DBPASSWORD=$USER
python ./runtests.py $*

