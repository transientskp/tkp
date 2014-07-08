#!/usr/bin/env python
"""
initialises a PostgreSQL database with TKP tables.
"""

import os
import sys
from subprocess import call
import tkp
from tkp.db.database import DB_VERSION


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
    ('%VERSION%', str(DB_VERSION))
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


monetdb_auth_query = """
ALTER USER "monetdb" RENAME TO "%(user)s";
ALTER USER SET PASSWORD '%(password)s' USING OLD PASSWORD 'monetdb';
CREATE SCHEMA "%(database)s" AUTHORIZATION "%(user)s";
ALTER USER "%(user)s" SET SCHEMA "%(database)s";
"""


def recreate_monetdb(dbconfig):
    """
    Destroys and creates a new MonetDB database.

    WARNING: this will DESTROY your database!

    args:
        dbconfig: a dict containing the database configuration
    """
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
    cur.execute(monetdb_auth_query % dbconfig)
    con.commit()
    con.close()


def recreate_postgresql(dbconfig):
    """
    Destroys and creates a new PostgreSQL database.

    WARNING: this will DESTROY your database!

    args:
        dbconfig: a dict containing the database configuration
    """
    import psycopg2
    con = psycopg2.connect(user=dbconfig['user'],
                           password=dbconfig['password'],
                           port=dbconfig['port'], host=dbconfig['host'],
                           database='postgres')
    con.autocommit = True
    cur = con.cursor()
    print "destroying database %(database)s on %(host)s..." % dbconfig
    try:
        cur.execute('DROP DATABASE %s' % dbconfig['database'])
    except psycopg2.ProgrammingError:
        pass
    print "creating database %(database)s on %(host)s..." % dbconfig
    cur.execute('CREATE DATABASE %s' % dbconfig['database'])
    if dbconfig['database'] != dbconfig['user']:
        # TODO (Gijs): This is a bad idea and should be solved.
        print "creating a SUPERUSER with name %(database)s on %(host)s..." %\
              dbconfig

        cur.execute("CREATE USER %s WITH PASSWORD '%s' SUPERUSER" %
                    (dbconfig['database'], dbconfig['database']))


def recreate(dbconfig):
    """
    Destroys and creates a new database.

    WARNING: this will DESTROY your database!

    args:
        dbconfig: a dict containing the database configuration
    """
    if dbconfig['engine'] == 'monetdb':
        recreate_monetdb(dbconfig)
    elif dbconfig['engine'] == 'postgresql':
        recreate_postgresql(dbconfig)
    else:
        raise NotImplementedError("we only support monetdb & postgresql")


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

    if dbconfig['engine'] == 'postgresql':
        # make sure plpgsql is enabled
        try:
            cur.execute("CREATE LANGUAGE plpgsql;")
        except conn.ProgrammingError:
            conn.rollback()

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
