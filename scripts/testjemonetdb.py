#!/usr/bin/python

import MonetSQLdb

def selectObservations():
    try:
        conn = MonetSQLdb.connect(host = 'acamar.science.uva.nl', port = 50000, user = 'lofar', password = 'cs1', lang = 'sql')
        cursor = conn.cursor()
        #query = "SELECT testfunct()"
        query = "SELECT testinsertgetdataset('gaatt?')"
        cursor.execute(query)
        dsid = cursor.fetchall()
        cursor.close()
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
