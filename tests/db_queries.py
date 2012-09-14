# LOFAR Transients Key Project
#
# Bart Scheers, Evert Rol, Tim Staley 
#
# discovery@transientskp.org
#

"""
A collection of back end db query subroutines used for unittesting 

"""

import logging
import monetdb.sql as db
from tkp.config import config

def count_runcat_entries(conn, dataset):
    """Count the number of runningcatalog sources
    for a specific dataset
    """

    try:
        cursor = conn.cursor()
        query = """\
        SELECT COUNT(*) 
          FROM runningcatalog 
         WHERE dataset = %s
        """
        cursor.execute(query, (dataset,))
        runcat_count = cursor.fetchall()
        if not config['database']['autocommit']:
            conn.commit()
        cursor.close()
    except db.Error, e:
        logging.warn("Failed on query: %s" % query)
        raise
    return runcat_count

def count_associated_sources(conn, dataset):
    """Count the number of associations for runningcatalog sources
    for a specific dataset
    """

    try:
        cursor = conn.cursor()
        query = """\
        SELECT runcat
              ,COUNT(*) 
          FROM assocxtrsource 
         WHERE runcat IN (SELECT id 
                            FROM runningcatalog 
                           WHERE dataset = %s
                         ) 
        GROUP BY runcat 
        ORDER BY runcat
        """
        cursor.execute(query, (dataset,))
        id_counts = cursor.fetchall()
        if not config['database']['autocommit']:
            conn.commit()
        cursor.close()
    except db.Error, e:
        logging.warn("Failed on query: %s" % query)
        raise
    return id_counts

