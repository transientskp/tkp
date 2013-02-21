"""
A collection of back end subroutines (mostly SQL queries).

This module contains the routines to deal with flagging and monitoring 
of transient candidates, mostly involving the monitoringlist.
"""
import logging
import monetdb.sql as db
from tkp.config import config
from . import general
from tkp.database.database import DataBase
from collections import namedtuple

logger = logging.getLogger(__name__)

MonitorTuple = namedtuple('MonitorTuple', 
                          ('ra', 'decl', 'runcat','monitorid')
                          )

AUTOCOMMIT = config['database']['autocommit']

def get_userdetections(image_id, deRuiter_r, radius=0.03):
    """Returns the monitoringlist user-entry sources for a forced fit
    in the current image
    
    Output: monlist.id, ra, decl
    """
    deRuiter_red = deRuiter_r / 3600.
    try:
        conn = DataBase().connection
        cursor = conn.cursor()
        query = """\
        SELECT m.id
              ,m.ra
              ,m.decl
          FROM monitoringlist m
              ,(SELECT dataset
                  FROM image
                 WHERE id = %s
               ) t
         WHERE m.dataset = t.dataset
           AND m.userentry = TRUE
        """
        cursor.execute(query, (image_id,))
        results = zip(*cursor.fetchall())
        if not AUTOCOMMIT:
            conn.commit()
        cursor.close()
        r = ()
        if len(results) != 0:
            p = zip(list(results[1]), list(results[2]))
            #maxbeam = max(results[3][0],results[4][0]) # all bmaj & bmin are the same
            r = (p,)
    except db.Error, e:
        query = query % (image_id,)
        logger.warn("Query failed:\n%s", query)
        raise
    return r

def get_nulldetections(image_id, deRuiter_r, radius=0.03):
    """Returns the runcat sources that do not have a counterpart in the 
    extractedsources of the current image
    
    We do not have to take into account associations with monitoringlist 
    sources, since they have been added to extractedsources at the beginning 
    of the association procedures (marked as extract_type=1 sources), and so
    they must have an occurence in extractedsource and runcat.
    
    Output: id, ra, decl
    """
    deRuiter_red = deRuiter_r / 3600.
    try:
        #print "\nTrying to find null detections for image_id:", image_id, "\n"
        conn = DataBase().connection
        cursor = conn.cursor()
        query = """\
        SELECT r1.id
              ,r1.wm_ra
              ,r1.wm_decl
          FROM runningcatalog r1
              ,image i1
         WHERE i1.id = %s
           AND i1.dataset = r1.dataset
           AND r1.id NOT IN (SELECT r.id
                               FROM runningcatalog r
                                   ,extractedsource x
                                   ,image i
                              WHERE i.id = %s
                                AND x.image = i.id
                                AND x.image = %s
                                AND i.dataset = r.dataset
                                AND r.zone BETWEEN CAST(FLOOR(x.decl - %s) as INTEGER)
                                               AND CAST(FLOOR(x.decl + %s) as INTEGER)
                                AND r.wm_decl BETWEEN x.decl - %s
                                                  AND x.decl + %s
                                AND r.wm_ra BETWEEN x.ra - alpha(%s, x.decl)
                                                AND x.ra + alpha(%s, x.decl)
                                AND SQRT(  (x.ra * COS(RADIANS(x.decl)) - r.wm_ra * COS(RADIANS(r.wm_decl)))
                                         * (x.ra * COS(RADIANS(x.decl)) - r.wm_ra * COS(RADIANS(r.wm_decl)))
                                         / (x.ra_err * x.ra_err + r.wm_ra_err * r.wm_ra_err) 
                                        + (x.decl - r.wm_decl) * (x.decl - r.wm_decl)
                                         / (x.decl_err * x.decl_err + r.wm_decl_err * r.wm_decl_err)
                                        ) < %s
                            )
        ;
        """
        #q = query % (image_id, image_id, image_id,
        #               radius, radius, radius, 
        #               radius, radius, radius, deRuiter_red)
        cursor.execute(query, (image_id, image_id, image_id, 
                                radius, radius, radius,
                                radius, radius, radius, deRuiter_red))
        results = zip(*cursor.fetchall())
        if not AUTOCOMMIT:
            conn.commit()                        
        cursor.close()
        r = ()
        if len(results) != 0:
            p = zip(list(results[1]), list(results[2]))
            r = (p,)
    except db.Error, e:
        query = query % (image_id, image_id, image_id, \
                         radius, radius, radius, \
                         radius, radius, radius, \
                         deRuiter_red)
        logger.warn("Query failed:\n%s", query)
        raise
    return r

def get_monsources(image_id, deRuiter_r, radius=0.03):
    """Returns the user-entry sources and no-counterpart sources from 
    monitoringlist
    
    Sources in monitoringlist that originate from a user entry and
    those that do not have a counterpart in extractedsource need to be 
    passed on to sourcefinder for a forced fit.
    
    Output: id, ra, decl
    """
    deRuiter_red = deRuiter_r / 3600.
    try:
        conn = DataBase().connection 
        cursor = conn.cursor()
        query = """\
        SELECT m1.id AS id
              ,r1.wm_ra AS ra
              ,r1.wm_decl AS decl
          FROM monitoringlist m1
              ,runningcatalog r1
              ,image i1
         WHERE i1.id = %s
           AND i1.dataset = m1.dataset
           AND m1.dataset = r1.dataset 
           AND m1.runcat = r1.id
           AND m1.userentry = FALSE
           AND m1.id NOT IN (
                            SELECT m.id
                              FROM monitoringlist m
                                  ,extractedsource x
                                  ,runningcatalog r
                                  ,image i
                             WHERE i.id = %s
                               AND i.id = x.image
                               AND x.image = %s
                               AND i.dataset = m.dataset
                               AND m.runcat = r.id
                               AND m.userentry = FALSE
                               AND r.zone BETWEEN CAST(FLOOR(x.decl - %s) as INTEGER)
                                              AND CAST(FLOOR(x.decl + %s) as INTEGER)
                               AND r.wm_decl BETWEEN x.decl - %s
                                                 AND x.decl + %s
                               AND r.wm_ra BETWEEN x.ra - alpha(%s, x.decl)
                                               AND x.ra + alpha(%s, x.decl)
                               AND SQRT(  (x.racosdecl - r.wm_ra * COS(RADIANS(r.wm_decl)))
                                        * (x.racosdecl - r.wm_ra * COS(RADIANS(r.wm_decl)))
                                        / (x.ra_err * x.ra_err + r.wm_ra_err * r.wm_ra_err)
                                       + (x.decl - r.wm_decl) * (x.decl - r.wm_decl)
                                        / (x.decl_err * x.decl_err + r.wm_decl_err * r.wm_decl_err)                            
                                       ) < %s
                            )
        """
        cursor.execute(query, (image_id, image_id, image_id, 
                                radius, radius, radius,
                                radius, radius, radius, deRuiter_r / 3600.))
        results = zip(*cursor.fetchall())
        if not AUTOCOMMIT:
            conn.commit()                        
        cursor.close()
        q = query % (image_id, image_id, image_id, 
                        radius, radius, radius, radius, radius, radius,
                        deRuiter_r / 3600.)
        r = ()
        if len(results) != 0:
            p = zip(list(results[1]), list(results[2]))
            r = (p,)
    except db.Error, e:
        query = query % (image_id,image_id,image_id, radius, radius,radius,radius,radius,radius,deRuiter_r / 3600.)
        logger.warn("Query failed:\n%s", query)
        raise
    return r

def insert_forcedfits_into_extractedsource(image_id, results, extract):
    general.insert_extracted_sources(image_id, results, extract)

def adjust_transients_in_monitoringlist(image_id, transients):
    """Adjust transients in monitoringlist, by either adding or
    updating them
    
    """
    conn = DataBase().connection
    _update_known_transients_in_monitoringlist(conn, image_id, transients)
    _insert_new_transients_in_monitoringlist(conn, image_id, transients)
    
def _update_known_transients_in_monitoringlist(conn, image_id, transients):
    """Update transients in monitoringlist"""
    cursor = conn.cursor()
    query = """\
    UPDATE monitoringlist
       SET ra = %s
          ,decl = %s
      WHERE runcat = %s
    """
    upd = 0
    for transient in transients:
        try:
            upd += cursor.execute(query, (float(transient.ra),
                                     float(transient.decl),
                                     transient.runcatid))
        except db.Error, e:
            logger.warn("Query failed:\n%s", query)
            raise

    if not AUTOCOMMIT:
                conn.commit()
    cursor.close()
    if upd > 0:
        logger.info("Updated %s known transients in monitoringlist" % (upd,))


def _insert_new_transients_in_monitoringlist(conn, image_id, transients):
    """Insert transients that are not yet stored in monitoringlist.

    Therefore, we have to grab the transients and check that there
    runcat ids are not in the monitoringlistlist
    
    """
    
    try:
        cursor = conn.cursor()
        query = """\
        INSERT INTO monitoringlist
          (runcat
          ,ra
          ,decl
          ,dataset
          )
          SELECT t.runcat
                ,r.wm_ra
                ,r.wm_decl
                ,r.dataset 
            FROM transient t
                ,runningcatalog r
                ,image i 
           WHERE t.runcat = r.id 
             AND r.dataset = i.dataset 
             AND i.id = %s
             AND t.runcat NOT IN (SELECT m0.runcat 
                                    FROM monitoringlist m0
                                        ,runningcatalog r0
                                        ,image i0
                                   WHERE m0.runcat = r0.id 
                                     AND r0.dataset = i0.dataset 
                                     AND i0.id = %s
                                 )
        """
        ins = cursor.execute(query, (image_id, image_id))
        if not AUTOCOMMIT:
            conn.commit()                        
        cursor.close()
        if ins == 0:
            logger.info("No new transients inserted in monitoringlist")
        else:
            logger.info("Inserted %s new transients in monitoringlist" % (ins,))
    except db.Error, e:
        query = query % (image_id, image_id)
        logger.warn("Query failed:\n%s", query)
        raise


def add_nulldetections(image_id):
    """
    Add null detections (intermittent) sources to monitoringlist.
     
    Null detections are picked up by the source association and
    added to extractedsource table to undergo normal processing.
   
    Variable or not, intermittent sources are interesting enough 
    to be added to the monitoringlist.
    
    Insert checks whether runcat ref of source exists
    """
    
    # TODO:
    # Do we need to take care of updates here as well (like the adjust_transients)?
    # Or is that correctly done in update monlist

    # Optimise by using image_id for image and extractedsource
    # extract_type = 1 -> the null detections (forced fit) in extractedsource
    try:
        conn = DataBase().connection
        cursor = conn.cursor()
        query = """\
        INSERT INTO monitoringlist
          (runcat
          ,ra
          ,decl
          ,dataset
          )
          SELECT r.id AS runcat
                ,r.wm_ra AS ra
                ,r.wm_decl AS decl
                ,r.dataset 
            FROM extractedsource x
                ,image i
                ,runningcatalog r
                ,assocxtrsource a 
           WHERE x.image = %s
             AND x.image = i.id 
             AND x.image = %s
             AND i.dataset = r.dataset 
             AND r.id = a.runcat 
             AND a.xtrsrc = x.id 
             AND x.extract_type = 1
             AND NOT EXISTS (SELECT m0.runcat 
                               FROM extractedsource x0
                                   ,image i0
                                   ,runningcatalog r0
                                   ,assocxtrsource a0 
                                   ,monitoringlist m0
                              WHERE x0.image = %s
                                AND x0.image = i0.id 
                                AND x0.image = %s
                                AND i0.dataset = r0.dataset 
                                AND r0.id = a0.runcat 
                                AND a0.xtrsrc = x0.id 
                                AND x0.extract_type = 1
                                AND r0.id = m0.runcat
                            )
        """
        ins = cursor.execute(query, (image_id, image_id, image_id, image_id))
        if not AUTOCOMMIT:
            conn.commit()
        cursor.close()
        if ins > 0:
            logger.info("Added %s forced fit null detections to monlist" % (ins,))
    except db.Error, e:
        query = query % (image_id,image_id,image_id,image_id) 
        logger.warn("query failed:\n%s", query)
        raise


def add_manual_entry_to_monitoringlist(conn, dataset_id, 
                          ra, dec):
    """
    Add manual entry to monitoringlist.
    
    In this case, the runcat_id defaults to null initially, 
    since there is no associated source yet.
    (This is updated when we perform our first forced extraction 
    at these co-ordinates.) 
    """
    
    cursor = conn.cursor()
    try:
        query = """\
        INSERT INTO monitoringlist
          (ra
          ,decl
          ,dataset
          ,userentry
          )
          SELECT %s 
                ,%s 
                ,%s
                ,TRUE
"""
        cursor.execute(query, (ra, dec, dataset_id))
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error:
        query = query 
        logger.warn("Query %s failed", query)
        cursor.close()
        raise
    finally:
        cursor.close()
