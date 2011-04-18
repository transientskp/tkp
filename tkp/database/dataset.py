#
# LOFAR Transients Key Project
#
"""
Dataset.

A container for ImageData objects that fall logically together as one
"dataset".
"""

# Python 2.5 only!
from __future__ import with_statement
from contextlib import closing
# Miscellaneous python imports
import logging
# Local stuff
import tkp.database.database as db


class DataSet(list):
    """
    A DataSet is a list of ImageData objects which fall logically together as
    one unit: potentially from the same HDF5 file or similar. They are
    therefore associated by having the same dataset id in the database.

    """
    def __init__(self, name, dbconnection=None, id=None):
        """

        :argument name: Dataset name

        :keyword dbconnection: database connection object

        :keyword id: ID of the dataset in the database. If None, a new
        ID will be created.
        
        """
        self.name = name
        self.dbconnection = dbconnection
        # Database ID placeholder: see the id() method below.
        self._id = id
        # Create an id in the DB if not available
        self.id

    @property
    def id(self):
        """Add a dataset ID to the database
        
        A dataset will be added to the database. A dataset id will be
        generated for every dataset name. If the name already exists the
        rerun value in the table will be incremented by 1. If the database is
        not enabled the id is set to "None".

        The stored function insertDataset() is called. It takes the name as
        input and returns the generated id.
        """

        # Note: put double code in separate function?
        if db.enabled == True and self._id is None:
            if self.dbconnection is not None:
                with closing(self.dbconnection.cursor()) as cursor:
                    try:
                        # MySQL & MonetDB syntax
                        cursor.execute("""SELECT insertDataset(%s)""", (
                            self.name,))
                        self.dbconnection.commit()
                        self._id = cursor.fetchone()[0]
                    except db.Error, e:
                        logging.warn("Insert DataSet %s failed." % (
                            self.name, ))
                        raise
            else:
                with closing(db.connection()) as conn:
                    with closing(conn.cursor()) as cursor:
                        try:
                            # MySQL & MonetDB syntax
                            cursor.execute("""SELECT insertDataset(%s)""", (
                                self.name, ))
                            conn.commit()
                            self._id = cursor.fetchone()[0]
                        except db.Error, e:
                            logging.warn("Insert DataSet %s failed" % (
                                self.name, ))
                            raise
        return self._id

    def __str__(self):
        return "DataSet: %s. Database ID: %s %d items." % (
            self.name, str(self.id), len(self))
