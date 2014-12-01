"""
initialises or removes TRAP tables in a database.
"""
import os
import sys
import tkp
from tkp.db.database import DB_VERSION


tkp_folder = tkp.__path__[0]
sql_repo = os.path.join(tkp_folder, 'db/sql/statements')

from tkp.db.sql.preprocessor import dialectise

# use these to replace strings in the SQL files
tokens = (
    ('%NODE%', '1'),
    ('%NODES%', '1'),
    ('%VERSION%', str(DB_VERSION))
)





def get_input(text):
    """
    We take this out of verify() so we can mock it in the test.
    """
    return raw_input(text)


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

    if dbconfig['destroy']:
        print("\n!!! WARNING !!! This will first REMOVE all data in '%s'"
              % dbconfig['database'])

    answer = get_input("\nDo you want to continue? [y/N]: ")
    if answer.lower() != 'y':
        sys.stderr.write("Aborting.\n")
        sys.exit(1)


def connect(dbconfig):
    """
    Connect to the database

    args:
        parsed: an argparse namespace

    returns:
        a database connection
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
        msg = "engine %s is not implemented" % dbconfig['engine']
        sys.stderr.write(msg)
        raise NotImplementedError(msg)


def destroy_postgres(connection):
    """
    Destroys the content of a PostgreSQL database.

    !! WARNING !! DESTROYS ALL CONTENTS OF THE DATABASE

    args:
        connection: A monetdb DB connection
    """

    # both queries below generate a resultset with rows containing SQL queries
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

    for big_query in postgres_gen_drop_tables, postgres_gen_drop_functions:
        cursor = connection.cursor()
        cursor.execute(big_query)
        queries = [row[0] for row in cursor.fetchall()]
        for query in queries:
            print query
            cursor.execute(query)
        connection.commit()


def destroy_monetdb():
    """
    Maybe some day destroys the content of a MonetDB database.
    """

    msg = """
tkp-manage.py doesn't support the removal of all MonetDB content at the moment, you
need to do this manually by destroying and recreating the database. Please refer
to the TKP manual on how to recreate a TKP database. When you recreate the
database manually you should run tkp-manage.py initdb again without the -d
flag.
"""
    sys.stderr.write(msg)
    sys.exit(1)


def destroy(dbconfig):
    """
    Destroys the content of a database defined by settings in dbconfig dict.

    !! WARNING !! DESTROYS ALL CONTENT

    args:
        dbconfig: a dict containing connection params for database
    """
    assert(dbconfig['destroy'])
    if dbconfig['engine'] == 'postgresql':
        connection = connect(dbconfig)
        destroy_postgres(connection)
    elif dbconfig['engine'] == 'monetdb':
        destroy_monetdb()


def set_monetdb_schema(cur, dbconfig):
    """
    create custom schema. use with MonetDB only.
    """
    schema_query = """
CREATE SCHEMA "%(database)s" AUTHORIZATION "%(user)s";
ALTER USER "%(user)s" SET SCHEMA "%(database)s";
"""
    print schema_query % dbconfig
    cur.execute(schema_query % dbconfig)


def populate(dbconfig):
    """
    Populates a database with TRAP tables.

    args:
        dbconfig: a dict containing db connection settings

    raises an exception when one of the tables already exists.
    """

    if not dbconfig['yes']:
        verify(dbconfig)

    if dbconfig['destroy']:
        destroy(dbconfig)

    conn = connect(dbconfig)
    cur = conn.cursor()

    if dbconfig['engine'] == 'postgresql':
        # make sure plpgsql is enabled
        try:
            cur.execute("CREATE LANGUAGE plpgsql;")
        except conn.ProgrammingError:
            conn.rollback()
    if dbconfig['engine'] == 'monetdb':
        set_monetdb_schema(cur, dbconfig)
        # reconnect to switch to schema
        conn.close()
        conn = connect(dbconfig)
        cur = conn.cursor()

    batch_file = os.path.join(sql_repo, 'batch')

    error = "\nproblem processing \"%s\".\nMaybe the DB is already populated. "\
            "Try -d/--destroy argument for initdb cmd.\n\n"

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
                sys.stderr.write(error % sql_file)
                raise
    if dbconfig['engine'] == 'postgresql':
        conn.commit()
    conn.close()
