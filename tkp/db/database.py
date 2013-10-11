import logging
import tkp.config

logger = logging.getLogger(__name__)

# The version of the TKP DB schema which is assumed by the current tree.
# Increment whenever the schema changes.
DB_VERSION = 16


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
            kwargs = tkp.config.database_config()

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
        # See issue 4778
        # https://support.astron.nl/lofar_issuetracker/issues/4778
        self._UnicornError = None

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
            error = "Database version incompatibility (needed %d, got %d)" % (DB_VERSION, schema_version)
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

    @property
    def UnicornError(self):
        if self._UnicornError is None:
            if self.engine == 'monetdb':
                import monetdb.exceptions
                self._UnicornError = monetdb.exceptions.OperationalError
            elif self.engine == 'postgresql':
                import psycopg2
                self._UnicornError = psycopg2.IntegrityError
        return self._UnicornError
