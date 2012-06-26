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


# Here you can specify what string in a SQL file to replace with what
# replace_string["%TOKEN%"] = "what to replace it with"
#######################################################

declare -A tokens
tokens["%NODE%"]=1
tokens["%NODES%"]=10
tokens["%NVSS%"]="/home/bscheers/catfiles/nvss/NVSS-all_strip.csv"
tokens["%VLSS%"]="/home/bscheers/catfiles/vlss//VLSS-all_strip.csv"
tokens["%WENSS%"]="/home/bscheers/catfiles/wenss/WENSS-all_strip.csv"


# Non-configurable variables
############################

WHEREAMI="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
WHATAMI="$0"
SQLFILES=${WHEREAMI}/..


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
	run_nostop "monetdb ${MONETDB_PARAMS} stop ${MONETDB_DATABASE}"
	run_nostop "monetdb ${MONETDB_PARAMS} destroy -f ${MONETDB_DATABASE}"
}

create_database() {
	run "monetdb ${MONETDB_PARAMS} create ${MONETDB_DATABASE}"
	run "monetdb ${MONETDB_PARAMS} start ${MONETDB_DATABASE}"
}

set_credentials() {
   mclient -d${MONETDB_DATABASE} <<-EOF
ALTER USER "monetdb" RENAME TO "${MONETDB_USERNAME}";
ALTER USER SET PASSWORD '${MONETDB_PASSWORD}' USING OLD PASSWORD 'monetdb';
CREATE SCHEMA "${MONETDB_DATABASE}" AUTHORIZATION "${MONETDB_USERNAME}";
ALTER USER "${MONETDB_USERNAME}" SET SCHEMA "${MONETDB_DATABASE}";
EOF

    DOTMONETDBFILE=.${MONETDB_DATABASE}
    cat > $DOTMONETDBFILE <<EOF
user=${MONETDB_USERNAME}
password=${MONETDB_PASSWORD}
EOF
}

rm_dotmonetdbfile() {
    rm $DOTMONETDBFILE
}

# the real code
###############

if ${MONETDB_RECREATE}; then
	message "(re)creating database ${MONETDB_DATABASE}"
	destroy_database
	create_database
    set_credentials
fi

for sql_file in $(cat ${BATCH_FILE} | grep -v ^#); do
	# replace tokens in sql files
	sql=`cat ${SQLFILES}/${sql_file}`
	for token in ${!tokens[*]}; do
		sql="${sql//${token}/${tokens[${token}]}}"
	done	

	# and then run it it
	message "processing ${sql_file}"
	echo "${sql}" | mclient -d${MONETDB_DATABASE}
	fail_check "failed to load SQL:\n ${sql}"
done 

if ${MONETDB_RECREATE}; then
    rm_dotmonetdbfile
fi

