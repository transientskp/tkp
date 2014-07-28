import logging
import numpy
from tkp.db.database import Database
from tkp.db.orm import DataSet, Image, ExtractedSource
from tkp.utility import substitute_inf

logger = logging.getLogger(__name__)

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

def execute(query, parameters={}, commit=False):
    """
    A generic wrapper for doing any query to the database

    :param query: the query string
    :param parameters: The query parameters. These will be converted and escaped.
    :param commit: should a commit be performed afterwards, boolean

    :returns: a database cursor object
    """
    #logger.info('executing query\n%s' % query % parameters)
    database = Database()
    cursor = database.connection.cursor()
    try:
        cursor.execute(query, sanitize_db_inputs(parameters))
        if commit:
            database.connection.commit()
    except database.connection.Error as e:
        logger.error("Query failed: %s. Query: %s." % (e, query % parameters))
        raise
    except Exception as e:
        logger.error("Big problem here: %s" % e)
        raise
    return cursor

def commit():
    database = Database()
    return database.connection.commit()

def rollback():
    database = Database()
    return database.connection.rollback()

def connect():
    database = Database()
    return database.connect()

def connection():
    database = Database()
    return database.connection
