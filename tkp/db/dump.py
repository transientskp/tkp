import logging
import subprocess
import tempfile
import os

logger = logging.getLogger(__name__)

def dump_db(engine, hostname, port, dbname, dbuser, dbpass, output):
    if engine == "monetdb":
        return dump_monetdb(hostname, port, dbname, dbuser, dbpass, output)
    elif engine == "postgresql":
        return dump_pg(hostname, port, dbname, dbuser, dbpass, output)
    else:
        raise NotImplementedError("Not able to dump %s" % (engine,))

def dump_monetdb(hostname, port, dbname, dbuser, dbpass, output_filename):
    mclient_executable = "mclient"

    with tempfile.NamedTemporaryFile() as dotmonetdb, \
        open(output_filename, 'w') as output_file:

        # NB we need to write *both* user and password into the dotmonetdb
        # file: writing just the password will fail.
        dotmonetdb.write("user=%s\n" % (dbuser,))
        dotmonetdb.write("password=%s\n" % (dbpass,))
        dotmonetdb.flush()

        try:
            env = os.environ
            env["DOTMONETDBFILE"]= dotmonetdb.name
            subprocess.check_call(
                [
                    mclient_executable,
                    "-h", hostname,
                    "-p", str(port),
                    "-d", dbname,
                    "--dump"
                ],
                env=env,
                stdout=output_file
            )
        except Exception, e:
            logger.error("Failed to dump: %s" % (e,))
            raise

def dump_pg(hostname, port, dbname, dbuser, dbpass, output_filename):
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
    except Exception, e:
        logger.error("Failed to dump: %s" % (e,))
        raise
