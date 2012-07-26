"""
A collection of back end subroutines (mostly SQL queries).

This module contains the routines to deal with flagging and monitoring 
of transient candidates, mostly involving the monitoringlist.
"""
import os
import sys
import math
import logging
import monetdb.sql as db
from tkp.config import config
from . import generic
from . import general


AUTOCOMMIT = config['database']['autocommit']
DERUITER_R = config['source_association']['deruiter_radius']
BG_DENSITY = config['source_association']['bg-density']


def is_monitored(conn, runcatid):
    """Check whether a source is in the monitoring list.
    
        Returns: boolean
    """

    cursor = conn.cursor()
    try:
        query = """\
        SELECT COUNT(*) 
          FROM monitoringlist 
         WHERE runcat = %s
        """
        cursor.execute(query, (runcatid,))
        result = bool(cursor.fetchone()[0])
    except db.Error, e:
        query = query % runcatid
        logging.warn("Query failed: %s", query)
        raise
    finally:
        cursor.close()
    return result


def get_monitoringlist_not_observed(conn, image_id, dataset_id):
    """
    Return a list of sources from the monitoringlist that have no 
    association with the extracted sources for this image.
    
    Returns (list of tuples), format is:
        [( ra, dec, runcatid , monitorid )]
    
    There is a bit of logic branching here to decide how the 
    RA, DEC is determined:
    
    -For a source with `blind' extractions, i.e. good signal to noise 
    in some image, position not pre-specified, then we should use the 
    weighted mean position from runningcatalog.
    
    -For a new, manual entry on monitoringlist,we have no choice but 
    to use the manually specified co-ordinates.
    
    -For a manually specified entry with previous extractions,
    the best course of action is unclear. Should we use the manually specified location, 
    or a previous association (via runcat weighted ra, dec) that might be somewhat offset?
    For now, we always just return the manual co-ordinates in this case.   
    
    TO DO: Carefully consider this logic case and update if necessary!
    
    
    """
    not_observed = get_monitoringlist_not_observed_blind_entries(
                                 conn, image_id, dataset_id)
    
    not_observed.extend(
            get_monitoringlist_not_observed_manual_entries(
                               conn, image_id, dataset_id)
                        )
    return not_observed
    
    

def get_monitoringlist_not_observed_blind_entries(conn, image_id, dataset_id):
    """
    Return a list of sources from the monitoringlist that have no
    association with the extracted sources for this image, but 
    are associated with previous blind extractions rather than 
    manual additions to the monitoringlist. 
    (and hence have at least one datapoint)
    
    We do this by matching the monitoring list runcat with the
    extractedsource ids through the assocxtrsource table. 
    Using a left outer join we get nulls in the place where a source should
    have been, but isn't: these are the sources that are not in
    extractedsources and thus weren't automatically picked up by the
    sourcefinder. We limit our query using the image_id (and dataset
    through image.dataset).

    Lastly, we get the best (weighted averaged) position for the
    sources to be monitored from the runningcatalog, which shows up in
    the final inner join.

    See also: get_monitoringlist_not_observed_manual_entries
     
    Args:

        conn: A database connection object.

        image_id (int): the image under consideration.
        dataset_id (int): the dataset to which the image belongs.
            (Specifying this allows us to narrow the query down better,
            resulting in a much smaller join)

    Returns (list):
        A list of sources yet to be observed; format is:
        [( ra, decl, runcatid , monitorid )]
    """
    
    
#NOTES:
# t1 : A Table comprising pairs of (runcatid, xtrsrcid) 
#         for extracted sources in this image.
#    
# t2: Pairs of runcatid, monitorid, for runcat entries which do NOT have an 
#        associated extraction in this image 
#     --- (Join on runcat id of monitoringlist, t1 contains 
#          xtrsrcid for entries in the monitoringlist 
#          which also have an extraction in this image, and  
#          contains NULL for all other entries.
#          We filter on xtrsrc=NULL to just give the non-extracted runcat entries.)
#    
#    Finally, pull in best estimates for RA, DEC by cross matching into runcat.
#    
#    
    try:
        cursor = conn.cursor()
        #Query simplified to match new database schema, 23/07/12. -TS
        query = """\
        SELECT rc.wm_ra
              ,rc.wm_decl
              ,t2.runcat
              ,t2.monitorid
          FROM (SELECT ml.id AS monitorid
                      ,ml.runcat AS runcat
                  FROM monitoringlist ml
                       LEFT OUTER JOIN (SELECT ax.runcat as runcat
                                              ,ax.xtrsrc as xtrsrc
                                          FROM extractedsource ex
                                              ,assocxtrsource ax
                                         WHERE ex.id = ax.xtrsrc
                                           AND ex.image = %s
                       ) t1
                       ON ml.runcat = t1.runcat
                     WHERE t1.xtrsrc IS NULL
                         AND ml.dataset = %s
                         AND ml.userentry = false
               ) t2
              ,runningcatalog rc
         WHERE rc.id = t2.runcat
        """
        cursor.execute(query, (image_id, dataset_id))
        results = cursor.fetchall()
    except db.Error, e:
        query = query % (image_id, image_id)
        logging.warn("Query failed: %s", query)
        raise
    finally:
        cursor.close()
    return results

def get_monitoringlist_not_observed_manual_entries(conn, image_id, dataset_id):
    """
    Return a list of manually added entries from the monitoringlist that have no
    association with the extracted sources for this image.
    
    Currently always returns the manually specified co-ordinates.
    (TO DO: This needs reviewing, we might need something smarter) 
    
    Returns (list of tuples), format is:
        [( ra, decl, runcatid , monitorid )]
    """
    
    
##Notes:
# See: comments for blind entries function.
# NB if ml entry is new, runcat will be NULL
#    but this will still generate a valid row in the left join 
#    (with xtrsrc=NULL), so it's fine.
#
    try:
        cursor = conn.cursor()        
        query = """\
        SELECT ml.ra as ra
                ,ml.decl AS decl
                ,ml.id AS monitorid
                ,ml.runcat AS runcat
          FROM monitoringlist ml
           LEFT OUTER JOIN (SELECT ax.runcat as runcat
                                  ,ax.xtrsrc as xtrsrc
                              FROM extractedsource ex
                              ,assocxtrsource ax
                             WHERE ex.id = ax.xtrsrc
                               AND ex.image = %s
               ) t1
               ON ml.runcat = t1.runcat
             WHERE t1.xtrsrc IS NULL
             AND ml.dataset = %s
             AND ml.userentry = true
        """
        cursor.execute(query, (image_id, dataset_id))
        results = cursor.fetchall()
    except db.Error, e:
        query = query % (image_id, image_id)
        logging.warn("Query failed: %s", query)
        raise
    finally:
        cursor.close()
    return results


def insert_monitored_sources(conn, results, image_id):
    """Insert the list of measured monitoring sources for this image into
    extractedsource and runningcatalog.

    For user-inserted sources (i.e., sources that were not discovered
    automatically), the source will be inserted into the
    runningcatalog as well; for "normal" monitoring sources (i.e.,
    ones that preset a transient), this does not happen, to not
    pollute the runningcatalog averages for this entry.

    The insertion into runningcatalog can be done by xtrsrc_id from
    monitoringlist. In case it is negative, it is appended to
    runningcatalog, and xtrsrc_id is updated in the monitoringlist.
    
    TO DO: Refactor into smaller functions 
        (+ I think there is probably some code duplication here) 
    
    Args:
    
    results -- list of tuples,
    [(runcat_id, monitoringlist_id, 
    ra, dec,
    ...    
    beam_angle)] 
    (See tuple unpacking below)     
    """

    cursor = conn.cursor()
    # step through all the indiviudal results (/sources)
    for runcatid, monitorid, result in results:

        
        #TO DO: This whole logic flow probably needs cleaning up more, and optimizing.
        
        # Always insert them into extractedsource
        xtrsrcid =_insert_user_monitored_source_into_extractedsource(
                             cursor, image_id, result)
        
        if runcatid is None: 
            #This is a userentry, measured for the first time. It needs a runcat entry.
            runcatid = _insert_user_monitored_source_into_runcat(
                                 cursor, xtrsrcid, image_id)
            
            #Also update the monitoringlist entry
            _update_monitoringlist_entry_rcid(cursor, monitorid, runcatid )
            
        
        # Whether the source is user or blind-extraction generated,
        # We don't update the runningcatalog, because:
        # - the fluxes are below the detection limit, and
        #   add little to nothing to the average flux
        # - the positions will have large errors, and
        #   contribute very litte to the average position
        # We thus only need to update the association table,
        _insert_monitored_source_into_assocxtrsource(cursor,runcatid,xtrsrcid)

    if not AUTOCOMMIT:
        conn.commit()                        
    cursor.close()
        
def _insert_user_monitored_source_into_extractedsource(cursor, image_id, result):
    """Returns: xtrsrcid
    
       TO DO: Could use general purpose extractedsource insertion routine,
               if only it returned the xtrsrc ids.
    """
    ra, dec, ra_err, dec_err, peak, peak_err, flux, flux_err, sigma, \
    semimajor, semiminor, pa = result
    x = math.cos(math.radians(dec)) * math.cos(math.radians(ra))
    y = math.cos(math.radians(dec)) * math.sin(math.radians(ra))
    z = math.sin(math.radians(dec))
    racosdecl = ra * math.cos(math.radians(dec))
    if True: #Temporary indentation hack to make it easier to track diff
        query = """\
        INSERT INTO extractedsource
          (image
          ,zone
          ,ra
          ,decl
          ,ra_err
          ,decl_err
          ,x
          ,y
          ,z
          ,racosdecl
          ,det_sigma
          ,f_peak
          ,f_peak_err
          ,f_int
          ,f_int_err
          ,semimajor
          ,semiminor
          ,pa
          ,extract_type
          )
        VALUES
          (%s
          ,%s
          ,%s
          ,%s
          ,%s
          ,%s
          ,%s
          ,%s
          ,%s
          ,%s
          ,%s
          ,%s
          ,%s
          ,%s
          ,%s
          ,%s
          ,%s
          ,%s
          ,1
          )
        """
        try:
            cursor.execute(
                query, (image_id, int(math.floor(dec)), ra, dec, ra_err, dec_err,
                        x, y, z, racosdecl, sigma, peak, peak_err, flux, flux_err,
                        semimajor, semiminor, pa))
            return cursor.lastrowid
        except db.Error, e:
            query = query % (
                image_id, int(math.floor(dec)), ra, dec, ra_err, dec_err,
                x, y, z, sigma, peak, peak_err, flux, flux_err,
                semimajor, semiminor, pa)
            logging.warn("Query failed: %s", query)
            cursor.close()
            raise
        
        

def _insert_user_monitored_source_into_runcat(cursor, xtrsrcid, image_id):
    """Returns: runcatid"""
    if True: #Temporary indentation hack to make it easier to track diff
        if True: #Remove once everything working fine.
            
            # Insert as new source into the running catalog
            # and update the monitoringlist.xtrsrc
            query = """\
            INSERT INTO runningcatalog
                (xtrsrc
                ,dataset
                ,datapoints
                ,zone
                ,wm_ra
                ,wm_decl
                ,wm_ra_err
                ,wm_decl_err
                ,avg_wra
                ,avg_wdecl
                ,avg_weight_ra
                ,avg_weight_decl
                ,x
                ,y
                ,z
                )
                SELECT x0.id
                      ,i0.dataset
                      ,1
                      ,x0.zone
                      ,x0.ra
                      ,x0.decl
                      ,x0.ra_err
                      ,x0.decl_err
                      ,x0.ra / (x0.ra_err * x0.ra_err)
                      ,x0.decl / (x0.decl_err * x0.decl_err)
                      ,1 / (x0.ra_err * x0.ra_err)
                      ,1 / (x0.decl_err * x0.decl_err)
                      ,x0.x
                      ,x0.y
                      ,x0.z
                  FROM extractedsource x0
                      ,image i0
                 WHERE x0.id = %s
                   AND i0.id = %s
            """
            # TODO: Add runcat_flux as well!
            try:
                cursor.execute(query, (xtrsrcid, image_id))
                return cursor.lastrowid
            except db.Error, e:
                query = query % (image_id, xtrsrcid)
                logging.warn("query failed: %s", query)
                cursor.close()
                raise
            
def _update_monitoringlist_entry_rcid(cursor, monitorid, runcatid ):
    if True: #Temporary indentation hack to make it easier to track diff
        if True: #Remove once everything working fine.
            # Now update the monitoringlist.runcat
            query = """\
            UPDATE monitoringlist 
               SET runcat = %s 
             WHERE id = %s
            """
            try:
                cursor.execute(query, (runcatid, monitorid))
            except db.Error, e:
#                query = query % (xtrsrcid, xtrsrc_id)
                logging.warn("query failed: %s", query)
                cursor.close()
                raise                    
            
def _insert_monitored_source_into_assocxtrsource(cursor,runcatid,xtrsrcid):
    if True: #Temporary indentation hack to make it easier to track diff
        if True: #Remove once everything working fine. 
            query = """\
            INSERT INTO assocxtrsource 
              (runcat
              ,xtrsrc
              ,type
              ,distance_arcsec
              ,r
              ,loglr
              )
            VALUES 
              (%s
              ,%s
              ,0
              ,0
              ,0
              ,0)
            """
            try:
                cursor.execute(query, (runcatid, xtrsrcid))
            except db.Error, e:
                query = query % (runcatid, xtrsrcid)
                logging.warn("query failed: %s", query)
                cursor.close()
                raise


def add_runcat_sources_to_monitoringlist(conn, dataset_id, 
                          runcat_ids):
    """
    Add entries to monitoringlist.
     
    Insert each runcat id if it doesn't already exist.
    (Action is idempotent).
    
    """
    
    #De-duplicate our input list:
    
    
    ##NB Should be able to check for pre-existing runcats, 
    ## and insert, all in one go with something like:
    
#    INSERT INTO monitoringlist
#    (runcat, dataset)
#    SELECT id, dataset
#    FROM runningcatalog
#    WHERE id in ()
#      AND
#    id NOT IN
#    (SELECT runcat FROM monitoringlist)

## But I can't get it to work, so I'll do it the simple way.

    prior_runcat_entries = generic.columns_from_table(conn, 
                              'monitoringlist', 
                              ['runcat'], 
                              where={'dataset':dataset_id})
    

    runcat_ids = set(runcat_ids).difference(
                           set(e['runcat'] for e in prior_runcat_entries)
                           )
    
    if len(runcat_ids):
        cursor = conn.cursor()
        try:
            values_placeholder = ", ".join(["( %s, %s )"] * len(runcat_ids))
            values_list = []
            for rcid in runcat_ids:
                values_list.extend([ rcid, dataset_id])
            query = """\
    INSERT INTO monitoringlist
    (runcat, dataset)
    VALUES
    {placeholder}
    """.format(placeholder = values_placeholder)
            cursor.execute(query, tuple(values_list))
            if not AUTOCOMMIT:
                conn.commit()
        except db.Error:
            query = query 
            logging.warn("Query %s failed", query)
            cursor.close()
            raise
        finally:
            cursor.close()
    

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
(ra, decl, dataset, userentry)
SELECT %s ,%s ,%s, true
"""
        cursor.execute(query, (ra, dec, dataset_id))
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error:
        query = query 
        logging.warn("Query %s failed", query)
        cursor.close()
        raise
    finally:
        cursor.close()

def select_winking_sources(conn, dsid):
    """Select sources not detected in all epochs.
    
    Selects entries in running catalog which
    are not detected in *all* the images belonging to the dataset.
    
    Returns:
    list of dicts:
        [ {runcat, xtrsrc, datapoints} ]
    """
    
    results = []
    cursor = conn.cursor()
    try:
        #Thought about trying to do this in one clever SQL statement
        #But this will have to do for now.
        query="""SELECT COUNT(1) from image where dataset=%s"""
        cursor.execute(query, (dsid,))
        nimgs = cursor.fetchone()[0]
#        query="""\
#SELECT  xtrsrc
#        ,datapoints
#        ,avg_i_peak
#    FROM runningcatalog 
#    WHERE ds_id=%s 
#    AND datapoints<>%s
#"""
        query="""\
SELECT  id
        ,xtrsrc
        ,datapoints
    FROM runningcatalog 
    WHERE dataset=%s 
    AND datapoints<>%s
"""
        cursor.execute(query, (dsid, nimgs))
        results = cursor.fetchall()
#        results = [dict(xtrsrc_id=x[0], datapoints=x[1], avg_i_peak=x[2])
        results = [dict(runcat=x[0], xtrsrc=x[1], datapoints=x[2])
                   for x in results]
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error:
        logging.warn("Failed on query %s", query)
        raise
    finally:
        cursor.close()
    return results

def select_transient_candidates_above_thresh(
                    conn, 
                    runcat_ids,
                    single_epoch_threshold,
                    combined_threshold
                    ):
    """Takes a list of runcat_ids for candidate transients.
    
    Selects info for those which exceed the specified detection thresholds.
    
    Returns: a list of dicts
        [ {runcat, max_det_sigma, sum_det_sigma} ]
        
    """
    results = []
    cursor = conn.cursor()
    try:
        ids_placeholder = ", ".join(["%s"] * len(runcat_ids))
        query= """\
SELECT ax.runcat
       ,MAX(ex.det_sigma)
       ,SUM(ex.det_sigma)
    FROM 
        assocxtrsource ax
        ,extractedsource ex
    WHERE ax.runcat in ({0}) 
        AND ax.xtrsrc = ex.id
    GROUP BY ax.runcat
    HAVING 
        MAX(ex.det_sigma)>%s    
        AND SUM(ex.det_sigma)>%s;
""".format(ids_placeholder)
        query_tuple = tuple(runcat_ids +[single_epoch_threshold, combined_threshold])
        
#        print "QUERY:"
#        print query % query_tuple
        cursor.execute(query, query_tuple)
        results = cursor.fetchall()
        results = [dict(runcat=x[0], max_det_sigma=x[1], sum_det_sigma=x[2])
                   for x in results]
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error:
        logging.warn("Failed on query %s", query)
        raise
    finally:
        cursor.close()
    return results
    pass

