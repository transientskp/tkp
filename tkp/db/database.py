
import logging
import numpy
import tkp.config
from tkp.utility import substitute_inf
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


logger = logging.getLogger(__name__)

# The version of the TKP DB schema which is assumed by the current tree.
# Increment whenever the schema changes.
DB_VERSION = 35



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
    transaction = None
    cursor = None

    # this makes this class a singleton
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        if self._configured:
            if kwargs:
                logger.warning("Not configuring pre-configured database")
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

        self.alchemy_engine = create_engine('%s://%s:%s@%s:%s/%s' %
                                            (self.engine,
                                             self.user,
                                             self.password,
                                             self.host,
                                             self.port,
                                             self.database),
                                            echo=False
                                            )
        self.Session = sessionmaker(bind=self.alchemy_engine)

    def connect(self, check=False):
        """
        connect to the configured database

        args:
            check (bool): check if schema version is correct
        """
        logger.info("connecting to database...")

        self._connection = self.alchemy_engine.connect()
        self._connection.execution_options(autocommit=False)

        if check:
            # Check that our database revision matches that expected by the
            # codebase.
            q = "SELECT value FROM version WHERE name='revision'"
            cursor = self.connection.execute(q)
            schema_version = cursor.fetchone()[0]
            if schema_version != DB_VERSION:
                error = ("Database version incompatibility (needed %d, got %d)" %
                         (DB_VERSION, schema_version))
                logger.error(error)
                self._connection.close()
                self._connection = None
                raise Exception(error)

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

        self.cursor = self._connection.connection.cursor()

        return self._connection

    def close(self):
        """
        close the connection if open
        """
        if self._connection:
            self._connection.close()
        self._connection = None

    def vacuum(self, table):
        """
        Force a vacuum on a table, which removes dead rows. (Postgres only)

        Normally the auto vacuum process does this for you, but in some cases
        (for example when the table receives many insert and deletes)  manual
        vacuuming is necessary for performance reasons.

        args:
            table: name of the table in the database you want to vacuum
        """

        if self.engine != "postgresql":
            return

        from psycopg2.extensions import (ISOLATION_LEVEL_AUTOCOMMIT,
                                            ISOLATION_LEVEL_READ_COMMITTED)

        # disable autocommit since can't vacuum in transaction
        self.connection.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = self.connection.connection.cursor()
        cursor.execute("VACUUM ANALYZE %s" % table)
        # reset settings
        self.connection.connection.set_isolation_level(ISOLATION_LEVEL_READ_COMMITTED)

    def execute(self, query, parameters={}, commit=False):
        if commit:
           self.transaction = self.connection.begin()

        try:
            cursor = self.connection.execute(query, parameters)
            if commit:
                self.transaction.commit()
            return cursor
        except Exception as e:
            logger.error("Query failed: %s. Query: %s." % (e, query % parameters))
            raise

    def rollback(self):
        if self.transaction:
            self.transaction.rollback()

    def reconnect(self):
        self._connection.close()
        self.connect()

