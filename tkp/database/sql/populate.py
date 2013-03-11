#!/usr/bin/env python
"""
initialises a PostgreSQL database with TKP tables.
"""

import os
import sys
import argparse
import getpass

from tkp.database.sql.preprocessor import dialectise

here = os.path.dirname(__file__)

# use these to replace strings in the SQL files
tokens = (
    ('%NODE%', '1'),
    ('%NODES%', '1'),
    ('%VLSS%', os.path.join(here, 'catalog/vlss/vlss.csv')),
    ('%WENSS%', os.path.join(here, 'catalog/wenss/wenss.csv')),
    ('%NVSS%', os.path.join(here, 'catalog/nvss/nvss.csv')),
    ('%EXO%', os.path.join(here, 'catalog/exoplanets/exo.csv')),
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
    if options.database:
        if not options.user:
            options.user = options.database
            #if not parsed.password:
            #    parsed.password = parsed.database

    if not options.yes:
        verify(options)

    conn = connect(options)
    cur = conn.cursor()

    batch_file = os.path.join(here, 'sql/batch')

    for line in [l.strip() for l in open(batch_file) if not l.startswith("#")]:
        if not line: # skip empty lines
            continue
        sql_file = os.path.join(here, 'sql', line)
        with open(sql_file) as sql_handler:
            sql = sql_handler.read()
            dialected = dialectise(sql, options.backend, tokens)
            try:
                cur.execute(dialected)
            except Exception as e:
                sys.stderr.write("\nproblem with file \"%s\"\n\n" % sql_file)
                raise

    cur.close()
    conn.close()
