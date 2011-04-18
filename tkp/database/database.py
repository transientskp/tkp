#
# LOFAR Transients Key Project
#
# Interface with the pipeline databases.
#

import logging
import contextlib
import monetdb.sql as db
from tkp.config import config
from ..utility.exceptions import TKPException, TKPDataBaseError


ENABLED = config['database']['enabled']
HOST = config['database']['host']
USER = config['database']['user']
PASSWD = config['database']['password']
DBASE = config['database']['name']
PORT = config['database']['port']


def connection(hostname=HOST, username=USER, password=PASSWD, database=DBASE,
               dbport=PORT):
    """Returns a connection object or raise an error if not enabled

    Use defaults from the config module, but the user can override these
    """

    if not ENABLED:
        raise TKPDataBaseError("Database is not enabled")
    conn = db.connect(hostname=hostname, username=username,
                      password=password, database=database, port=dbport)
    return conn


def connection_to_db(usr, dbname):
    """Returns a connection object or raise an error if not enabled"""

    user = usr
    dbase = dbname
    if not ENABLED:
        raise TKPDataBaseError("Database is not enabled")
    else:
        conn = db.connect(hostname=HOST, username=USER, password=PASSWD,
                          port=PORT)
    return conn


def call_proc(conn, procname):
    """Calls a particular database procedure"""

    if not ENABLED:
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
    """Save a list of detections belonging to a particular dataset to
    the database"""

    cursor = conn.cursor()
    try:
        for det in objectlist:
            ##print "det.serializeAll():",det.serializeAll()
            ##print "det.serialize()[1]:",det.serialize()[1]
            ## TODO: how to handle weird fits?
            ## Here we exclude a position in an image with id 327...
            ##if ((det.serialize()[0] == 327) and (det.serialize()[1] >
            # 161.205 and det.serialize()[1] < 161.212) and
            # (det.serialize()[2] > 21.617 and det.serialize()[2] < 21.628)):
            ##    print "\nNOTE: Not inserted :\n",det.serialize(), "\n"
            ##else:
            procInsert = "CALL InsertSrc(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)" % (
                dataset.id, ) + det.serialize()
            ##print procInsert
            cursor.execute(procInsert)
            ##cursor.execute("COPY INTO insertedsources " + \
            ##               "FROM STDIN UNSING DELIMITERS '\r\n','\t' ", (
            ##det.serialize(),))
    except db.Error, e:
        logging.warn("Insert source %s failed" % str((dataset.id, ) +
                                                     det.serialize()))
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
        logging.warn("Associating image %s failed." % (str(imageid), ))
        raise
