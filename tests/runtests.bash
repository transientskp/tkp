#! /bin/bash

export PYTHONPATH=./tkp/python-packages/lib.linux-x86_64-2.6:./tkp/trunk/external/deconv:./tkp/trunk/external/python-wcslib
# Extra paths needed on CEP1
export PYTHONPATH=./tkp/python-packages/lib:${PYTHONPATH}:/opt/pythonlibs/lib/python2.5/site-packages/:/opt/MonetDB/lib/python2.5/site-packages/
export LD_LIBRARY_PATH=./tkp/trunk/external/libwcstools
dir=`dirname $0`
echo "Running python TKP tests"
python ${dir}/test.py
