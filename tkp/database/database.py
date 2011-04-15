#
# LOFAR Transients Key Project
#
# Interface with the pipeline databases.
#

#from pysqlite2 import dbapi2 as db
#
# Uncomment the import statement depending on the DB
# that is used
#
import logging
import contextlib

import tkp.settings as settings
from ..utility.exceptions import TKPException, TKPDataBaseError


enabled = settings.database_enabled
host = settings.database_host
user = settings.database_user
passwd = settings.database_passwd
dbase = settings.database_dbase
lang = settings.database_lang
port = settings.database_port
dbtype = settings.database_type

if dbtype == "MySQL":
    import MySQLdb as db
    from MySQLdb import Error as Error
elif dbtype == "MonetDB":
    import monetdb.sql as db
    from monetdb.sql import Error as Error

test = settings.database_test


@contextlib.contextmanager
def connect(*args, **kwargs):
    db = connection(*args, **kwargs)
    try:
        yield db
    finally:
        # we probably still need to check for actual database opening errors
        db.close()


def connection(hostname=host, username=user, password=passwd, database=dbase, 
               dbport=port):
    """Returns a connection object or raise an error if not enabled

    Use defaults from the settings module, but the user can override these
    """

    if not enabled:
        raise TKPDataBaseError("Database is not enabled")
    if lang == "sql":
        conn = db.connect(hostname=hostname, username=username, 
                          password=password, database=database, port=dbport)
    else:
        conn = db.connect(host=hostname, user=username, passwd=password, 
                          db=database)
    return conn


def connection_to_db(usr, dbname):
    """Returns a connection object or raise an error if not enabled"""

    user = usr
    dbase = dbname
    if not enabled:
        raise TKPDataBaseError("Database is not enabled")
    elif lang == "sql":
        conn = db.connect(hostname=host, username=user, password=passwd, port=port)
    else:
        conn = db.connect(host=host, user=user, passwd=passwd, db=dbase)
    return conn


def call_proc(conn, procname):
    """Calls a particular database procedure"""
    
    if not enabled:
        raise TKPDataBaseError("Database is not enabled")
    cursor = conn.cursor()
    try:
        cursor.execute(procname)
    except dbError, e:
        logging.warn("DB procedure %s failed" % (procname,))
        raise
    finally:
        cursor.close()
        conn.commit()

def save_to_db(dataset, objectlist, conn):
    """Save a list of detections belonging to a particular dataset to the database"""
    
    cursor = conn.cursor()
    try:
        for det in objectlist:
            ##print "det.serializeAll():",det.serializeAll()
            ##print "det.serialize()[1]:",det.serialize()[1]
            ## TODO: how to handle weird fits?
            ## Here we exclude a position in an image with id 327...
            ##if ((det.serialize()[0] == 327) and (det.serialize()[1] > 161.205 and det.serialize()[1] < 161.212) and (det.serialize()[2] > 21.617 and det.serialize()[2] < 21.628)):
            ##    print "\nNOTE: Not inserted :\n",det.serialize(), "\n"
            ##else:
            procInsert = "CALL InsertSrc(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)" % (dataset.id,) + det.serialize()
            ##print procInsert
            cursor.execute(procInsert)
            ##cursor.execute("COPY INTO insertedsources " + \
            ##               "FROM STDIN UNSING DELIMITERS '\r\n','\t' ", (det.serialize(),))
    except db.Error, e:
        logging.warn("Insert source %s failed" % str((dataset.id,) + det.serialize()))
        raise
    finally:
        cursor.close()
    conn.commit()


def assoc_in_db(imageid, conn):
    """Associate the sources found in imageid with the database catalogs"""
    
    procAssoc = "CALL AssocXSourceByImage(%d)" % (imageid) 
    try:
        call_proc(conn, procAssoc)
    except db.Error, e:
        logging.warn("Associating image %s failed" % (str(imageid),))
        raise


def assoc_xsrc_to_xsrc(imageid, conn):
    """Associate sources with sources from a previous image"""
    
    procAssoc = "CALL AssocXSources2XSourcesByImage(%d)" % (imageid) 
    try:
        call_proc(conn, procAssoc)
    except db.Error, e:
        logging.warn("Associating image %s failed." % (str(imageid),))
        raise
    

def assoc_xsrc_to_cat(imageid, conn):
    """Associate sources with the current catalog"""
    
    procAssoc = "CALL AssocXSources2CatByImage(%d)" % (imageid) 
    try:
        call_proc(conn, procAssoc)
    except db.Error, e:
        logging.warn("Associating image %s failed." % (str(imageid),))
        raise
