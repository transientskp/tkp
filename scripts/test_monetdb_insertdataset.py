#!/usr/bin/python

import os
import time
import tkp_lib.database as db

def insertDatasetByQuery(params):
    try:
        conn = db.connection()
        cursor = conn.cursor()
        insds = "INSERT INTO dataset (obs_id, res_id, dstype, taustart_timestamp, inname) VALUES (%d, %d, %d, %d, %s)" %(params)
	    cursor.execute(insds)
	    cursor.close()
	    conn.commit()
    except MySQLdb.Error, e:
        print "Insert Dataset Failed"
	print e
	return -1

def main():
    params = (1, 1, 1, 2008, 'pythontest')
    try:
        insertObservations(params)
    except db.Error, e:
        print "Insert in main Failed"
	print e

if __name__ == "__main__":
    main()
