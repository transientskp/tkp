#!/bin/bash

# assume:
# - mclient/monetdb are in path
# - user/pass is monetdb

# script performs:
# - if meroport and meropass are set, (re)create database and initialise
# - scrambling administrator account to something else for sugagurity
# - create voc user/schema
# - load voc dataset
# - create webdemo user with password webdemo in schema webdemo
# - create views for tables from voc set in webdemo schema

# arguments:
# $1: host
# $2: database
# $3 (optional): new user
# $4 (optional): new password

# An example call of this script could be:
# %> ./setup.db.batch host port database meroport meropass useradminname adminpassword
# %> ./setup.db.batch localhost 50000 pipeline_develop 50001 xxxxxxxxxxxxxxxxxxxxxxxxx lofar xxx
# %> ./setup.db.batch localhost 50000 pipeline_develop 50001 xxxxxxxxxxxxxxxxxxxxxxxxx lofar xxx
# to create database on host, which can be controlled over port
# 50001 using control passphrase $#$#.  Port 50000 on host is
# used for mclient to connect to the database database and populate it.
# You better make sure you save the output of this script (or remember your command)
# as it resets the username and password of the admin user (which by default is
# monetdb/monetdb).

PGPATH=/usr/lib/postgresql/8.4/bin

if [ -z "$*" ]
then
    echo "Usage:"
    echo "$0 [options]  db-host  database-name  [ username ]  [ password ]"
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

HOST=$1
NAME=$2
USER=$3
ADMIN="postgres"
if [ -n "$create_database" ]
# Need to create a new database
then
    echo "(re)creating ${2} at ${1}"
    #monetdb -h$1 -p$4 -P$5 stop ${2}
    ${PGPATH}/dropdb -h $HOST -U $ADMIN  $NAME
    ${PGPATH}/createdb -h $HOST -U $ADMIN -O $USER $NAME || exit 1
    ${PGPATH}/createlang -h $HOST -U $USER -d $NAME plpgsql 
fi

if [ -z "$DATABASETKPHOME" ]
# user didn't define a 'home' (base) directory; make a good guess
then
    DATABASETKPHOME=`dirname $0`/..
fi


echo -e "\t----------------------------------------"
echo -e "\tCreating ${2} tables"
echo -e "\t----------------------------------------"

echo -e "\t\tCreating ${NAME} table versions"
psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/tables/create.table.versions.sql

echo -e "\t\tCreating ${NAME} table frequencybands"
psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/tables/create.table.frequencybands.sql

echo -e "\t\tCreating ${NAME} table datasets"
psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/tables/create.table.datasets.sql

echo -e "\t\tCreating ${NAME} table images"
psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/tables/create.table.images.sql

#echo -e "\t\tCreating ${NAME} table associationclass"
#psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/tables/create.table.associationclass.sql

echo -e "\t\tCreating ${NAME} table catalogs"
psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/tables/create.table.catalogs.sql

echo -e "\t\tCreating ${NAME} table catalogedsources"
psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/tables/create.table.catalogedsources.sql

echo -e "\t\tCreating ${NAME} table extractedsources"
psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/tables/create.table.extractedsources.sql

#echo -e "\t\tCreating ${NAME} table loadxtrsources"
#psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/tables/create.table.loadxtrsources.sql

#echo -e "\t\tCreating ${NAME} table basesources"
#psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/tables/create.table.basesources.sql

#echo -e "\t\tCreating ${NAME} table tempbasesources"
#psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/tables/create.table.tempbasesources.sql

echo -e "\t\tCreating ${NAME} table assoccatsources"
psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/tables/create.table.assoccatsources.sql

echo -e "\t\tCreating ${NAME} table assocxtrsources"
psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/tables/create.table.assocxtrsources.sql

#echo -e "\t\tCreating ${NAME} table aux_assocs"
#psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/tables/create.table.aux_assocs.sql

echo -e "\t\tCreating ${NAME} table lsm"
psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/tables/create.table.lsm.sql

echo -e "\t\tCreating ${NAME} table spectralindices"
psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/tables/create.table.spectralindices.sql

echo -e "\t\tCreating ${NAME} table runningcatalog"
psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/tables/create.table.runningcatalog.sql

echo -e "\t\tCreating ${NAME} table temprunningcatalog"
psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/tables/create.table.temprunningcatalog.sql

echo -e "\t\tCreating ${NAME} table detections"
psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/tables/create.table.detections.sql


#echo -e "\t\tCreating ${NAME} table zoneheight"
#psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/tables/create.table.zoneheight.sql

#echo -e "\t\tCreating ${NAME} table zones"
#psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/tables/create.table.zones.sql

#echo -e "\t\tCreating ${NAME} Query History"
#psql  -h ${HOST} -d ${NAME} -U ${USER}  < ${DATABASEHOME}/share/MonetDB/sql/history.sql

#echo -e "\t-------------------------------------------------------------------------"
#echo -e "\tCreating ${NAME} tables for multiple catalog association"
#echo -e "\t-------------------------------------------------------------------------"

#echo -e "\t\tCreating ${NAME} table multiplecatalogsources"
#psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/tables/create.table.multiplecatalogsources.sql

#echo -e "\t\tCreating ${NAME} table multiplecatalogassocs"
#psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/tables/create.table.multiplecatalogassocs.sql

## -----------------------------------------------------
## Tables to store detected transients & classifications
## -----------------------------------------------------

echo -e "\t\tCreating ${NAME} table transients"
psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/tables/create.table.transients.sql

echo -e "\t\tCreating ${NAME} table classification"
psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/tables/create.table.classification.sql



echo -e "\t-------------------------------------------"
echo -e "\tCreating ${NAME} functions"
echo -e "\t-------------------------------------------"

# These functions are embedded in the sys db ;)
#echo -e "\t\tCreating ${NAME} math functions"
#psql  -h ${HOST} -d ${NAME} -U ${USER}  < ${DATABASEHOME}/lib/MonetDB5/math.sql

#echo -e "\t\tCreating ${NAME} date functions"
#psql  -h ${HOST} -d ${NAME} -U ${USER}  < ${DATABASEHOME}/lib/MonetDB5/date.sql

#echo -e "\t\tCreating ${NAME} times functions"
#psql  -h ${HOST} -d ${NAME} -U ${USER}  < ${DATABASEHOME}/lib/MonetDB5/times.sql

#echo -e "\t\tCreating ${NAME} mtime functions"
#psql  -h ${HOST} -d ${NAME} -U ${USER}  < /scratch/bscheers/databases/MonetDB/share/MonetDB/sql/mtime.sql

echo -e "\t\tCreating ${NAME} function deg"
psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/functions/create.function.deg.sql

echo -e "\t\tCreating ${NAME} function rad"
psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/functions/create.function.rad.sql

echo -e "\t\tCreating ${NAME} function alpha"
psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/functions/create.function.alpha.sql

#echo -e "\t\tCreating ${NAME} function getVectorLength"
#psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/functions/create.function.getVectorLength.sql

echo -e "\t\tCreating ${NAME} function getDistanceArcsec"
psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/functions/create.function.getDistanceArcsec.sql

echo -e "\t\tCreating ${NAME} function getDistanceXSource2CatArcsec"
psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/functions/create.function.getDistanceXSource2CatArcsec.sql

echo -e "\t\tCreating ${NAME} function getDistanceXSourcesArcsec"
psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/functions/create.function.getDistanceXSourcesArcsec.sql

echo -e "\t\tCreating ${NAME} function solidangle_arcsec2"
psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/functions/create.function.solidangle_arcsec2.sql

#echo -e "\t\tCreating ${NAME} function getWeightRectIntersection"
#psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/functions/create.function.getWeightRectIntersection.sql

#echo -e "\t\tCreating ${NAME} function doSourcesIntersect"
#psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/functions/create.function.doSourcesIntersect.sql

#echo -e "\t\tCreating ${NAME} function doPosErrCirclesIntersect"
#psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/functions/create.function.doPosErrCirclesIntersect.sql

echo -e "\t\tCreating ${NAME} function nearestNeighborInCat"
psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/functions/create.function.nearestNeighborInCat.sql

echo -e "\t\tCreating ${NAME} function getNeighborsinCat"
psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/functions/create.function.getNeighborsInCat.sql

echo -e "\t\tCreating ${NAME} function getNearestNeighborInCat"
psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/functions/create.function.getNearestNeighborInCat.sql

echo -e "\t\tCreating ${NAME} function getNearestNeighborInImage"
psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/functions/create.function.getNearestNeighborInImage.sql

echo -e "\t\tCreating ${NAME} function getBand"
psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/functions/create.function.getBand.sql

echo -e "\t\tCreating ${NAME} function decl2deg"
psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/functions/create.function.decl2deg.sql

echo -e "\t\tCreating ${NAME} function decl2dms"
psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/functions/create.function.decl2dms.sql

echo -e "\t\tCreating ${NAME} function decl2bbsdms"
psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/functions/create.function.decl2bbsdms.sql

echo -e "\t\tCreating ${NAME} function insertDataset"
psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/functions/create.function.insertDataset.sql

echo -e "\t\tCreating ${NAME} function insertImage"
psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/functions/create.function.insertImage.sql

#echo -e "\t\tCreating ${NAME} function selectAssocs"
#psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/functions/create.function.selectAssocs.sql

echo -e "\t\tCreating ${NAME} function ra2deg"
psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/functions/create.function.ra2deg.sql

echo -e "\t\tCreating ${NAME} function ra2hms"
psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/functions/create.function.ra2hms.sql

echo -e "\t\tCreating ${NAME} function ra2bbshms"
psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/functions/create.function.ra2bbshms.sql

echo -e "\t\tCreating ${NAME} function getSkyDensity_sr"
psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/functions/create.function.getSkyDensity_sr.sql

echo -e "\t\tCreating ${NAME} function getHuynhSkyDensity_deg2"
psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/functions/create.function.getHuynhSkyDensity_deg2.sql

echo -e "\t\tCreating ${NAME} function localSourceDensityInCat_deg2"
psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/functions/create.function.localSourceDensityInCat_deg2.sql


echo -e "\t----------------------------------------------------"
echo -e "\tCreating ${NAME} general procedures"
echo -e "\t----------------------------------------------------"

#echo -e "\t\tCreating ${NAME} general procedure AssocXSources2XSourcesByImage"
#psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/procedures/create.procedure.AssocXSources2XSourcesByImage.sql

#echo -e "\t\tCreating ${NAME} general procedure AssocXSources2CatByImage"
#psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/procedures/create.procedure.AssocXSources2CatByImage.sql

#echo -e "\t\tCreating ${NAME} general procedure AssocXSources2CatByZones"
#psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/procedures/create.procedure.AssocXSources2CatByZones.sql

#echo -e "\t\tCreating ${NAME} general procedure AssocXSrc2XSrc"
#psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/procedures/create.procedure.AssocXSrc2XSrc.sql

#echo -e "\t\tCreating ${NAME} general procedure AssocXSrc2XCat"
#psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/procedures/create.procedure.AssocXSrc2Cat.sql

#echo -e "\t\tCreating ${NAME} general procedure AssocWenssSources2Cat"
#psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/procedures/create.procedure.AssocWenssSources2Cat.sql

#echo -e "\t\tCreating ${NAME} general procedure AssocWenssSources2CatByZones"
#psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/procedures/create.procedure.AssocWenssSources2CatByZones.sql

#echo -e "\t\tCreating ${NAME} general procedure AssocWenssSources2CatByImage"
#psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/procedures/create.procedure.AssocWenssSources2CatByImage.sql

#echo -e "\t\tCreating ${NAME} general procedure BuildAssociationClass"
#psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/procedures/create.procedure.BuildAssociationClass.sql

echo -e "\t\tCreating ${NAME} general procedure BuildFrequencyBands"
psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/procedures/create.procedure.BuildFrequencyBands.sql

#echo -e "\t\tCreating ${NAME} general procedure BuildZones"
#psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/procedures/create.procedure.BuildZones.sql

echo -e "\t\tCreating ${NAME} general procedure InsertVersion"
psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/procedures/create.procedure.InsertVersion.sql

#echo -e "\t\tCreating ${NAME} general procedure InsertSrc"
#psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/procedures/create.procedure.InsertSrc.sql

echo -e "\t\tCreating ${NAME} general procedure LoadLSM"
psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/procedures/create.procedure.LoadLSM.sql

#echo -e "\t\tCreating ${NAME} general procedure LoadWenssSourceAndBGFields"
#psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/procedures/create.procedure.LoadWenssSourceAndBGFields.sql


#echo -e "\t-----------------------------------------------------------------------------"
#echo -e "\tCreating ${NAME} procedures for multiple catalog association"
#echo -e "\t-----------------------------------------------------------------------------"

#echo -e "\t\tCreating ${NAME} specific procedure MultipleCatMatchingInit"
#psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/procedures/create.procedure.MultipleCatMatchingInit.sql

#echo -e "\t\tCreating ${NAME} specific procedure MultipleCatMatching"
#psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/procedures/create.procedure.MultipleCatMatching.sql


echo -e "\t-----------------------------------"
echo -e "\tInitialize MonetDB ${NAME}"
echo -e "\t-----------------------------------"

echo -e "\t\tInitialize MonetDB ${NAME} tables"
psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/init/init.tables.sql


echo -e "\t----------------------------------------------"
echo -e "\tLoading catalogs into MonetDB ${NAME}"
echo -e "\t----------------------------------------------"

#date '+%Y-%m-%d-%H:%M:%S'

#echo -e "\t\tLoad catalogs"
#psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/load/copy.catalogs.sql
#echo -e "\t\tLoad catalogedsources"
#psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/load/copy.catalogedsources.sql

echo -e "\t\tLoad NVSS catalog"
time psql -h ${HOST} -d ${NAME} -U ${ADMIN}  < $DATABASETKPHOME/load/load.cat.nvss.sql

echo -e "\t\tLoad VLSS catalog"
time psql -h ${HOST} -d ${NAME} -U ${ADMIN}  < $DATABASETKPHOME/load/load.cat.vlss.sql

echo -e "\t\tLoad WENSS catalog"
time psql -h ${HOST} -d ${NAME} -U ${ADMIN}  < $DATABASETKPHOME/load/load.cat.wenss.sql

#echo -e "\t\tLoad GRB catalog"
#psql -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/load/load.cat.grb.sql
#date '+%Y-%m-%d-%H:%M:%S'

#echo -e "\t\tLoad SIMDATA catalog"
#psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/load/load.cat.simdata.sql
#date '+%Y-%m-%d-%H:%M:%S'

#echo -e "\t\tLoad 2XMMi-Slim catalog"
#psql  -h ${HOST} -d ${NAME} -U ${USER}  < $DATABASETKPHOME/load/load.cat.2XMMi-slim.sql
#date '+%Y-%m-%d-%H:%M:%S'


echo -e "-----"
echo -e "READY"
echo -e "-----"
