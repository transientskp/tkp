"""
Dump database schema and content
"""
import logging
import subprocess
import tempfile
import os

logger = logging.getLogger(__name__)

def dump_db(engine, hostname, port, dbname, dbuser, dbpass, output):
    """
    Dumps a database

    Args:
        engine: the name of the database system (either postgresql)
        hostname: the hostname of the database
        port: the port of the database server
        dbname: the database name to be dumped
        dbuser: the user authorised to do the dump
        dbpass: the pw for the user
        output: the output file to which the dump is written
    """
    if engine == "postgresql":
        return dump_pg(hostname, port, dbname, dbuser, dbpass, output)
    else:
        raise NotImplementedError("Not able to dump %s" % (engine,))


def dump_pg(hostname, port, dbname, dbuser, dbpass, output_filename):
    """
    Dumps a PostgreSQL database in specified output file
    """
    pg_dump_executable = "pg_dump"

    try:
        env = os.environ
        env["PGPASSWORD"]= dbpass
        subprocess.check_call(
            [
                pg_dump_executable,
                "-h", hostname,
                "-p", str(port),
                "-U", dbuser,
                "-f", output_filename,
                dbname
            ],
            env=env
        )
    except Exception as e:
        logger.error("Failed to dump: %s" % (e,))
        raise
