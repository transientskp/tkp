#!/usr/bin/env python
"""
initialises a PostgreSQL database with TKP tables.
"""

import os
import sys
import tkp

tkp_folder = tkp.__path__[0]
sql_repo = os.path.join(tkp_folder, 'database/sql/statements')

from tkp.database.sql.preprocessor import dialectise

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
    print("WARNING: this script will populate a database with these settings:")
    print("")
    print("\tbackend:  " + parsed.backend)
    print("\tdatabase: " + parsed.database)
    print("\tuser:     " + parsed.user)
    print("\tpassword: " + (parsed.password or ""))
    print("\thost:     " + (parsed.host or ""))
    print("\tport:     " + str(parsed.port))
    print("")
    answer = raw_input("Do you want to continue? [y/N]: ")
    if answer.lower() != 'y':
        print("Aborting.")
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
                                   port=parsed.port)



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

    if options.backend == 'monetdb' and not options.password:
        options.password = options.database

    if not options.yes:
        verify(options)

    conn = connect(options)
    #conn.autocommit = True
    cur = conn.cursor()

    batch_file = os.path.join(sql_repo, 'batch')

    for line in [l.strip() for l in open(batch_file) if not l.startswith("#")]:
        if not line:  # skip empty lines
            continue
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

    cur.close()
    conn.close()
