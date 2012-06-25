#!/usr/bin/env bash


# Configurables
###############

BATCH_FILE="sql_files"
MONETDB_DATABASE="trap"
MONETDB_USERNAME="trap"
MONETDB_PASSWORD="trap"
MONETDB_RECREATE=true
#MONETDB_PORT="5000"
#MONETDB_HOST="localhost"
#MONETDB_PARAMS="-h${MONETDB_HOST} -p${MONETDB_PORT}"


# Here you can specify what string in a SQL file to replace with what
# replace_string["%TOKEN%"] = "what to replace it with"
#######################################################

declare -A tokens
tokens["%NODE%"]=1
tokens["%NODES%"]=10
tokens["%NVSS%"]="/scratch/catfiles/NVSS-all_strip.csv"
tokens["%VLSS%"]="/scratch/catfiles/VLSS-all_strip.csv"
tokens["%WENSS%"]="/scratch/catfiles/WENSS-all_strip.csv"


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
   mclient -h$host -p$port -d$dbname <<-EOF
ALTER USER "monetdb" RENAME TO "${adminuser}";
ALTER USER SET PASSWORD '${adminpassword}' USING OLD PASSWORD 'monetdb';
CREATE SCHEMA "${dbname}" AUTHORIZATION "${adminuser}";
ALTER USER "${adminuser}" SET SCHEMA "${dbname}";
EOF
}


# the real code
###############

if ${MONETDB_RECREATE}; then
	message "(re)creating database ${MONETDB_DATABASE}"
	destroy_database
	create_database
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

