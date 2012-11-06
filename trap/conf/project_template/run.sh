#!/bin/bash

HERE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ -z "$1" ]; then
    echo "please supply a job name"
    exit 1
fi

JOB=$1
JOBDIR=${HERE}/${JOB}

if [ ! -x ${JOBDIR} ]; then
    echo "${JOB} doesn't exists"
    exit
fi

PYTHONPATH=${JOBDIR}:$PYTHONPATH

trap-run.py \
 -c $HERE/pipeline.cfg \
 -t $HERE/tasks.cfg -d -j ${JOB}
