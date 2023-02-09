"""
initialises or removes TRAP tables in a database.
"""

import os
import re
import sys
import tkp
from tkp.db.model import SCHEMA_VERSION
import tkp.db.database
import tkp.db.model
import tkp.db.quality
from tkp.config import get_database_config
from sqlalchemy.exc import ProgrammingError


tkp_folder = tkp.__path__[0]
sql_repo = os.path.join(tkp_folder, 'db/sql/statements')

from tkp.db.sql.preprocessor import dialectise


def get_input(text):
    """
    We take this out of verify() so we can mock it in the test.
    """
    return input(text)


def verify(dbconfig):
    """
    Verify with the user if he wants to continue with the given settings.

    :param parsed: a argparse namespace
    """
    print("\nThis script will populate a database with these settings:")
    print("")
    print("\tengine:     " + (dbconfig['engine'] or ""))
    print("\tdatabase:   " + (dbconfig['database'] or ""))
    print("\tuser:       " + (dbconfig['user'] or ""))
    print("\tpassword:   " + (dbconfig['password'] or ""))
    print("\thost:       " + (dbconfig['host'] or ""))
    print("\tport:       " + str(dbconfig['port']))

    if not re.match(r'\w+$', dbconfig['database']):
        print("\n!!! WARNING !!! Banana does not handles non-alphanumeric "
              "database names well. Please remove any non-alphanumeric "
              "character from the database name.")

    if dbconfig['destroy']:
        print("\n!!! WARNING !!! This will first REMOVE all data in '%s'"
              % dbconfig['database'])

    answer = get_input("\nDo you want to continue? [y/N]: ")
    if answer.lower() != 'y':
        sys.stderr.write("Aborting.\n")
        sys.exit(1)



def destroy_postgres(connection):
    """
    Destroys the content of a PostgreSQL database.

    !! WARNING !! DESTROYS ALL CONTENTS OF THE DATABASE

    args:
        connection: A PostgresSQL DB connection
    """

    # queries below generate a resultset with rows containing SQL queries
    # which can be executed to drop the db content
    postgres_gen_drop_tables = """
select 'drop table if exists "' || tablename || '" cascade;'
  from pg_tables
 where schemaname = 'public';
"""
    postgres_gen_drop_functions = """
select 'drop function if exists ' || ns.nspname || '.' || proname
       || '(' || oidvectortypes(proargtypes) || ') cascade;'
from pg_proc inner join pg_namespace ns on (pg_proc.pronamespace = ns.oid)
where ns.nspname = 'public'  order by proname;
"""

    postgres_gen_drop_sequences = """
select 'drop sequence ' ||  relname || ';'
from pg_class c
inner join pg_namespace ns on (c.relnamespace = ns.oid)
where ns.nspname = 'public' and c.relkind = 'S';
"""

    for big_query in postgres_gen_drop_tables, \
                     postgres_gen_drop_functions, \
                     postgres_gen_drop_sequences:
        cursor = connection.cursor()
        cursor.execute(big_query)
        queries = [row[0] for row in cursor.fetchall()]
        for query in queries:
            print(query)
            cursor.execute(query)
        connection.commit()


def destroy(dbconfig):
    """
    Destroys the content of a database defined by settings in dbconfig dict.

    !! WARNING !! DESTROYS ALL CONTENT

    args:
        dbconfig: a dict containing connection params for database
    """
    assert(dbconfig['destroy'])
    if dbconfig['engine'] == 'postgresql':
        database = tkp.db.database.Database()

        destroy_postgres(database.connection.connection)


def populate(dbconfig):
    """
    Populates a database with TRAP tables.

    args:
        dbconfig: a dict containing db connection settings

    raises an exception when one of the tables already exists.
    """

    if not dbconfig['yes']:
        verify(dbconfig)

    # configure the database before we do anyting else
    get_database_config(dbconfig, apply=True)

    database = tkp.db.database.Database()
    database.connect(check=False)

    if dbconfig['destroy']:
        destroy(dbconfig)

    if dbconfig['engine'] == 'postgresql':
        # make sure plpgsql is enabled
        try:
            database.session.execute("CREATE LANGUAGE plpgsql;")
        except ProgrammingError:
            database.session.rollback()

    batch_file = os.path.join(sql_repo, 'batch')

    error = "\nproblem processing \"%s\".\nMaybe the DB is already populated. "\
            "Try -d/--destroy argument for initdb cmd.\n\n"

    tkp.db.model.Base.metadata.create_all(database.alchemy_engine)

    version = tkp.db.model.Version(name='revision',
                                   value=tkp.db.model.SCHEMA_VERSION)
    database.session.add(version)

    tkp.db.quality.sync_rejectreasons(database.session)

    for line in [l.strip() for l in open(batch_file) if not l.startswith("#")]:
        if not line:  # skip empty lines
            continue
        print("processing %s" % line)
        sql_file = os.path.join(sql_repo, line)
        with open(sql_file) as sql_handler:
            sql = sql_handler.read()
            major_version = database.session.get_bind().dialect.server_version_info[0]
            dialected = dialectise(sql, dbconfig['engine'], version=major_version).strip()

            if not dialected:  # empty query, can happen
                continue
            try:
                database.session.execute(dialected)
            except Exception as e:
                sys.stderr.write(error % sql_file)
                raise

        database.session.commit()
        database.close()

