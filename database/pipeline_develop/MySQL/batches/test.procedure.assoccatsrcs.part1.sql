#!/bin/sh
# This script loads the DDLs for the MySQL pipeline_develop DB
# 

./setup.pipeline_develop.db.batch

echo -e "Associate 1000 WENSS sources with 1000 XMM sources"
mysql -ulofar -pcs1 -Dpipeline_develop < ../queries/test.proc.assoccatsrcs.wenss1000.xmm1000.sql

./setup.pipeline_develop.db.batch

echo -e "Associate 10000 WENSS sources with 1000 XMM sources"
mysql -ulofar -pcs1 -Dpipeline_develop < ../queries/test.proc.assoccatsrcs.wenss10000.xmm1000.sql

./setup.pipeline_develop.db.batch

echo -e "Associate 100000 WENSS sources with 1000 XMM sources"
mysql -ulofar -pcs1 -Dpipeline_develop < ../queries/test.proc.assoccatsrcs.wenss100000.xmm1000.sql

./setup.pipeline_develop.db.batch

echo -e "Associate all WENSS sources with 1000 XMM sources"
mysql -ulofar -pcs1 -Dpipeline_develop < ../queries/test.proc.assoccatsrcs.wenssall.xmm1000.sql

./setup.pipeline_develop.db.batch

echo -e "Associate 1000 WENSS sources with 10000 XMM sources"
mysql -ulofar -pcs1 -Dpipeline_develop < ../queries/test.proc.assoccatsrcs.wenss1000.xmm10000.sql

./setup.pipeline_develop.db.batch

echo -e "Associate 10000 WENSS sources with 10000 XMM sources"
mysql -ulofar -pcs1 -Dpipeline_develop < ../queries/test.proc.assoccatsrcs.wenss10000.xmm10000.sql

./setup.pipeline_develop.db.batch

echo -e "Associate 100000 WENSS sources with 10000 XMM sources"
mysql -ulofar -pcs1 -Dpipeline_develop < ../queries/test.proc.assoccatsrcs.wenss100000.xmm10000.sql

./setup.pipeline_develop.db.batch

echo -e "Associate all WENSS sources with 10000 XMM sources"
mysql -ulofar -pcs1 -Dpipeline_develop < ../queries/test.proc.assoccatsrcs.wenssall.xmm10000.sql 

