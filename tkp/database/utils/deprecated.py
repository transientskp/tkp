"""
SQL subroutines which look like they might come in handy,
but are not currently in use

"""
import logging
import monetdb.sql as db
from tkp.config import config

logger = logging.getLogger(__name__)

AUTOCOMMIT = config['database']['autocommit']
DERUITER_R = config['source_association']['deruiter_radius']
BG_DENSITY = config['source_association']['bg-density']


def select_single_epoch_detection(conn, dsid):
    """Select sources from running catalog which have only one detection
    
        NB: Deprecated. 
        -This has not been tested since the schema update,
         as it's not actually used anywhere currently.
            
    """

    results = []
    cursor = conn.cursor()
    try:
        query = """\
SELECT runcat
      ,dataset
      ,datapoints
      ,wm_ra
      ,wm_decl
      ,wm_ra_err
      ,wm_decl_err
      ,sqrt(datapoints*(avg_I_peak_sq - avg_I_peak*avg_I_peak) /
            (datapoints-1)) / avg_I_peak as V
      ,(datapoints/(datapoints-1)) *
       (avg_weighted_I_peak_sq -
        avg_weighted_I_peak * avg_weighted_I_peak / avg_weight_peak)
       as eta
  FROM runningcatalog
 WHERE dataset = %s
   AND datapoints = 1
"""
        cursor.execute(query, (dsid, ))
        results = cursor.fetchall()
        results = [dict(srcid=x[0], npoints=x[2], v_nu=x[7], eta_nu=x[8])
                   for x in results]
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error:
        logger.warn("Failed on query %s", query)
        raise
    finally:
        cursor.close()
    return results


# To do: move these two functions to unit tests
# Are these being used anyway? They appear to be defined, but not used
def concurrency_test_fixedalpha(conn):
    """Unit test function to test concurrency
    """

    theta = 0.025
    decl = 80.
    alpha = None
    try:
        cursor = conn.cursor()
        query = """\
        SELECT alpha(%s, %s)
        """
        cursor.execute(query, (theta, decl))
        alpha = cursor.fetchone()[0]
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error, e:
        logger.warn("Query failed: %s." % query)
        raise
    finally:
        conn.cursor().close()
    return alpha


def concurrency_test_randomalpha(conn):
    """Unit test function to test concuurency
    """

    import random
    theta = 0.025
    decl = random.random() * 90
    alpha = None
    try:
        cursor = conn.cursor()
        query = """\
        SELECT alpha(%s, %s)
        """
        cursor.execute(query, (theta, decl))
        alpha = cursor.fetchone()[0]
    except db.Error, e:
        logger.warn("Query failed: %s." % query)
        raise
    finally:
        conn.cursor().close()
    return alpha