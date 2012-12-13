import logging
import monetdb.sql
from .database import DataBase
from .orm import DataSet
from .orm import Image
from .orm import ExtractedSource

import quality

from tkp.config import config
autocommit = config['database']['autocommit']

logger = logging.getLogger(__name__)

def query(conn, query, parameters=None, commit=False):
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
        cursor.execute(query, parameters)
        if not autocommit and commit:
            conn.commit()
    except monetdb.sql.Error as e:
        logger.error("Query failed: %s. Query: %s." % (e, query))
        raise
    return cursor
