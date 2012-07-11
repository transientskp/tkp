#! /bin/bash

# Script to use with simlightcurve's --command option:
# this script will start the pipeline, setting up the parsets
# and config files in the correct manner.
# Take care of providing the correct runtime dir & job, otherwise
# the script won't find the parset. Ditto for the location
# of the pipeline.cfg file


RUNTIMEDIR=/home/evert/work/trap
JOB=A
CONFIGFILE=/home/evert/work/trap/trap.cfg


imageid=$1
datasetid=$2

#echo $imageid $datasetid
# set up parset
parsetfile=${RUNTIMEDIR}/jobs/A/parsets/source_association.parset
cat > $parsetfile <<EOF
image_id = ${imageid}
radius = 90                # assocation search radius of 90 arcsec
density = 4.02439375E-06   # source density; this is the NVSS source density
distance = 1.5            # valid distance for source association
EOF


#export LD_LIBRARY_PATH=/opt/LofIm/daily/lofar/lib:/opt/external/boost/boost-1.40.0/lib:/opt/wcslib/lib:/opt/LofIm/daily/pyrap/lib:/opt/LofIm/daily/casarest/build/lib:/opt/hdf5/lib:/opt/LofIm/daily/casacore/lib:/opt/LofIm/external/log4cplus/lib/
export PYTHONPATH=/home/evert/sw/lib/python2.6/site-packages:/usr/lib/python2.6/dist-packages:/opt/pipeline/framework/lib/python2.6/site-packages:/usr/local/lib/python2.6/dist-packages:/opt/LofIm/lofar/lib/python2.6/dist-packages:/usr/local/lib/python2.6/dist-packages:/home/evert/lofar/svn/tkp/code/pipe/python-packages
#export PYTHONPATH=/opt/pipeline/dependencies/lib/python2.5/site-packages:/opt/pipeline/framework/lib/python2.5/site-packages:/opt/LofIm/daily/lofar/lib/python2.5/site-packages:/opt/LofIm/daily/pyrap/lib

# remove the statefile; otherwise we're stuck with repeating the same pipeline part
rm ${RUNTIMEDIR}/jobs/A/statefile

#python -c "import lofar.parameterset"
python /home/evert/work/trap/jobs/A/control/trap.py -jA -d  -c ${CONFIGFILE}
retcode=$?


exit $retcode;
