#
# LOFAR Transients Key Project
#
# Interface with the pipeline databases.
#

import logging
import contextlib
import monetdb
import monetdb.sql
from tkp.config import config
from ..utility.exceptions import TKPDataBaseError


ENABLED = config['database']['enabled']
HOST = config['database']['host']
USER = config['database']['user']
PASSWORD = config['database']['password']
NAME = config['database']['name']
PORT = config['database']['port']


class DataBase(object):
    """An object representing a database connection

    This object only represents the database; it takes care of the
    login procedure etc, but doesn't care about the actual contents of
    the database, such as the tables.

    It keeps a a connection object and a cursor object around as well,
    which can readily be accessed. Usage example:

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
    Error = monetdb.sql.Error

    def __init__(self, host=HOST, name=NAME, user=USER,
                 password=PASSWORD, port=PORT):
        """Set up a database connection object

        Raises an exception if not enabled.

        Use defaults from the config module, but the user can override these
        """
        self.host = host
        self.name = name
        self.user = user
        self.password = password
        self.port = port
        self.connection = None
        if not ENABLED:
            raise TKPDataBaseError("Database is not enabled")
        self.connect()

    def __del__(self):
        self.close()

    def __str__(self):
        return "Database '%s' @ '%s' for user '%s'" % (
            self.name, self.host, self.user)

    def __repr__(self):
        return "DataBase(host=%s, name=%s, user=%s, password=%s, port=%d" % (
            self.host, self.name, self.user, self.password, self.port)

    def connect(self):
        """Connect to the database"""
        
        print "self.host =", self.host
        print "self.user =", self.user
        print "self.password =", self.password
        print "self.name =", self.name
        print "self.port =", self.port
        self.connection = monetdb.sql.connect(
            hostname=self.host, username=self.user, password=self.password,
            database=self.name, port=self.port)
        self.cursor = self.connection.cursor()

    def commit(self):
        """Shortcut to self.connection.commit"""

        return self.connection.commit()

    def execute(self, *args):
        """Shortcut to self.cursor.execute"""

        return self.cursor.execute(*args)
    
    def close(self):
        """Explicitly close the database connection"""

        try:
            self.connection.close()
        except monetdb.monetdb_exceptions.Error:
            pass
        except AttributeError:
            pass
