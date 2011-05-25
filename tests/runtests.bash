#! /bin/bash

if [ -z "$PYTHONPATH" ]
then
    export PYTHONPATH=./tkp/python-packages/lib.linux-x86_64-2.6:./tkp/trunk/external/deconv:./tkp/trunk/external/python-wcslib
else
    export PYTHONPATH=${PYTHONPATH}:./tkp/python-packages/lib.linux-x86_64-2.6:./tkp/trunk/external/deconv:./tkp/trunk/external/python-wcslib
fi
if [ -z "$LD_LIBRARY_PATH" ]
then
    export LD_LIBRARY_PATH=./tkp/trunk/external/libwcstools
else
    export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:./tkp/trunk/external/libwcstools
fi

dir=`dirname $0`
echo "Running python TKP tests"
python ${dir}/test.py
