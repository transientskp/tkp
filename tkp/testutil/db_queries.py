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
from tkp.database import query

def count_runcat_entries(conn, dataset):
    """Count the number of runningcatalog sources
    for a specific dataset
    
    Returns an integer.
    """

    try:
        cursor = conn.cursor()
        query = """\
        SELECT COUNT(*) 
          FROM runningcatalog 
         WHERE dataset = %s
        """
        cursor.execute(query, (dataset,))
        runcat_count = cursor.fetchall()[0][0]
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
    
    Returns: A list of pairwise tuples,
         [ (assoc_src_id, assocs_count) ]
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


def dataset_images(dataset_id, database=None):
    q = "SELECT id FROM image WHERE dataset=%(dataset)s LIMIT 1"
    args = {'dataset': dataset_id}
    cursor = query(q, args)
    image_ids = [x[0] for x in cursor.fetchall()]
    return image_ids

def convert_to_cartesian(conn, ra, decl):
    """Returns tuple (x,y,z)"""
    qry = """SELECT x,y,z FROM cartesian(%s, %s)"""
    curs = conn.cursor()
    curs.execute(qry, (ra, decl))
    return curs.fetchone()


