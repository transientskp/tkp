import exceptions
import logging
import numpy
import tkp.config
from tkp.utility import substitute_inf

logger = logging.getLogger(__name__)

# The version of the TKP DB schema which is assumed by the current tree.
# Increment whenever the schema changes.
DB_VERSION = 27

class DBExceptions(object):
    """
    This provides an engine-agnostic wrapper around the exceptions that can
    the thrown by the database layer: we can refer to eg
    DBExcetions(engine).Error rather than <engine specific module>.Error.

    We handle both the PEP-0249 exceptions as provided by the DB engine, and
    add our own as necessary.
    """
    def __init__(self, engine):
        # RhombusError refers to unhandled source layout, See issue 4778:
        # https://support.astron.nl/lofar_issuetracker/issues/4778
        if engine == "monetdb":
            import monetdb.exceptions
            self.exceptions = monetdb.exceptions
            self.RhombusError = self.exceptions.OperationalError
        elif engine == "postgresql":
            import psycopg2
            self.exceptions = psycopg2
            self.RhombusError = self.exceptions.IntegrityError

    def __getattr__(self, attrname):
        obj = getattr(self.exceptions, attrname)
        # Weed the cluttered psycopg2 namespace: only return things that
        # really are valid database errors.
        if isinstance(obj, type) and issubclass(obj, exceptions.StandardError):
            return obj
        else:
            raise AttributeError(attrname)


def sanitize_db_inputs(params):
    """
    Replace values in params with alternatives suitable for database insertion.

    That includes:

        * Convert numpy.floating types into Python floats;
        * Convert infs into the string "Infinity".

    Args:
        params (dict/list/tuple): (Potentially) dirty database inputs

    Returns:
        cleaned (dict/list/tuple): Sanitized database inputs
    """
    def sanitize(val):
        val = substitute_inf(val)
        if isinstance(val, numpy.floating):
            val = float(val)
        return val

    # According to the DB-API, params could be a dict-alike (ie, has key-value
    # pairs) or a list-alike (an ordered sequence).
    if hasattr(params, "iteritems"):
        cleaned = {k: sanitize(v) for k, v in params.iteritems()}
    else:
        cleaned = [sanitize(v) for v in params]

    return cleaned


class Database(object):
    """
    An object representing a database connection.
    """
    _connection = None
    _configured = False

    # this makes this class a singleton
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if self._configured:
            if kwargs: logger.warning("Not configuring pre-configured database")
            return
        elif not kwargs:
            kwargs = tkp.config.get_database_config()

        self.engine = kwargs['engine']
        self.database = kwargs['database']
        self.user = kwargs['user']
        self.password = kwargs['password']
        self.host = kwargs['host']
        self.port = kwargs['port']
        logger.info("Database config: %s://%s@%s:%s/%s" % (self.engine,
                                                           self.user,
                                                           self.host,
                                                           self.port,
                                                           self.database))
        self._configured = True
        # Provide placeholders for engine-specific Exception classes
        self.exceptions = DBExceptions(self.engine)

    def connect(self):
        """
        connect to the configured database
        """
        logger.info("connecting to database...")

        kwargs = {}
        if self.user:
            kwargs['user'] = self.user
        if self.host:
            kwargs['host'] = self.host
        if self.database:
            kwargs['database'] = self.database
        if self.password:
            kwargs['password'] = self.password
        if self.port:
            kwargs['port'] = int(self.port)

        # During pipeline operation, we force autocommit to off (which should
        # be the default according to the DB-API specs). See #4885.
        if self.engine == 'monetdb':
            import monetdb.sql
            kwargs['autocommit'] = False
            self._connection = monetdb.sql.connect(**kwargs)
        elif self.engine == 'postgresql':
            import psycopg2
            self._connection = psycopg2.connect(**kwargs)
            self._connection.autocommit = False
        else:
            msg = "engine %s not supported " % self.engine
            logger.error(msg)
            raise NotImplementedError(msg)

        # Check that our database revision matches that expected by the
        # codebase.
        cursor = self.connection.cursor()
        cursor.execute("SELECT value FROM version WHERE name='revision'")
        schema_version = cursor.fetchone()[0]
        if schema_version != DB_VERSION:
            error = ("Database version incompatibility (needed %d, got %d)" %
                        (DB_VERSION, schema_version))
            logger.error(error)
            self._connection.close()
            self._connection = None
            raise Exception(error)

        # I don't like this but it is used in some parts of TKP
        self.cursor = self._connection.cursor()

        logger.info("connected to: %s://%s@%s:%s/%s" % (self.engine,
                                                           self.user,
                                                           self.host,
                                                           self.port,
                                                           self.database))


    @property
    def connection(self):
        """
        The database connection, will be created if it doesn't exists.

        This is a property to be backwards compatible with the rest of TKP.

        :return: a database connection
        """
        if not self._connection:
            self.connect()

        # I don't like this but it is used in some parts of TKP
        self.cursor = self._connection.cursor()

        return self._connection

    def close(self):
        """
        close the connection if open
        """
        if self._connection:
            self._connection.close()
        self._connection = None
