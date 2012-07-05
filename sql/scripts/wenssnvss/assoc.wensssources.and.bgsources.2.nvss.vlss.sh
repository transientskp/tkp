#!/usr/bin/env bash

# arguments:
# $1 host
# $2 database
# $3 dbuser
# $4 dbpw


# An example call of this script could be:
# %> ./scriptname.sh ldb001 pipeline_wenssnvss wenssnvss ch3
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

echo "calling LoadWenssSourceAndBGFields()"
mclient -t -lsql -h$1 -d$2 -u$3 -P$4 <<-EOF
CALL LoadWenssSourceAndBGFields();
EOF

echo "calling LoadLSM(0, 360, -90, 90, 'NVSS', 'VLSS', '')"
mclient -t -lsql -h$1 -d$2 -u$3 -P$4 <<-EOF
CALL LoadLSM(0, 360, -90, 90, 'NVSS', 'VLSS', '');
EOF

echo "calling AssocWenssSources2CatByZones(1)"
mclient -t -lsql -h$1 -d$2 -u$3 -P$4 <<-EOF
CALL AssocWenssSources2CatByZones(1);
EOF

echo "calling AssocWenssSources2CatByZones(2)"
mclient -t -lsql -h$1 -d$2 -u$3 -P$4 <<-EOF
CALL AssocWenssSources2CatByZones(2);
EOF

echo "calling AssocWenssSources2CatByZones(3)"
mclient -t -lsql -h$1 -d$2 -u$3 -P$4 <<-EOF
CALL AssocWenssSources2CatByZones(3);
EOF

echo "calling AssocWenssSources2CatByZones(4)"
mclient -t -lsql -h$1 -d$2 -u$3 -P$4 <<-EOF
CALL AssocWenssSources2CatByZones(4);
EOF

echo "calling AssocWenssSources2CatByZones(5)"
mclient -t -lsql -h$1 -d$2 -u$3 -P$4 <<-EOF
CALL AssocWenssSources2CatByZones(5);
EOF

echo "calling AssocWenssSources2CatByZones(6)"
mclient -t -lsql -h$1 -d$2 -u$3 -P$4 <<-EOF
CALL AssocWenssSources2CatByZones(6);
EOF

echo "calling AssocWenssSources2CatByZones(7)"
mclient -t -lsql -h$1 -d$2 -u$3 -P$4 <<-EOF
CALL AssocWenssSources2CatByZones(7);
EOF

echo "calling AssocWenssSources2CatByZones(8)"
mclient -t -lsql -h$1 -d$2 -u$3 -P$4 <<-EOF
CALL AssocWenssSources2CatByZones(8);
EOF

echo "calling AssocWenssSources2CatByZones(9)"
mclient -t -lsql -h$1 -d$2 -u$3 -P$4 <<-EOF
CALL AssocWenssSources2CatByZones(9);
EOF

echo "calling AssocWenssSources2CatByZones(10)"
mclient -t -lsql -h$1 -d$2 -u$3 -P$4 <<-EOF
CALL AssocWenssSources2CatByZones(10);
EOF

echo "calling AssocWenssSources2CatByZones(11)"
mclient -t -lsql -h$1 -d$2 -u$3 -P$4 <<-EOF
CALL AssocWenssSources2CatByZones(11);
EOF

echo "calling AssocWenssSources2CatByZones(12)"
mclient -t -lsql -h$1 -d$2 -u$3 -P$4 <<-EOF
CALL AssocWenssSources2CatByZones(12);
EOF

echo "calling AssocWenssSources2CatByZones(13)"
mclient -t -lsql -h$1 -d$2 -u$3 -P$4 <<-EOF
CALL AssocWenssSources2CatByZones(13);
EOF

echo "calling AssocWenssSources2CatByZones(14)"
mclient -t -lsql -h$1 -d$2 -u$3 -P$4 <<-EOF
CALL AssocWenssSources2CatByZones(14);
EOF

echo "calling AssocWenssSources2CatByZones(15)"
mclient -t -lsql -h$1 -d$2 -u$3 -P$4 <<-EOF
CALL AssocWenssSources2CatByZones(15);
EOF

echo "calling AssocWenssSources2CatByZones(16)"
mclient -t -lsql -h$1 -d$2 -u$3 -P$4 <<-EOF
CALL AssocWenssSources2CatByZones(16);
EOF

echo "calling AssocWenssSources2CatByZones(17)"
mclient -t -lsql -h$1 -d$2 -u$3 -P$4 <<-EOF
CALL AssocWenssSources2CatByZones(17);
EOF

echo "calling AssocWenssSources2CatByZones(18)"
mclient -t -lsql -h$1 -d$2 -u$3 -P$4 <<-EOF
CALL AssocWenssSources2CatByZones(18);
EOF

echo -e "-----"
echo -e "READY"
echo -e "-----"

