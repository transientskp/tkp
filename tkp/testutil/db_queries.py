
"""
A collection of back end db query subroutines used for unittesting 
"""
from tkp.db import execute


def dataset_images(dataset_id, database=None):
    q = "SELECT id FROM image WHERE dataset=%(dataset)s LIMIT 1"
    args = {'dataset': dataset_id}
    cursor = execute(q, args)
    image_ids = [x[0] for x in cursor.fetchall()]
    return image_ids


def convert_to_cartesian(conn, ra, decl):
    """Returns tuple (x,y,z)"""
    qry = """SELECT x,y,z FROM cartesian(%s, %s)"""
    curs = conn.cursor()
    curs.execute(qry, (ra, decl))
    return curs.fetchone()


