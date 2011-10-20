#! /bin/bash

pythonpath=../../python-packages/lib.linux-x86_64-2.6:../external/deconv:../external/python-wcslib
# Add path for unittest2 & argparse
pythonpath=${pythonpath}:../../../../tkp/trunk/tests
if [ -z "$PYTHONPATH" ]
then
    export PYTHONPATH=${pythonpath}
else
    export PYTHONPATH=${PYTHONPATH}:${pythonpath}
fi

ld_library_path=../../../tkp/trunk/external/libwcstools:/opt/cep/LofIm/daily/casacore/lib:/opt/cep/LofIm/daily/pyrap/lib
# extra paths on heastro
ld_library_path=${ld_library_path}:/opt/wcslib/lib:/opt/casacore/lib:/opt/casarest/lib:/opt/pyrap/lib
if [ -z "$LD_LIBRARY_PATH" ]
then
    export LD_LIBRARY_PATH=${ld_library_path}
else
    export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${ld_library_path}
fi
# Needs check whether we're on OS X, but setting an extra
# environment variable should not be a problem
if [ -z "$DYLD_FALLBACK_LIBRARY_PATH" ]
then
    export DYLD_FALLBACK_LIBRARY_PATH=${ld_library_path}
else
    export DYLD_FALLBACK_LIBRARY_PATH=${DYLD_FALLBACK_LIBRARY_PATH}:${ld_library_path}
fi

# MonetDB Python path on heastro
export PYTHONPATH=${PYTHONPATH}:/opt/monetdb/lib/python2.6/site-packages:/opt/pyrap/lib/python2.6/dist-packages
# Extra paths needed on CEP1
export PYTHONPATH=../../python-packages/lib:${PYTHONPATH}:/opt/pythonlibs/lib/python2.5/site-packages/:/opt/MonetDB/
# Extra paths needed on CEP2
export PYTHONPATH=${PYTHONPATH}:/opt/cep/MonetDB/lib/python/site-packages:/opt/cep/LofIm/daily/pyrap/lib:/home/rol/sw/lib/python2.6/site-packages
dir=`dirname $0`

datapath=
if [ -d /zfs/heastro-plex/scratch/evert/testdata ]
then
    datapath='--datapath=/zfs/heastro-plex/scratch/evert/testdata'
fi
result=`python ${dir}/test.py ${datapath} "$@"`
exit $result
