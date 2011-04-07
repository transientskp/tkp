#!/usr/bin/python

#
# To run this script correctly :
# (1) in settings.py: Uncomment database_type = "MonetDB"
# (2) in database.py: Uncomment the MonetDB import statement
# (3) start MonetDB server: %> ./mserver5 --dbname="pipeline_develop" --dbinit="include sql;"
# (4) create schema: %> ./setup.pipeline_develop.db.batch
# (5) GO!
# This should give the generated dataset id as output result
#

import MonetSQLdb

def selectObservations():
    try:
        conn = MonetSQLdb.connect(dbname = 'pipeline_develop', host = 'pc-swinbank.science.uva.nl', port = 50000, lang = 'sql', user = 'lofar', password = 'cs1')
        #conn = MonetSQLdb.connect(host = 'acamar.science.uva.nl', port = 50000, user = 'lofar', password = 'cs1', lang = 'sql')
        #conn = MonetSQLdb.connect(host = 'localhost', user = 'lofar', password = 'cs1', lang = 'sql')
        cursor = conn.cursor()
        query = "SELECT insertdataset('hello');"
        #query = "SELECT alpha(3.14,60);"
        #query = "SELECT obsid, time_s, time_e, description FROM observations"
        #query = "SELECT * FROM tables"
        cursor.execute(query)
        #print cursor._rows()
        #rows = cursor.fetchall()
        dsid = cursor.fetchall()
        cursor.close()
        #return rows
        print dsid
        return dsid
    except MonetSQLdb.Error, e:
        print "Insert Observation Failed"
        print e
        return -1

def main():
    try:
        print selectObservations()
    except MonetSQLdb.Error, e:
        print "Insert in main Failed"
	print e

if __name__ == "__main__":
    main()
