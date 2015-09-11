
"""
A collection of back end db query subroutines used for unittesting
"""
from tkp.db import execute
from tkp.db.generic import get_db_rows_as_dicts


def dataset_images(dataset_id, database=None):
    q = "SELECT id FROM image WHERE dataset=%(dataset)s LIMIT 1"
    args = {'dataset': dataset_id}
    cursor = execute(q, args)
    image_ids = [x[0] for x in cursor.fetchall()]
    return image_ids


def convert_to_cartesian(conn, ra, decl):
    """Returns tuple (x,y,z)"""
    qry = """SELECT x,y,z FROM cartesian(%s, %s)"""
    curs = conn.connection.cursor()
    curs.execute(qry, (ra, decl))
    return curs.fetchone()

def get_assoc_entries(db, runcat_id):
    """
    Return the full history of variability indices for a runcat entry,
    ordered by time.
    """
    query = """\
    select a.runcat
          ,a.xtrsrc
          ,x.extract_type
          ,i.taustart_ts
          ,a.v_int
          ,a.eta_int
          ,a.f_datapoints
          ,a.type
          ,r.mon_src
      from assocxtrsource a
          ,extractedsource x
          ,image i
          ,runningcatalog r
     where a.xtrsrc = x.id
       and x.image = i.id
       and a.runcat = r.id
       and r.id = %(runcat_id)s
    order by i.taustart_ts
    """
    db.cursor.execute(query, {'runcat_id': runcat_id})
    return get_db_rows_as_dicts(db.cursor)


