#!/usr/bin/env bash

WHEREAMI="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SQLFILES=${WHEREAMI}/sql
NVSS=${WHEREAMI}/catalog/nvss/nvss.csv
VLSS=${WHEREAMI}/catalog/vlss/vlss.csv
WENSS=${WHEREAMI}/catalog/wenss/wenss.csv


declare -A tokens
tokens["%NODE%"]=1
tokens["%NODES%"]=10
tokens["%NVSS%"]=${NVSS}
tokens["%VLSS%"]=${VLSS}
tokens["%WENSS%"]=${WENSS}


for sql_file in $(cat sql/batch | grep -v ^# | grep tables) ; do
    sql=`cat sql/${sql_file}| grep -v ^[\s]*--`
    for token in ${!tokens[*]}; do
        sql="${sql//${token}/${tokens[${token}]}}"
    done

    echo "${sql}"
done
