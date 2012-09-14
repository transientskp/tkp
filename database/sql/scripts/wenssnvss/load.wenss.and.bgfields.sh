#!/usr/bin/env bash

# arguments:
# $1 host
# $2 database
# $3 dbuser
# $4 dbpw


# An example call of this script could be:
# %> ./load.wenss.and.bgfields.sh ldb001 pipeline_wenssnvss wenssnvss ch3
# The procedure will process all the wenss sources as if they were extracted from 
# the source extraction modules in our TKP-pipeline.
# Then, every source is offset by 180", and this is done eight times,
# where the 8 offset sources lie on a rectangular 3x3 grid with the
# wenss source in the middle. These Background sources are also 
# processed as if they were extracted from the source extraction modules

#host=${1}
#db=${2}
#dbuser=${3}
#dbpasswd=${4}

echo "calling procedure LoadWenssSourceAndBGFields()"
$MONETDBCLIENT/mclient -t -lsql -h$1 -d$2 -u$3 -P$4 <<-EOF
CALL LoadWenssSourceAndBGFields();
EOF

echo -e "-----"
echo -e "READY"
echo -e "-----"

