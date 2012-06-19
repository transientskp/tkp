#!/bin/bash

###############################################################################
# The assumption here is that the monetdbd deamon program is running, so that #
# databases can be created.                                                   #
# And furthermore that mclient & monetdb are in the path, and the user/passw  #
# is monetdb.                                                                 #
###############################################################################


###############################################################################
# arguments:                                                                  #
# $1: host                                                                    #
# $2: database                                                                #
# $3 (optional) new user                                                      #
# $4 (optional): new password                                                 #
# $5 (optional): port                                                         #
###############################################################################

###############################################################################
# An example call of this script could be:                                    #
# %> ./setup.db.batch localhost test1 test1 test1 50000                       #
###############################################################################

if [ -z "$*" ]
then
    echo "Usage:"
    echo "$0 [options]  db-host  database-name  [ username ] [ password ] [ port ]"
    echo "Options: --no-create-database: do not create a database"
    exit ;
fi

create_database=1
# parse through options
while true
do
    case "$1" in
        --no-create-database) 
            unset create_database
            shift 1
            ;;
        --) 
	    # end of all options
            shift
            break
            ;;
        *)
            break
            ;;
    esac
done

# Set up defaults
host=$1
dbname=$2
if [ -z "$3" ]
then
    username=$dbname
else
    username=$3
fi
if [ -z "$4" ]
then
    password=$dbname
else
    password=$4
fi
if [ -z "$5" ]
then
    port=50000
else
    port=$5
fi

monetdb_login=""
if [ -f ${HOME}/.meropass ]
then
    monetdb_login="-h$host -p$port -P"`cat ${HOME}/.meropass`
fi

echo "monetdb_login: $monetdb_login"

if [ -n "$create_database" ]
# Need to create a new database
then
    echo "(re)creating $dbname at $host"
    monetdb $monetdb_login stop $dbname 
    monetdb $monetdb_login destroy -f $dbname
    monetdb $monetdb_login create $dbname 
    monetdb $monetdb_login start $dbname 
    echo "Created $dbname at $host"
    
    adminuser=$username
    adminpassword=$password
    
    # Is this block necessary ? 
    DEFAULTDOTFILE=.monetdb
    #if [ -z "$MONETDBHOME" ]
    #then
    #    MONETDBHOME=$HOME
    #fi
    #DOTMONETDBFILE=$MONETDBHOME/$DEFAULTDOTFILE
    DOTMONETDBFILE=$HOME/$DEFAULTDOTFILE
    #export DOTMONETDBFILE
    
    # set up a default .monetdb file, with default pass
    cat > $DOTMONETDBFILE <<EOF
user=monetdb
password=monetdb
EOF
    
    echo "changing monetdb/monetdb user/password into:"
    echo "user: ${adminuser}"
    echo "password: ${adminpassword}"
    mclient -h$host -p$port -d$dbname <<-EOF
ALTER USER "monetdb" RENAME TO "${adminuser}";
ALTER USER SET PASSWORD '${adminpassword}' USING OLD PASSWORD 'monetdb';
CREATE SCHEMA "${dbname}" AUTHORIZATION "${adminuser}";
ALTER USER "${adminuser}" SET SCHEMA "${dbname}";
EOF
    
    # Here we set the DOTMONETDBFILE to the current dbname
    #DOTMONETDBFILE=$MONETDBHOME/.${dbname}
    DOTMONETDBFILE=$HOME/.${dbname}
    cat > $DOTMONETDBFILE <<EOF
user=${adminuser}
password=${adminpassword}
EOF
    
    chmod go-rwx $DOTMONETDBFILE
else
    monetdb $monetdb_login lock ${dbname}
fi
export DOTMONETDBFILE

MONETDBTKPHOME=`dirname $0`/..
echo "Fetch sql sources from ${MONETDBTKPHOME}"

echo -e "\t----------------------------------------"
echo -e "\tCreating MonetDB ${dbname} tables"
echo -e "\t----------------------------------------"

echo -e "\t\tCreating MonetDB ${dbname} table versions"
mclient -p$port -h$host -d${dbname} < $MONETDBTKPHOME/tables/create.table.versions.sql || exit 1

echo -e "\t\tCreating MonetDB ${dbname} table frequencybands"
mclient -p$port -h$host -d${dbname} < $MONETDBTKPHOME/tables/create.table.frequencybands.sql || exit 1

echo -e "\t\tCreating MonetDB ${dbname} table datasets"
mclient -p$port -h$host -d${dbname} < $MONETDBTKPHOME/tables/create.table.datasets.sql || exit 1

echo -e "\t\tCreating MonetDB ${dbname} table images"
mclient -p$port -h$host -d${dbname} < $MONETDBTKPHOME/tables/create.table.images.sql || exit 1

echo -e "\t\tCreating MonetDB ${dbname} table catalogs"
mclient -p$port -h$host -d${dbname} < $MONETDBTKPHOME/tables/create.table.catalogs.sql || exit 1

echo -e "\t\tCreating MonetDB ${dbname} table catalogedsources"
mclient -p$port -h$host -d${dbname} < $MONETDBTKPHOME/tables/create.table.catalogedsources.sql || exit 1

echo -e "\t\tCreating MonetDB ${dbname} table extractedsources"
bash $MONETDBTKPHOME/tables/create.table.extractedsources.sh $host $dbname $port 1 1 || exit 1

echo -e "\t\tCreating MonetDB ${dbname} table assoccatsources"
mclient -p$port -h$host -d${dbname} < $MONETDBTKPHOME/tables/create.table.assoccatsources.sql || exit 1

echo -e "\t\tCreating MonetDB ${dbname} table assocxtrsources"
mclient -p$port -h$host -d${dbname} < $MONETDBTKPHOME/tables/create.table.assocxtrsources.sql || exit 1

echo -e "\t\tCreating MonetDB ${dbname} table runningcatalog"
mclient -p$port -h$host -d${dbname} < $MONETDBTKPHOME/tables/create.table.runningcatalog.sql || exit 1

echo -e "\t\tCreating MonetDB ${dbname} table temprunningcatalog"
mclient -p$port -h$host -d${dbname} < $MONETDBTKPHOME/tables/create.table.temprunningcatalog.sql || exit 1

echo -e "\t\tCreating MonetDB ${dbname} table detections"
mclient -p$port -h$host -d${dbname} < $MONETDBTKPHOME/tables/create.table.detections.sql || exit 1

echo -e "\t----------------------------------------------------------------------------"
echo -e "\tCreating MonetDB ${dbname} tables to store detected transients & classifications "
echo -e "\t----------------------------------------------------------------------------"

echo -e "\t\tCreating MonetDB ${dbname} table monitoringlist"
mclient -p$port -h$host -d${dbname} < $MONETDBTKPHOME/tables/create.table.monitoringlist.sql || exit 1

echo -e "\t\tCreating MonetDB ${dbname} table transients"
mclient -p$port -h$host -d${dbname} < $MONETDBTKPHOME/tables/create.table.transients.sql || exit 1

echo -e "\t\tCreating MonetDB ${dbname} table classification"
mclient -p$port -h$host -d${dbname} < $MONETDBTKPHOME/tables/create.table.classification.sql || exit 1

echo -e "\t-------------------------------------------"
echo -e "\tCreating MonetDB ${dbname} functions"
echo -e "\t-------------------------------------------"

# These functions are also mbedded in the sys schema
echo -e "\t\tCreating MonetDB ${dbname} math functions"
mclient -p$port -h$host -d${dbname} < $MONETDBTKPHOME/functions/monetdb_10_math.sql || exit 1

echo -e "\t\tCreating MonetDB ${dbname} function alpha"
mclient -p$port -h$host -d${dbname} < $MONETDBTKPHOME/functions/create.function.alpha.sql || exit 1

echo -e "\t\tCreating MonetDB ${dbname} function getDistanceArcsec"
mclient -p$port -h$host -d${dbname} < $MONETDBTKPHOME/functions/create.function.getDistanceArcsec.sql || exit 1

echo -e "\t\tCreating MonetDB ${dbname} function getDistanceXSource2CatArcsec"
mclient -p$port -h$host -d${dbname} < $MONETDBTKPHOME/functions/create.function.getDistanceXSource2CatArcsec.sql || exit 1

echo -e "\t\tCreating MonetDB ${dbname} function getDistanceXSourcesArcsec"
mclient -p$port -h$host -d${dbname} < $MONETDBTKPHOME/functions/create.function.getDistanceXSourcesArcsec.sql || exit 1

echo -e "\t\tCreating MonetDB ${dbname} function solidangle_arcsec2"
mclient -p$port -h$host -d${dbname} < $MONETDBTKPHOME/functions/create.function.solidangle_arcsec2.sql || exit 1

echo -e "\t\tCreating MonetDB ${dbname} function nearestNeighborInCat"
mclient -p$port -h$host -d${dbname} < $MONETDBTKPHOME/functions/create.function.nearestNeighborInCat.sql || exit 1

echo -e "\t\tCreating MonetDB ${dbname} function getNeighborsinCat"
mclient -p$port -h$host -d${dbname} < $MONETDBTKPHOME/functions/create.function.getNeighborsInCat.sql || exit 1

echo -e "\t\tCreating MonetDB ${dbname} function getNearestNeighborInCat"
mclient -p$port -h$host -d${dbname} < $MONETDBTKPHOME/functions/create.function.getNearestNeighborInCat.sql || exit 1

echo -e "\t\tCreating MonetDB ${dbname} function getNearestNeighborInImage"
mclient -p$port -h$host -d${dbname} < $MONETDBTKPHOME/functions/create.function.getNearestNeighborInImage.sql || exit 1

echo -e "\t\tCreating MonetDB ${dbname} function getBand"
mclient -p$port -h$host -d${dbname} < $MONETDBTKPHOME/functions/create.function.getBand.sql || exit 1

echo -e "\t\tCreating MonetDB ${dbname} function decl2deg"
mclient -p$port -h$host -d${dbname} < $MONETDBTKPHOME/functions/create.function.decl2deg.sql || exit 1

echo -e "\t\tCreating MonetDB ${dbname} function decl2dms"
mclient -p$port -h$host -d${dbname} < $MONETDBTKPHOME/functions/create.function.decl2dms.sql || exit 1

echo -e "\t\tCreating MonetDB ${dbname} function insertDataset"
mclient -p$port -h$host -d${dbname} < $MONETDBTKPHOME/functions/create.function.insertDataset.sql || exit 1

echo -e "\t\tCreating MonetDB ${dbname} function insertImage"
mclient -p$port -h$host -d${dbname} < $MONETDBTKPHOME/functions/create.function.insertImage.sql || exit 1

echo -e "\t\tCreating MonetDB ${dbname} function getAssocParams"
mclient -p$port -h$host -d${dbname} < $MONETDBTKPHOME/functions/create.function.getAssocParams.sql || exit 1

echo -e "\t\tCreating MonetDB ${dbname} function getAssocParamsByPos"
mclient -p$port -h$host -d${dbname} < $MONETDBTKPHOME/functions/create.function.getAssocParamsByPos.sql || exit 1

echo -e "\t\tCreating MonetDB ${dbname} function ra2deg"
mclient -p$port -h$host -d${dbname} < $MONETDBTKPHOME/functions/create.function.ra2deg.sql || exit 1

echo -e "\t\tCreating MonetDB ${dbname} function ra2hms"
mclient -p$port -h$host -d${dbname} < $MONETDBTKPHOME/functions/create.function.ra2hms.sql || exit 1

echo -e "\t\tCreating MonetDB ${dbname} function getSkyDensity_deg2"
mclient -p$port -h$host -d${dbname} < $MONETDBTKPHOME/functions/create.function.getSkyDensity_sr.sql || exit 1

echo -e "\t\tCreating MonetDB ${dbname} function getHuynhSkyDensity_deg2"
mclient -p$port -h$host -d${dbname} < $MONETDBTKPHOME/functions/create.function.getHuynhSkyDensity_deg2.sql || exit 1

echo -e "\t\tCreating MonetDB ${dbname} function localSourceDensityInCat_deg2"
mclient -p$port -h$host -d${dbname} < $MONETDBTKPHOME/functions/create.function.localSourceDensityInCat_deg2.sql || exit 1

echo -e "\t\tCreating MonetDB ${dbname} function neighborsInCatsParams"
mclient -p$port -h$host -d${dbname} < $MONETDBTKPHOME/functions/create.function.neighborsInCatsParams.sql || exit 1

echo -e "\t\tCreating MonetDB ${dbname} function neighborsInCats"
mclient -p$port -h$host -d${dbname} < $MONETDBTKPHOME/functions/create.function.neighborsInCats.sql || exit 1


echo -e "\t----------------------------------------------------"
echo -e "\tCreating MonetDB ${dbname} general procedures"
echo -e "\t----------------------------------------------------"

echo -e "\t\tCreating MonetDB ${dbname} general procedure BuildFrequencyBands"
mclient -p$port -h$host -d${dbname} < $MONETDBTKPHOME/procedures/create.procedure.BuildFrequencyBands.sql || exit 1

echo -e "\t\tCreating MonetDB ${dbname} general procedure InsertVersion"
mclient -p$port -h$host -d${dbname} < $MONETDBTKPHOME/procedures/create.procedure.InsertVersion.sql || exit 1 

echo -e "\t-----------------------------------"
echo -e "\tInitialize MonetDB ${dbname}"
echo -e "\t-----------------------------------"

echo -e "\t\tInitialize MonetDB ${dbname} tables"
mclient -p$port -h$host -d${dbname} < $MONETDBTKPHOME/init/init.tables.sql || exit 1

echo -e "\t----------------------------------------------"
echo -e "\tLoading catalogs into MonetDB ${dbname}"
echo -e "\t----------------------------------------------"

echo -e "\t\tLoad NVSS catalog"
time mclient -p$port -h$host -d${dbname} < $MONETDBTKPHOME/load/load.cat.nvss.sql || exit 1

echo -e "\t\tLoad VLSS catalog"
time mclient -p$port -h$host -d${dbname} < $MONETDBTKPHOME/load/load.cat.vlss.sql || exit 1

echo -e "\t\tLoad WENSS catalog"
time mclient -p$port -h$host -d${dbname} < $MONETDBTKPHOME/load/load.cat.wenss.sql || exit 1 

echo -e "\t\tLoad EXOplanets catalog"
time mclient -p$port -h$host -d${dbname} < $MONETDBTKPHOME/load/load.cat.exo.sql || exit 1

#echo -e "\t\tLoad GRB catalog"
#mclient -p$port -lsql -h$host -d${dbname} < $MONETDBTKPHOME/load/load.cat.grb.sql || exit 1
#date '+%Y-%m-%d-%H:%M:%S'

#echo -e "\t\tLoad SIMDATA catalog"
#mclient -p$port -h$host -d${dbname} < $MONETDBTKPHOME/load/load.cat.simdata.sql || exit 1
#date '+%Y-%m-%d-%H:%M:%S'

#echo -e "\t\tLoad 2XMMi-Slim catalog"
#mclient -p$port -h$host -d${dbname} < $MONETDBTKPHOME/load/load.cat.2XMMi-slim.sql || exit 1
#date '+%Y-%m-%d-%H:%M:%S'

echo -e "\t----------------------------"
echo -e "\tRelease MonetDB ${dbname}"
echo -e "\t----------------------------"

if [ -n "$create_database" ]
then
    monetdb $monetdb_login release ${dbname} || exit 1
fi

mclient -p$port -h$host -d${dbname} -s"SELECT * FROM versions;"

echo -e "-----"
echo -e "READY"
echo -e "-----"
