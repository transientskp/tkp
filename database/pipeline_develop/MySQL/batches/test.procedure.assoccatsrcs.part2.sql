#!/bin/sh
# This script loads the DDLs for the MySQL pipeline_develop DB
# 

./setup.pipeline_develop.db.batch

echo -e "Associate 1000 WENSS sources with 100000 XMM sources"
mysql -ulofar -pcs1 -Dpipeline_develop < ../queries/test.proc.assoccatsrcs.wenss1000.xmm100000.sql

./setup.pipeline_develop.db.batch

echo -e "Associate 10000 WENSS sources with 100000 XMM sources"
mysql -ulofar -pcs1 -Dpipeline_develop < ../queries/test.proc.assoccatsrcs.wenss10000.xmm100000.sql 

./setup.pipeline_develop.db.batch

echo -e "Associate 100000 WENSS sources with 100000 XMM sources"
mysql -ulofar -pcs1 -Dpipeline_develop < ../queries/test.proc.assoccatsrcs.wenss100000.xmm100000.sql

./setup.pipeline_develop.db.batch

echo -e "Associate all WENSS sources with 100000 XMM sources"
mysql -ulofar -pcs1 -Dpipeline_develop < ../queries/test.proc.assoccatsrcs.wenssall.xmm100000.sql

./setup.pipeline_develop.db.batch

echo -e "Associate 1000 WENSS sources with all XMM sources"
mysql -ulofar -pcs1 -Dpipeline_develop < ../queries/test.proc.assoccatsrcs.wenss1000.xmmall.sql

./setup.pipeline_develop.db.batch

echo -e "Associate 10000 WENSS sources with all XMM sources"
mysql -ulofar -pcs1 -Dpipeline_develop < ../queries/test.proc.assoccatsrcs.wenss10000.xmmall.sql

./setup.pipeline_develop.db.batch

echo -e "Associate 100000 WENSS sources with all XMM sources"
mysql -ulofar -pcs1 -Dpipeline_develop < ../queries/test.proc.assoccatsrcs.wenss100000.xmmall.sql

./setup.pipeline_develop.db.batch

echo -e "Associate all WENSS sources with all XMM sources"
mysql -ulofar -pcs1 -Dpipeline_develop < ../queries/test.proc.assoccatsrcs.wenssall.xmmall.sql

