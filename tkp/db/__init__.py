import logging
import numpy
from tkp.db.database import Database, sanitize_db_inputs
from tkp.db.orm import DataSet, Image, ExtractedSource


logger = logging.getLogger(__name__)

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
