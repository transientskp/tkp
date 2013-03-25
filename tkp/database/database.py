"""
Interface with the MonetDB pipeline database.
"""

import logging
from tkp.config import config
from ..utility.exceptions import TKPDataBaseError

logger = logging.getLogger(__name__)

# Set up the Python DB API.
# Record which module was imported as the engine via the ENGINE global.
# port = 0 is a flag to use the default port instead
ENGINE = config['database']['engine']
if ENGINE == 'monetdb':
    import monetdb.sql as engine
    if config['database']['port'] == 0:
        config['database']['port'] = 50000
elif ENGINE == 'postgresql':
    config['database']['autocommit'] = False  # PostgreSQL does not have autocommit
    import psycopg2 as engine
    if config['database']['port'] == 0:
        config['database']['port'] = 5432
else:
    raise TypeError("unknown engine %s" % config['database']['engine'])



class DataBase(object):
    """An object representing a database connection

    This object only represents the database; it takes care of the
    login procedure etc, but doesn't care about the actual contents of
    the database, such as the tables.

    It keeps a a connection object and a cursor object around as well,
    which can readily be accessed. Usage example:

    >>> # Make a database connection using the TKP configuration defaults
    >>> db = DataBase()
    >>> # Now make a different connection
    >>> db = DataBase(host, name, user, password)
    >>> db
    <tkp.database.database.DataBase object at 0x1004959d0>
    >>> db.connection
    <monetdb.sql.connections.Connection instance at 0x10149a5f0>
    >>> db.cursor
    <monetdb.sql.cursors.Cursor instance at 0x10149a710>

    (Note: this example is not doctest compatible.)
    """

    # Assign this class variable for convenience
    Error = engine.Error

    # this makes this class a singleton
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self, host=None, name=None, user=None,
                 password=None, port=None,
                 autocommit=None):
        """Set up a database connection object

        Raises an exception if not enabled.

        Use login defaults from the config module, but the user can
        override these.
        """
        #Dynamically load defaults from config file.
        if host == None:
            host = config['database']['host']
        if user == None:
            user = config['database']['user']
        if password == None:
            password = config['database']['password']
        if name == None:
            name = config['database']['name']
        if port == None:
            port = config['database']['port']
        if autocommit == None:
            autocommit = config['database']['autocommit']
        if ENGINE == 'postgresql':
            autocommit = False
        
        self.host = host
        self.name = name
        self.user = user
        self.password = password
        self.port = port
        self.autocommit = autocommit
        self.connection = None
        if not config['database']['enabled']:
            raise TKPDataBaseError("Database is not enabled")
        self.connect()

    def __str__(self):
        return "Database '%s' @ '%s' for user '%s'" % (
            self.name, self.host, self.user)

    def __repr__(self):
        return ("DataBase(host=%s, name=%s, user=%s, password=%s, port=%d, "
                "autocommit=%s)" % (self.host, self.name, self.user,
                self.password, self.port, self.autocommit))

    def connect(self, host=None, name=None, user=None, password=None,
                port=None, autocommit=None):
        """Connect to the database.

        For any keyword value that is not given (None), the value from
        the corresponding self attributes is used. These attribute
        values are set *only* through __init__, not with connect()
        (though they can, temporariliy, be overriden in connect().
        """

        # This could probably be done using a loop with fancy __getattribute__
        # calls, locals() etc, but that would overly complicate things
        # Or we should use **kwargs in the function declaration above instead,
        # since we can't set the default values using self
        kwargs = {}
        kwargs['host'] = host if host else self.host
        kwargs['database'] = name if name else self.name
        kwargs['user'] = user if user else self.user
        kwargs['password'] = password if password else self.password
        kwargs['port'] = port if port else self.port
        kwargs['autocommit'] = autocommit if autocommit else self.autocommit
        if ENGINE == 'postgresql':  # PostgreSQL doesn't have autocommit
            assert kwargs['autocommit'] is False 
        self.connection = engine.connect(**kwargs)
        self.cursor = self.connection.cursor()
        
    def commit(self):
        """Shortcut to self.connection.commit"""

        return self.connection.commit()

    def execute(self, *args):
        """Shortcut to self.cursor.execute
        
        This function's list of arguments consist of the actual SQL
        query plus the arguments fed into that SQL query.  For a
        single argument, this is only the SQL query. Note that the
        extra arguments are passed separately and not inside a tuple.
        They are put together in a tuple by ethis function and then
        passed into the cursor.execute() function.

        Examples:

            DataBase().execute("SELECT COUNT(*) FROM images")

            DataBase().execute(
                "SELECT image_id, url FROM images WHERE dataset = %s",
                11)
        """

        query = args[0]
        q_args = tuple(args[1:]) if len(args) > 1 else None
        try:
            if q_args is not None:
                self.cursor.execute(query, q_args)
            else:
                self.cursor.execute(query)
        except engine.Error:
            if q_args:
                query = query % q_args
            logger.warn("Failed for query %s", query)
            raise

    def fetchall(self):
        """Shortcut to self.cursor.fetchall"""

        return self.cursor.fetchall()

    def fetchone(self):
        """Shortcut to self.cursor.fetchone"""

        return self.cursor.fetchone()
    
    def get(self, *args):
        """Execute() and fetchall() in one

        Not always recommend, since it may obscure errors,
        or execution of the process overall.

        For details on usage, see the execute() documentation.
        """

        self.execute(*args)
        return self.cursor.fetchall()
    
    def getone(self, *args):
        """Execute() and fetchone() in one

        Not always recommend, since it may obscure errors,
        or execution of the process overall.

        For details on usage, see the execute() documentation.
        """

        self.execute(*args)
        return self.cursor.fetchone()
    
    def tables(self):
        """Return a list of tables in the database"""

        query = """SELECT * FROM sys.tables WHERE system = FALSE"""
        tables = self.get(query)
        return [table[0] for table in tables]

    def close(self):
        """Explicitly close the database connection"""

        self.connection.close()
