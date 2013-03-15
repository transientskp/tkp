"""
All code required for interacting with the database
"""

import logging
import os

logger = logging.getLogger(__name__)

# defaults settings
defaults = {
    'engine': 'monetdb',
    'database': 'trap',
    'username': 'trap',
    'password': 'trap',
    'hostname': 'localhost',
    'port': 50000,
}

class Database(object):
    """
    An object representing a database connection.
    """
    engine = None
    database = None
    username = None
    password = None
    autocommit = False

    _connection = None

    # this makes this class a singleton
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls)
            cls._instance.configure()
        return cls._instance

    def configure(self, engine=None, database=None, username=None,
                  password=None, hostname=None, port=None):
        """
        Configures the database with the given parameters.

        If a parameter is ignored the system environment variables are used::

          * TKP_DBENGINE
          * TKP_DBNAME
          * TKP_DBUSER
          * TKP_DBPASS
          * TKP_DBHOST
          * TKP_DBPORT

        If these are also not set a default set of settings are used.

        """
        e = os.environ
        Database.engine = engine or os.environ.get('TKP_DBENGINE',
                                                   defaults['engine'])
        Database.database = database or os.environ.get('TKP_DBNAME',
                                                       defaults['database'])
        Database.username = username or os.environ.get('TKP_DBUSER',
                                                       defaults['username'])
        Database.password = password or os.environ.get('TKP_DBPASS',
                                                       defaults['password'])
        Database.hostname = hostname or os.environ.get('TKP_DBHOST',
                                                       defaults['hostname'])
        Database.port = port or int(os.environ.get('TKP_DBPORT',
                                                   defaults['port']))

    def connect(self):
        if self.engine == 'monetdb':
            import monetdb.sql
            self._connection = monetdb.sql.connect(username=self.username,
                                                   password=self.password,
                                                   hostname=self.hostname,
                                                   port=self.port,
                                                   database=self.database)
        elif self.engine == 'postgresql':
            import psycopg2
            self._connection = psycopg2.connect(user=self.username,
                                                password=self.password,
                                                host=self.hostname,
                                                port=self.port,
                                                database=self.database)
        else:
            raise NotImplementedError("engine %s not supported " % self.engine)

            # I don't like this but it is used in some parts of TKP
        self.cursor = self._connection.cursor()

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