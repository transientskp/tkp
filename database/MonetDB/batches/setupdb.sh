#!/usr/bin/env bash


# Configurables
###############

BATCH_FILE="sql_files"
MONETDB_DATABASE="trap"
MONETDB_USERNAME="trap"
MONETDB_PASSWORD="trap"
MONETDB_RECREATE=true
#MONETDB_PORT="50000"
#MONETDB_HOST="localhost"
#MONETDB_PARAMS="-h${MONETDB_HOST} -p${MONETDB_PORT}"


# Non-configurable variables
############################

WHEREAMI="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
WHATAMI="$0"
SQLFILES=${WHEREAMI}/..


# Here you can specify what string in a SQL file to replace with what
# replace_string["%TOKEN%"] = "what to replace it with"
#######################################################

declare -A tokens
tokens["%NODE%"]=1
tokens["%NODES%"]=10
tokens["%NVSS%"]="${WHEREAMI}/../../catfiles/nvss/nvss.csv"
tokens["%VLSS%"]="/${WHEREAMI}/../../catfiles/vlss/vlss.csv"
tokens["%WENSS%"]="${WHEREAMI}/../../catfiles/wenss/wenss.csv"


# Functions
###########

message() {
    echo "*** ${WHATAMI}: $1"
}

error_message() {
    echo "*** ${WHATAMI}: ERROR: $1" >&2
}

fail_check() {
    if [ ! $? -eq 0 ]; then
        error_message "$1"
        exit 1
    fi
}

run() {
    message "running ${1}"
    eval ${1}
    fail_check "running ${1} failed"
}

run_nostop() {
    message "running ${1}"
    eval ${1}
}

destroy_database() {
    message "destroying old database"
	run_nostop "monetdb ${MONETDB_PARAMS} stop ${MONETDB_DATABASE}"
	run_nostop "monetdb ${MONETDB_PARAMS} destroy -f ${MONETDB_DATABASE}"
}

create_database() {
    message "creating database ${MONETDB_DATABASE}"
	run "monetdb ${MONETDB_PARAMS} create ${MONETDB_DATABASE}"
	run "monetdb ${MONETDB_PARAMS} start ${MONETDB_DATABASE}"
}

set_credentials() {
    message "setting credentials"
   mclient -d${MONETDB_DATABASE} <<-EOF
ALTER USER "monetdb" RENAME TO "${MONETDB_USERNAME}";
ALTER USER SET PASSWORD '${MONETDB_PASSWORD}' USING OLD PASSWORD 'monetdb';
CREATE SCHEMA "${MONETDB_DATABASE}" AUTHORIZATION "${MONETDB_USERNAME}";
ALTER USER "${MONETDB_USERNAME}" SET SCHEMA "${MONETDB_DATABASE}";
EOF
}

restore_monetconffile() {
    message "restoring monetdb config file ~/.monetdb"
    mv ~/.monetdb.old ~/.monetdb
}

# the real code
###############

#echo "WHEREAMI=${WHEREAMI}"
#echo "WHATAMI=${WHATAMI}"
#echo "SQLFILES=${SQLFILES}"

if ${MONETDB_RECREATE}; then
	message "(re)creating database ${MONETDB_DATABASE}"
	destroy_database
	create_database

    message "creating backup of monetdb config file to ~/.monetdb.old"
    mv ~/.monetdb ~/.monetdb.old
    message "creating temporary monetdb config file"
    cat > ~/.monetdb <<-EOF
user=monetdb
password=monetdb
EOF

    set_credentials

    message "creating backup of monetdb config file to ~/.monetdb.old"
    mv ~/.monetdb ~/.monetdb.old
    message "creating temporary monetdb config file"
    cat > ~/.monetdb <<-EOF
user=${MONETDB_USERNAME}
password=${MONETDB_PASSWORD}
EOF


    # always run this on exit
    trap restore_monetconffile EXIT
fi

for sql_file in $(cat ${WHEREAMI}/${BATCH_FILE} | grep -v ^#); do
	# replace tokens in sql files
	sql=`cat ${SQLFILES}/${sql_file}`
    for token in ${!tokens[*]}; do
		sql="${sql//${token}/${tokens[${token}]}}"
	done	

	# and then run it it
	message "processing ${sql_file}"
	echo "${sql}" | mclient -d${MONETDB_DATABASE}
	fail_check "failed to load SQL:

${sql}"
done 


