"""
A collection of generic functions used to generate SQL queries
and return data in an easy to use format such as dictionaries.
"""
import logging
import tkp.db


logger = logging.getLogger(__name__)


def columns_from_table(table, keywords=None, alias=None, where=None,
                       order=None):
    """Obtain specific column (keywords) values from 'table', with
    kwargs limitations.

    A very simple helper function, that builds an SQL query to obtain
    the specified columns from 'table', and then executes that
    query. Optionally, the WHERE clause can be specified using the
    where dictionary. It returns a list of a
    dict (with the originally supplied keywords as dictionary keys),
    which can be empty.

    Example:

        >>> columns_from_table('image', \
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
                    
        order (string): ORDER BY key.

    Returns:

        list: list of dicts. Each dict contains the given keywords,
            or all if keywords=None. Each element of the list
            corresponds to a table row.

    """
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
    if order:
        query += " ORDER BY " + order

    cursor = tkp.db.execute(query, where_args)
    results = cursor.fetchall()
    results_dict = convert_db_rows_to_dicts(results, cursor.description, alias)
    return results_dict


def convert_db_rows_to_dicts(results, cursor_description, alias_map=None):
    """Takes a list of rows as returned by cursor.fetchall(),
        converts to a list of dictionaries."""
    col_names = [d[0] for d in cursor_description]
    if alias_map is not None:  # Replace column names with chosen alias
        for index, k in enumerate(col_names):
            if k in alias_map:
                col_names[index] = alias_map[k]
    #NB enumerate generates only one loop
    #so store it in a list!
    col_index = [(i, c) for i, c in enumerate(col_names)]
    result_dicts = []
    for row in results:
        rd = dict((keyword, row[index])
                        for index, keyword in col_index)
        result_dicts.append(rd)
    return result_dicts


def get_db_rows_as_dicts(cursor, alias_map=None):
    """Grab results of cursor.fetchall(), convert to a list of dictionaries."""
    return convert_db_rows_to_dicts(cursor.fetchall(), cursor.description,
                                    alias_map)



def set_columns_for_table(table, data=None, where=None):
    """Set specific columns (keywords) for 'table', with 'where'
    limitations.

    A simple helper function, that builds an SQL query to update the
    specified columns given by data for 'table', and then executes
    that query. Optionally, the WHERE clause can be specified using
    the 'where' dictionary.

    The data argument is a dictionary with the names and corresponding
    values of the columns that need to be updated.
    """
    query = "UPDATE " + table + " SET " + ", ".join(["%s=%%s" % key for key in data.iterkeys()])
    if where is None:
        where = {}
    where_args = tuple(where.itervalues())
    where = " AND ".join(["%s=%%s" % key for key in where.iterkeys()])
    values = tuple(data.itervalues())
    if where:
        query += " WHERE " + where

    tkp.db.execute(query, values + where_args, commit=True)
