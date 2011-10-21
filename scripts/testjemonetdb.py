#!/usr/bin/python

import tkp.database.database as database
import monetdb.sql as db

db_host = "togano"
db_dbase = "node1db"
#db_dbase = "node1db+node1db@*/lightcurve1,node2db+node2db@*/lightcurve2,node3db+node3db@*/lightcurve3"
db_user = "node1db"
db_passwd = "node1db"
db_port = 60200
db_autocommit = False


def selectVersion():
    try:
        db = database.DataBase(host=db_host, name=db_dbase, 
                               user=db_user, password=db_passwd, 
                               port=db_port, autocommit=True)
        conn = db.connection
        cursor = conn.cursor()
        query = """\
        SELECT *
          FROM versions
        """
        cursor.execute(query)
        results = cursor.fetchall()
        #conn.commit()
    except db.Error, e:
        print "Error on Query %s; with reason %s" % (query,e)
        raise
    finally:
        cursor.close()
        conn.close()
    return results

def insertVersion():
    try:
        db = database.DataBase(host=db_host, name=db_dbase, 
                               user=db_user, password=db_passwd, 
                               port=db_port, autocommit=True)
        conn = db.connection
        cursor = conn.cursor()
        version = '0.0.2'
        scriptname = '/this'
        query = """\
        INSERT INTO versions
          (version
          ,creation_date
          ,monet_version
          ,scriptname
          )
        VALUES 
          (%s
          ,NOW()
          ,'11.5.3'
          ,%s
               )
        """
        results = cursor.execute(query, (version,scriptname))
        #conn.commit()
    except db.Error, e:
        print "Error on Query %s; with reason %s" % (query,e)
        raise
    finally:
        cursor.close()
        conn.close()
    return results

def main():
        print selectVersion()
        print insertVersion()
        print selectVersion()

if __name__ == "__main__":
    main()
