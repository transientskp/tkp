#!/usr/bin/env bash

# Configurables
###############

DESTROY=true
CONFIRM=true
DATABASE=trap
BATCH="sql/batch"
USERNAME=${DATABASE}
PASSWORD=${DATABASE}
HOSTNAME=localhost
PORT=50000

# Non-configurable variables
############################

WHEREAMI="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
WHATAMI="$0"
SQLFILES=${WHEREAMI}/sql
VLSS=${WHEREAMI}/catalog/vlss/vlss.csv
WENSS=${WHEREAMI}/catalog/wenss/wenss.csv
NVSS=${WHEREAMI}/catalog/nvss/nvss.csv
EXO=${WHEREAMI}/catalog/exoplanets/exo.csv


# Here you can specify what string in a SQL file to replace with what
# replace_string["%TOKEN%"] = "what to replace it with"
#######################################################

declare -A tokens
tokens["%NODE%"]=1
tokens["%NODES%"]=1
tokens["%VLSS%"]=${VLSS}
tokens["%WENSS%"]=${WENSS}
tokens["%NVSS%"]=${NVSS}
tokens["%EXO%"]=${EXO}


# Functions
###########

usage() {
cat << EOF
usage: $0 options

This script will populate the TKP database

OPTIONS:
   -h      Show this message
   -r      Don't destroy database before population
   -y      Don't prompt for comfirmation
   -d      Database name to use
   -u      Set database username to this value
   -p      Set database password to this value
   -H      Database hostname
   -P      Database port
   -b      Set batch file to use
EOF
}

parse_arguments() {
	while getopts “hryd:u:p:H:P:b:” OPTION
	do
		 case $OPTION in
			 h)
				 usage
				 exit 1
				 ;;
			 r)
				 DESTROY=false
				 ;;
			 y)
				 CONFIRM=false
				 ;;
			 d)
				 DATABASE=${OPTARG}
				 USERNAME=${OPTARG}
				 PASSWORD=${OPTARG}
				 ;;
			 u)
				 USERNAME=${OPTARG}
				 ;;
			 p)
				 PASSWORD=${OPTARG}
				 ;;
			 H)
				 HOSTNAME=${OPTARG}
				 REMOTEHOST=1
				 ;;
			 P)
				 PORT=${OPTARG}
				 ;;
			 b)
				 BATCH=${OPTARG}
                 ;;
			 ?)
				 usage
				 exit
				 ;;
		 esac
	done
}

message() {
    echo -e "*** ${WHATAMI}: $1"
}

error_message() {
    echo -e "*** ${WHATAMI}: ERROR: $1" >&2
}

check_file() {
	message "checking if $1 exists"
	if [ ! -f $1 ]; then
		error_message "$2"
		exit 1
	fi
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
	run_nostop "monetdb ${PARAMS} stop ${DATABASE}"
	run_nostop "monetdb ${PARAMS} destroy -f ${DATABASE}"
}

create_database() {
    message "creating database ${DATABASE}"
	run "monetdb ${PARAMS} create ${DATABASE}"
	run "monetdb ${PARAMS} start ${DATABASE}"
}

set_credentials() {
    message "setting credentials"
    mclient -d${DATABASE} -p${PORT} -h${HOSTNAME} <<-EOF
ALTER USER "monetdb" RENAME TO "${USERNAME}";
ALTER USER SET PASSWORD '${PASSWORD}' USING OLD PASSWORD 'monetdb';
CREATE SCHEMA "${DATABASE}" AUTHORIZATION "${USERNAME}";
ALTER USER "${USERNAME}" SET SCHEMA "${DATABASE}";
EOF
}

restore_monetconffile() {
    message "restoring monetdb config file ~/.monetdb"
    mv ~/.monetdb.old ~/.monetdb
}

lock_database() {
	run_nofail "monetdb ${PARAMS} lock ${DATABASE}"
}


release_database() {
	run "monetdb ${PARAMS} release ${DATABASE}"
}


# the real code
###############

parse_arguments $*

echo
echo "TKP database will be populated with these settings:"
echo
echo " Destroy database: " ${DESTROY}
echo " Database name: " ${DATABASE}
echo " Batch file: " ${BATCH}
echo " username: " ${USERNAME}
echo " Password: " ${PASSWORD}
echo " Hostname: " ${HOSTNAME}
echo " Port: " ${PORT}
echo
echo "use $0 -h to see how to set all options"
echo

if [ ${REMOTEHOST} ]; then
    # Hostname specified on the command line -> we are connecting over TCP
    # Build an appropriate argument list for monetdb
    PARAMS=""
    if [ ${HOSTNAME} ]; then
        PARAMS+=" -h ${HOSTNAME}"
    fi
    if [ ${PORT} ]; then
        PARAMS+=" -p ${PORT}"
    fi
    if [ ${PASSWORD} ] ; then
        PARAMS+=" -P ${PASSWORD}"
    fi
fi

if "${CONFIRM}"; then
    echo 
    echo "WARNING: this will (re)create the database ${DATABASE}."
    read -p "Continue? [y/N]" -n 1
    if [[ ! $REPLY =~ ^[Yy]$ ]]
    then
        echo
        exit 1
    fi
fi

for i in ${NVSS} ${VLSS} ${WENSS}; do
	check_file $i "please download a catalog or symlink something to $i"
done

if ${DESTROY}; then
	message "Destroying database ${DATABASE}"
	destroy_database
	message "Creating database ${DATABASE}"
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
user=${USERNAME}
password=${PASSWORD}
EOF

    # always run this on exit
    trap restore_monetconffile EXIT
else
    lock_database
fi

for sql_file in $(cat ${WHEREAMI}/${BATCH} | grep -v ^#); do
	# replace tokens in sql files
	sql=`cat ${SQLFILES}/${sql_file}`
    for token in ${!tokens[*]}; do
		sql="${sql//${token}/${tokens[${token}]}}"
	done	

	# and then run it it
	message "processing ${sql_file}"
	echo "${sql}" | mclient -d${DATABASE} -p${PORT} -h${HOSTNAME}
	fail_check "failed to load SQL: ${sql}"
done 

release_database

