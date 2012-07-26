#
# LOFAR Transients Key Project
#
# Bart Scheers, Evert Rol, Tim Staley
#
# discovery@transientskp.org
#

"""
A collection of generic functions used to generate SQL queries
and return data in an easy to use format such as dictionaries. 
"""

import os
import sys
import math
import logging
import monetdb.sql as db
from tkp.config import config


AUTOCOMMIT = config['database']['autocommit']
DERUITER_R = config['source_association']['deruiter_radius']
BG_DENSITY = config['source_association']['bg-density']


def columns_from_table(conn, table, 
                       keywords=None,
                       alias=None,  
                       where=None):
    """Obtain specific column (keywords) values from 'table', with
    kwargs limitations.

    A very simple helper function, that builds an SQL query to obtain
    the specified columns from 'table', and then executes that
    query. Optionally, the WHERE clause can be specified using the
    where dictionary. It returns a list of a
    dict (with the originally supplied keywords as dictionary keys),
    which can be empty.

    Example:
    
        >>> columns_from_table(conn, 'image',
            keywords=['taustart_ts', 'tau_time', 'freq_eff', 'freq_bw'], where={'imageid': 1})
            [{'freq_eff': 133984375.0, 'taustart_ts': datetime.datetime(2010, 10, 9, 9, 4, 2), 'tau_time': 14400.0, 'freq_bw': 1953125.0}]

        This builds the SQL query:
        "SELECT taustart_ts, tau_time, freq_eff, freq_bw FROM image WHERE imageid=1"

    This function is implemented mainly to abstract and hide the SQL
    functionality from the Python interface.

    Args:

        conn: database connection object

        table (string): database table name

    Kwargs:

        keywords (list): column names to select from the table. None indicates all ('*')

        where (dict): where clause for the query, specified as a set
            of 'key = value' comparisons. Comparisons are and-ed
            together. Obviously, only 'is equal' comparisons are
            possible.
            
        alias (dict): Chosen aliases for the column names, 
                    used when constructing the returned list of dictionaries 

    Returns:

        (list): list of dicts. Each dict contains the given keywords,
            or all if keywords=None. Each element of the list
            corresponds to a table row.
        
    """

    # Note from the Python docs: If items(), keys(), values(),
    # iteritems(), iterkeys(), and itervalues() are called with no
    # intervening modifications to the dictionary, the lists will
    # directly correspond.
    results = []
    if keywords is None:
        query = "SELECT * FROM " + table
    else:
        query = "SELECT " + ", ".join(keywords) + " FROM " + table
    if where is None:
        where = {}
    where_args = tuple(where.itervalues())
    where = " AND ".join(["%s=%%s" % key for key in where.iterkeys()])
    if where:
        query += " WHERE " + where
    try:
        cursor = conn.cursor()
        cursor.execute(query, where_args)
        results = cursor.fetchall()
        if keywords is None:
            keywords = [desc[0] for desc in cursor.description]
        if alias is not None: #Replace column names with chosen alias
            for index, k in enumerate(keywords):
                if k in alias:
                    keywords[index] = alias[k]
        results = [ dict((keyword, value) for keyword, value in zip(keywords, result)) 
                    for result in results ]
    except db.Error, exc:
        query = query % where_args
        logging.warn("Query failed: %s" % query)
        raise
    finally:
        conn.cursor().close()
    return results


def set_columns_for_table(conn, table, data=None, where=None):
    """Set specific columns (keywords) for 'table', with 'where'
    limitations.

    A simple helper function, that builds an SQL query to update the
    specified columns given by data for 'table', and then executes
    that query. Optionally, the WHERE clause can be specified using
    the 'where' dictionary.

    The data argument is a dictionary with the names and corresponding
    values of the columns that need to be updated.
    """

    # Note from the Python docs: If items(), keys(), values(),
    # iteritems(), iterkeys(), and itervalues() are called with no
    # intervening modifications to the dictionary, the lists will
    # directly correspond.
    query = "UPDATE " + table + " SET " + ", ".join(["%s=%%s" % key for key in data.iterkeys()])
    if where is None:
        where = {}
    where_args = tuple(where.itervalues())
    where = " AND ".join(["%s=%%s" % key for key in where.iterkeys()])
    values = tuple(data.itervalues())
    if where:
        query += " WHERE " + where
    try:
        cursor = conn.cursor()
        cursor.execute(query, values + where_args)
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error, e:
        query = query % (values + where_args)
        logging.warn("Query failed: %s", query)
        raise
    finally:
        cursor.close()
