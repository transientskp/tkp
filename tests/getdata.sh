#!/bin/bash

DIRECTORY=data

if [ -d "$DIRECTORY" ]; then
    pushd $DIRECTORY
        svn up
    popd
else
    svn co http://svn.transientskp.org/data/unittests/tkp_lib/ data
fi


