#! /bin/bash

pythonpath=./tkp/python-packages/lib.linux-x86_64-2.6:./tkp/trunk/external/deconv:./tkp/trunk/external/python-wcslib:../tkp/tests
if [ -z "$PYTHONPATH" ]
then
    export PYTHONPATH=${pythonpath}
else
    export PYTHONPATH=${PYTHONPATH}:${pythonpath}
fi
ld_library_path=./tkp/trunk/external/libwcstools
if [ -z "$LD_LIBRARY_PATH" ]
then
    export LD_LIBRARY_PATH=${ld_library_path}
    export DYLD_LIBRARY_PATH=${ld_library_path}
else
    export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${ld_library_path}
    export DYLD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${ld_library_path}
fi
# Needs check whether we're on OS X, but setting an extra
# environment variable should not be a problem
if [ -z "$DYLD_LIBRARY_PATH" ]
then
    export DYLD_LIBRARY_PATH=${ld_library_path}
else
    export DYLD_LIBRARY_PATH=${DYLD_LIBRARY_PATH}:${ld_library_path}
fi

dir=`dirname $0`
echo "Running python TKP tests"
python ${dir}/test.py
