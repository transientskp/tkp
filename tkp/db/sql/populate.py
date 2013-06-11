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


def verify(parsed):
    """
    Verify with the user if he wants to continue with the given settings.

    :param parsed: a argparse namespace
    """
    print("This script will populate a database with these settings:")
    print("")
    print("\tbackend:  " + parsed.backend)
    print("\tdatabase: " + parsed.database)
    print("\tuser:     " + parsed.user)
    print("\tpassword: " + (parsed.password or ""))
    print("\thost:     " + (parsed.host or ""))
    print("\tport:     " + str(parsed.port))
    print("")
    print("!!! WARNING !!! This will REMOVE all data in '%s'" % parsed.database)
    print("")
    answer = raw_input("Do you want to continue? [y/N]: ")
    if answer.lower() != 'y':
        sys.stderr.write("Aborting.")
        sys.exit(1)


def connect(parsed):
    """
    Connect to the database

    :param parsed: an argparse namespace
    :returns: a database connection
    """
    if parsed.backend == "postgresql":
        import psycopg2
        return psycopg2.connect(database=parsed.database, user=parsed.user,
                                password=parsed.password, host=parsed.host,
                                port=parsed.port)
    elif parsed.backend == "monetdb":
        import monetdb
        return monetdb.sql.connect(database=parsed.database, user=parsed.user,
                                   password=parsed.password, host=parsed.host,
                                   port=parsed.port, autocommit=True)
    else:
        sys.stderr.write("backend %s is not implemented" % parsed.backend)
        raise NotImplementedError

auth_query = """
ALTER USER "monetdb" RENAME TO "%(username)s";
ALTER USER SET PASSWORD '%(password)s' USING OLD PASSWORD 'monetdb';
CREATE SCHEMA "%(database)s" AUTHORIZATION "%(username)s";
ALTER USER "%(username)s" SET SCHEMA "%(database)s";
"""

def recreate(options):
    """
    Destroys and creates a new database.

    :param options: a argparse namespace generated with tkp.management

    WARNING: this will DESTROY your database!

    Note: this will raise an Exception ONLY when the creation of the database
          fails
    """

    params = {'username': options.user,
              'password': options.password,
              'database': options.database,
              'host': options.host
              }

    if options.backend == 'monetdb':
        import monetdb.sql
        monetdb_cmd = lambda cmd: call('monetdb %s %s' % (cmd,
                                                          options.database),
                                       shell=True)
        monetdb_cmd('stop')
        monetdb_cmd('destroy -f')
        monetdb_cmd('create')
        monetdb_cmd('release')
        if monetdb_cmd('start') != 0:
            raise Exception("can't create a new monetdb database!")

        con = monetdb.sql.connect(username='monetdb', password='monetdb',
                                  hostname=options.host, port=options.port,
                                  database=options.database)
        cur = con.cursor()
        cur.execute(auth_query % params)
        con.commit()
        con.close()

    elif options.backend == 'postgresql':
        if params['host'] == 'localhost':
            drop_cmd = 'dropdb %(database)s'
            create_cmd = 'createdb %(database)s'
        else:
            drop_cmd = 'dropdb -h %(host)s -U %(username)s %(database)s'
            create_cmd = 'createdb -h %(host)s -U %(username)s %(database)s'

        call(drop_cmd % params, shell=True)
        if call(create_cmd % params, shell=True) != 0:
            raise Exception("can't create a new postgresql database!")
    else:
        raise NotImplementedError


def populate(options):
    """
    Populates a database
    :param options: a argparse namespace generated with tkp.management
    """
    if options.port == 0:
        if options.backend == 'monetdb':
            options.port = 50000
        else:
            options.port = 5432

    if not options.user:
        options.user = options.database

    if not options.password:
        options.password = options.database

    if not options.host:
        options.host = 'localhost'

    if not options.yes:
        verify(options)

    recreate(options)
    conn = connect(options)
    cur = conn.cursor()

    batch_file = os.path.join(sql_repo, 'batch')

    for line in [l.strip() for l in open(batch_file) if not l.startswith("#")]:
        if not line:  # skip empty lines
            continue
        print "processing %s" % line
        sql_file = os.path.join(sql_repo, line)
        with open(sql_file) as sql_handler:
            sql = sql_handler.read()
            dialected = dialectise(sql, options.backend, tokens).strip()

            if not dialected:  # empty query, can happen
                continue

            try:
                cur.execute(dialected)
            except Exception as e:
                sys.stderr.write("\nproblem with file \"%s\"\n\n" % sql_file)
                raise
    if options.backend == 'postgresql':
        conn.commit()
    conn.close()
