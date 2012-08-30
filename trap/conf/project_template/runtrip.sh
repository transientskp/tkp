#!/bin/bash

BUILD_VER=stable
RECIPE_DIR=/opt/lofar-${BUILD_VER}/symlinks/tkp-root/recipes
USER_CONFIG_REPO=$(dirname $(readlink -f $BASH_SOURCE))

source /opt/soft/reset-paths.sh 
source /opt/lofar-${BUILD_VER}/init-lofar.sh

rm -f statefile

PYTHONPATH=./:$PYTHONPATH \
python $USER_CONFIG_REPO/trip.py  \
	-c $USER_CONFIG_REPO/pipeline.cfg \
    -t $USER_CONFIG_REPO/trip-tasks.cfg -d $*
