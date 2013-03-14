import logging
import monetdb.sql
from tkp.database.database import Database
from tkp.database.orm import DataSet, Image, ExtractedSource


logger = logging.getLogger(__name__)


def query(query, parameters=(), commit=False):
    """
    A generic wrapper for doing any query to the database

    :param query: the query string
    :param commit: should a commit be performed afterwards

    :returns: a database cursor object
    """
    database = Database()
    cursor = database.connection.cursor()
    try:
        cursor.execute(query, parameters)
        if commit:
            database.connection.commit()
    except monetdb.sql.Error as e:
        logger.error("Query failed: %s. Query: %s." % (e, query % parameters))
        raise
    return cursor


def configure(*args, **kwargs):
    database = Database()
    return database.configure(*args, **kwargs)


def commit():
    database = Database()
    return database.connection.commit()

def rollback():
    database = Database()
    return database.connection.rollback()

def connect():
    database = Database()
    return database.connect()