import logging
import monetdb.sql
from tkp.database.database import DataBase

#TODO: this should really be removed, other modules should import this directly
from tkp.database.orm import DataSet, Image, ExtractedSource

from tkp.config import config
autocommit = config['database']['autocommit']

logger = logging.getLogger(__name__)

def query(query, parameters=None, commit=False):
    """A generic wrapper for doing any query to the database
    Args:
        conn: the database connection object
        query: the query string
        commit: should a commit be performed afterwards
    returns:
        a MonetDB cursor object
    """
    try:
        database = DataBase()
        connection = database.connection
        cursor = connection.cursor()
        cursor.execute(query, parameters)
        if not autocommit and commit:
            connection.commit()
    except monetdb.sql.Error as e:
        logger.error("Query failed: %s. Query: %s." % (e, query))
        raise
    return cursor
