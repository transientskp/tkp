#!/usr/bin/env python
"""
initialises a PostgreSQL database with TKP tables.
"""

import os
import sys
from subprocess import call
import tkp


tkp_folder = tkp.__path__[0]
sql_repo = os.path.join(tkp_folder, 'db/sql/statements')

from tkp.db.sql.preprocessor import dialectise

# use these to replace strings in the SQL files
tokens = (
    ('%NODE%', '1'),
    ('%NODES%', '1'),
    ('%VLSS%', os.path.join(tkp_folder, '../database/catalog/vlss/vlss.csv')),
    ('%WENSS%', os.path.join(tkp_folder, '../database/catalog/wenss/wenss.csv')),
    ('%NVSS%', os.path.join(tkp_folder, '../database/catalog/nvss/nvss.csv')),
    ('%EXO%', os.path.join(tkp_folder, '../database/catalog/exoplanets/exo.csv')),
)


def verify(dbconfig):
    """
    Verify with the user if he wants to continue with the given settings.

    :param parsed: a argparse namespace
    """
    print("This script will populate a database with these settings:")
    print("")
    print("\tengine:    " + (dbconfig['engine'] or ""))
    print("\tdatabase:   " + (dbconfig['database'] or ""))
    print("\tuser:       " + (dbconfig['user'] or ""))
    print("\tpassword:   " + (dbconfig['password'] or ""))
    print("\thost:       " + (dbconfig['host'] or ""))
    print("\tport:       " + str(dbconfig['port']))
    print("\tpassphrase: " + (dbconfig['passphrase'] or ""))
    print("")
    print("!!! WARNING !!! This will REMOVE all data in '%s'" % dbconfig['database'])
    print("")
    answer = raw_input("Do you want to continue? [y/N]: ")
    if answer.lower() != 'y':
        sys.stderr.write("Aborting.")
        sys.exit(1)


def connect(dbconfig):
    """
    Connect to the database

    :param parsed: an argparse namespace
    :returns: a database connection
    """
    if dbconfig['engine'] == "postgresql":
        import psycopg2
        return psycopg2.connect(database=dbconfig['database'], user=dbconfig['user'],
                                password=dbconfig['password'], host=dbconfig['host'],
                                port=dbconfig['port'])
    elif dbconfig['engine'] == "monetdb":
        import monetdb
        return monetdb.sql.connect(database=dbconfig['database'], user=dbconfig['user'],
                                   password=dbconfig['password'], host=dbconfig['host'],
                                   port=dbconfig['port'], autocommit=True)
    else:
        sys.stderr.write("engine %s is not implemented" % dbconfig['engine'])
        raise NotImplementedError

auth_query = """
ALTER USER "monetdb" RENAME TO "%(username)s";
ALTER USER SET PASSWORD '%(password)s' USING OLD PASSWORD 'monetdb';
CREATE SCHEMA "%(database)s" AUTHORIZATION "%(username)s";
ALTER USER "%(username)s" SET SCHEMA "%(database)s";
"""

def recreate(dbconfig):
    """
    Destroys and creates a new database.

    :param options: a argparse namespace generated with tkp.management

    WARNING: this will DESTROY your database!

    Note: this will raise an Exception ONLY when the creation of the database
          fails
    """
    params = {'username': dbconfig['user'],
              'password': dbconfig['password'],
              'database': dbconfig['database'],
              'host': dbconfig['host']
              }
    if dbconfig['engine'] == 'monetdb':
        import monetdb.sql
        import monetdb.control
        control = monetdb.control.Control(dbconfig['host'], dbconfig['port'],
                                          dbconfig['passphrase'])

        database = dbconfig['database']
        print("stopping %s" % database)
        try:
            control.stop(database)
        except monetdb.sql.OperationalError, e:
            print("database not running")
        print "destroying %s" % database
        try:
            control.destroy(database)
        except monetdb.sql.OperationalError, e:
            print("can't destroy database: %s" % str(e))

        control.create(database)
        control.release(database)
        control.start(database)

        con = monetdb.sql.connect(username='monetdb', password='monetdb',
                                  hostname=dbconfig['host'], port=dbconfig['port'],
                                  database=dbconfig['database'])
        cur = con.cursor()
        cur.execute(auth_query % params)
        con.commit()
        con.close()

    elif dbconfig['engine'] == 'postgresql':
        print "destroying database %(database)s on %(host)s..." % params
        call('dropdb -h %(host)s -U %(username)s %(database)s' % params,
             shell=True)
        print "creating database %(database)s on %(host)s..." % params
        if call('createdb -h %(host)s -U %(username)s %(database)s' % params,
                shell=True) != 0:
            raise Exception("can't create a new postgresql database!")
        print "installing plpgsql langunage for %(database)s on %(host)s..." % params
        if call('createlang -h %(host)s -U %(username)s plpgsql %(database)s' % params,
                shell=True) != 0:
            raise Exception("can't create a new postgresql database!")
    else:
        raise NotImplementedError


def populate(dbconfig):
    """
    Populates a database
    :param dbconfig: a dict containing db connection settings
    """

    if not dbconfig['yes']:
        verify(dbconfig)

    recreate(dbconfig)
    conn = connect(dbconfig)
    cur = conn.cursor()

    batch_file = os.path.join(sql_repo, 'batch')

    for line in [l.strip() for l in open(batch_file) if not l.startswith("#")]:
        if not line:  # skip empty lines
            continue
        print "processing %s" % line
        sql_file = os.path.join(sql_repo, line)
        with open(sql_file) as sql_handler:
            sql = sql_handler.read()
            dialected = dialectise(sql, dbconfig['engine'], tokens).strip()

            if not dialected:  # empty query, can happen
                continue

            try:
                cur.execute(dialected)
            except Exception as e:
                sys.stderr.write("\nproblem with file \"%s\"\n\n" % sql_file)
                raise
    if dbconfig['engine'] == 'postgresql':
        conn.commit()
    conn.close()
