#!/bin/bash
#################################################################################
#  A script to prep a database dump, ready for TKP unit tests 
#  Flow is as follows:
#  -Create a fresh test database 
#  -Dump to the chosen directory
#  -Output relevant tkp.cfg [test] section entries to a ./tkp-test.cfg
#  -Automatically append these entries to ~/.transientskp.cfg/tkp.cfg if safe to do so.
#
#################################################################################
# User variables:

DB_DUMP_DIR=/opt/repos/tkp-data/unittests/tkp_lib/db_dump
BATCHFILE=/opt/lofar-dev/symlinks/tkp-root/database/batches/setup.db.batch
TESTDB_NAME=testdb

#############################################################################

START_DIR=`pwd`
cd `dirname $BATCHFILE`  #setup.db.batch fails unless you run it from the batches directory
bash $BATCHFILE localhost $TESTDB_NAME $TESTDB_NAME $TESTDB_NAME
cd $START_DIR

##########################################
#Store user=testdb, password=testdb in local .monetdb defaults file, as these cannot be passed on command line.
cat > .monetdb <<-END
user=$TESTDB_NAME
password=$TESTDB_NAME
END
echo "Database created, dumping..."
mkdir -p $DB_DUMP_DIR
mclient -lsql -h localhost -dtestdb --dump >$DB_DUMP_DIR/fresh_db1.sql
##########################################
cat > tkp-test.cfg <<-END
[test]
test_database_dump_dir = $DB_DUMP_DIR
test_database_name = $TESTDB_NAME
reset_test_database = True              #Recreate fresh test database for every unit test.  (True/False)
END

if  ! grep "\[test\]" ~/.transientskp/tkp.cfg ; then
    echo "Appending database dump dir entry to tkp.cfg"
    cat tkp-test.cfg >> ~/.transientskp/tkp.cfg
else
    echo "Config file [test] section already exists, please edit your ~/.transientskp/tkp.cfg file if necessary"
    echo "(See ./tkp-test.cfg for newly created settings)"
fi





