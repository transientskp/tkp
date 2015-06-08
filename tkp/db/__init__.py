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
    database = Database()
    return database.execute(query, parameters=parameters, commit=commit)


def rollback():
    database = Database()
    return database.rollback()
