import logging
import monetdb.sql
from .database import DataBase
from .orm import DataSet
from .orm import Image
from .orm import ExtractedSource

from tkp.config import config
autocommit = config['database']['autocommit']

def query(conn, query, commit=False):
    """A generic wrapper for doing any query to the database
    Args:
        conn: the database connection object
        query: the query string
        commit: should a commit be performed afterwards
    returns:
        a MonetDB cursor object
    """
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        if not autocommit and commit:
            conn.commit()
    except monetdb.sql.Error, e:
        logging.warn("Query failed: %s." % query)
        raise
    return cursor