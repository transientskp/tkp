"""
All code required for interacting with the database
"""

import logging
import os
import getpass

logger = logging.getLogger(__name__)


class Database(object):
    """
    An object representing a database connection.
    """
    _connection = None

    # this makes this class a singleton
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls)
            cls._instance.configure()
        return cls._instance

    def configure(self, engine=None, database=None, user=None, password=None,
                  host=None, port=None):
        """
        Configures the database with the given parameters.

        If a parameter is not used these system environment variables are
        checked::

          * TKP_DBENGINE
          * TKP_DBNAME
          * TKP_DBUSER
          * TKP_DBPASS
          * TKP_DBHOST
          * TKP_DBPORT

        If these are also not set a default set of settings are used.
        """
        e = os.environ

        # defaults settings
        username = getpass.getuser()
        self.engine = engine or e.get('TKP_DBENGINE', 'monetdb')
        self.database = database or e.get('TKP_DBNAME', username)
        self.user = user or e.get('TKP_DBUSER', username)
        self.password = password or e.get('TKP_DBPASS', username)
        self.host = host or e.get('TKP_DBHOST', False)
        self.port = port or int(e.get('TKP_DBPORT', False))

        logger.info("Database config: %s://%s@%s:%s/%s" % (self.engine,
                                                           self.user,
                                                           self.host,
                                                           self.port,
                                                           self.database))

        # reset connection
        self._connection = False

    def connect(self):
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
            kwargs['port'] = self.port

        if self.engine == 'monetdb':
            import monetdb.sql
            self._connection = monetdb.sql.connect(**kwargs)
        elif self.engine == 'postgresql':
            import psycopg2
            self._connection = psycopg2.connect(**kwargs)
        else:
            msg = "engine %s not supported " % self.engine
            logger.error(msg)
            raise NotImplementedError(msg)

        # I don't like this but it is used in some parts of TKP
        self.cursor = self._connection.cursor()

        logger.info("connected to database %s at %s" % (self.database, self.host))


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
        return self.connection.close()