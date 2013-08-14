
"""
A collection of back end db query subroutines used for unittesting
"""
from math import sqrt
from collections import namedtuple
from tkp.db import execute
from tkp.testutil.db_subs import example_extractedsource_tuple

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

Position = namedtuple("Position",  # Everything in degrees
                            ['ra', 'dec' ,  # In degrees
                             'ra_err' , 'dec_err' ,  # In degrees
                             ])

def extractedsource_to_position(ex):
    """NB worth having a separate data structure,
    since extractedsource is used in the real world, whereas positiontuple
    is purely for testing and hence can be kept simple, resulting in unit
    tests which are easier to understand.
    
    We just have to carefully make the conversion here.
    """
    return Position(ra=ex.ra, dec=ex.dec, 
             ra_err=sqrt(ex.ra_fit_err ** 2 + (ex.ra_sys_err / 3600.) ** 2),
             dec_err=sqrt(ex.dec_fit_err ** 2 + (ex.dec_sys_err / 3600.) ** 2))

def position_to_extractedsource(posn):
    p = posn
    return example_extractedsource_tuple(ra=p.ra, dec=p.ra,
                         ra_fit_err=p.ra_err, dec_fit_err=p.dec_err,
                         ra_sys_err=0, dec_sys_err=0)


def deruiter(connection, pos1, pos2, cross_meridian):
    """pos1,2 should be of type ``Position``"""
#     if cross_meridian:
#         qry = """SELECT deruiter_meridian(%(ra1)s,%(dec1)s,%(ra1_err)s,%(dec1_err)s,
#                                 %(ra2)s,%(dec2)s,%(ra2_err)s,%(dec2_err)s)"""
#     else:
    qry = """SELECT deruiter(%(ra1)s,%(dec1)s,%(ra1_err)s,%(dec1_err)s,
                            %(ra2)s,%(dec2)s,%(ra2_err)s,%(dec2_err)s,
                            %(xmerid)s)"""
    qry_args = {'ra1':pos1.ra, 'dec1':pos1.dec,
                'ra1_err':pos1.ra_err, 'dec1_err':pos1.dec_err,
                'ra2':pos2.ra, 'dec2':pos2.dec,
                'ra2_err':pos2.ra_err, 'dec2_err':pos2.dec_err,
                'xmerid':cross_meridian
                }
    curs = connection.cursor()
    curs.execute(qry, qry_args)
    return curs.fetchone()[0]

