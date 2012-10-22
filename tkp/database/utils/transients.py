"""
A collection of back end subroutines (mostly SQL queries).

This module contains the routines dealing with analysis of transients,
mostly involving the 'transient' table.

"""
import os
import sys
import math
import logging
import monetdb.sql as db
from tkp.config import config
import numpy
from scipy.stats import chisqprob
from . import monitoringlist

from tkp.classification.transient import Transient
from tkp.classification.transient import Position
from tkp.classification.transient import DateTime

AUTOCOMMIT = config['database']['autocommit']
DERUITER_R = config['source_association']['deruiter_radius']
BG_DENSITY = config['source_association']['bg-density']



def insert_transient(conn, transient, dataset_id, imageid):
    """Insert a transient source in the database.
    Transients are stored in the transient table, 
    as well as in the monitoringlist.
    Transient behaviour is checked per frequency band, 
    because we assume that fluxes are not comparable across bands.

    A check is performed on the runcat id. If there is an entry for this 
    runcat id already in the table, we replace that transient by this one.

    We also call the monitoringlist insertion routine to ensure its flux
    will be measured even when the transient drops below the detection
    threshold. 
    """

    #runcatid = transient.runcatid
    #print "runcatid:",runcatid
    try:  # Find the possible transient associated with the current source
        cursor = conn.cursor()
        #query = """\
        #SELECT id 
        #  FROM transient
        # WHERE runcat = %s
        #   AND band = %s
        #"""
        #cursor.execute(query, (transient.runcatid,))
        #cursor.execute(query, (transient.runcatid, transient.band))
        #transientid = cursor.fetchone()
        #print "transientid:",transientid
        #print "transient.trid:",transient.trid
        if transient.trid is not None:  # update/replace existing source
            #print "HALT: INCLUDE transient.id from above IN QUERY AS WELL"
            query = """\
            UPDATE transient
               SET siglevel = %s
                  ,V_int = %s
                  ,eta_int = %s
             WHERE id = %s
            """
            cursor.execute(query, (numpy.float(transient.siglevel),transient.V_int, 
                                   transient.eta_int, transient.trid))
        else:  # insert new source
            ## FIXME: ASSUMES ONLY INPUT ONE IMAGE AT A TIME
            ## SEE ISSUE #3531
            # https://support.astron.nl/lofar_issuetracker/issues/3531
            
            # First, let's find the current xtrsrc_id that belongs to the
            # current image: this is the trigger source id
            #if imageid is None:
            #    query_tail = ""
            #else:
            #    image_set = ", ".join([str(image) for image in imageid])
            #    query_tail = " AND ex.image IN (%s)" % image_set  
            #query = """\
            #SELECT ex.id 
            #  FROM extractedsource ex
            #      ,assocxtrsource ax
            # WHERE 
            #     ex.id = ax.xtrsrc 
            #   AND ax.runcat = %s
            #""" + query_tail
            #query = """\
            #SELECT ex.id 
            #  FROM extractedsource ex
            #      ,assocxtrsource ax
            # WHERE ex.id = ax.xtrsrc 
            #   AND ax.runcat = %s
            #   AND ex.image = %s
            #"""
            
            #print "Q2:\n", query % (transient.runcatid, imageid)
            #cursor.execute(query, (transient.runcatid,imageid))
            #trigger_srcid = cursor.fetchone()[0]
            #print "trigger_srcid:",trigger_srcid
            #print "transient.trigger_xtrsrc:",transient.trigger_xtrsrc
            #sys.exit()
            query = """\
            INSERT INTO transient
              (runcat
              ,band
              ,siglevel
              ,V_int
              ,eta_int
              ,trigger_xtrsrc
              )
            VALUES 
              (%s
              ,%s
              ,%s
              ,%s
              ,%s
              ,%s
              )
            """
            #print "transient.siglevel:",transient.siglevel
            #print "numpy.float(transient.siglevel):",numpy.float(transient.siglevel)
            cursor.execute(query, (transient.runcatid, transient.band, 
                                   numpy.float(transient.siglevel),
                                   transient.V_int, transient.eta_int, transient.trigger_xtrsrc))
        if not AUTOCOMMIT:
            conn.commit()
        cursor.close()
    except db.Error:
        logging.warn("Query %s failed", query)
        raise
    
    monitoringlist.add_runcat_sources_to_monitoringlist(conn,
                                                        dataset_id, 
                                                        [transient.runcatid])



def _select_variability_indices(conn, imageid, V_lim, eta_lim):
    """Select sources and variability indices in the running catalog

    This comes relatively easily, since we have kept track of the
    average fluxes and the variance measures, and thus can quickly
    obtain any sources that exceed a constant flux by a certain amount.

    We select those sources that have a V_lim (V_int_lim) and eta_lim 
    (eta_int_lim) larger than their critical values, based on their 
    integrated fluxes. In the result set are the values based on the 
    peak fluxes shown as well.

    Args:

        dsid (int): dataset of interest

        V_lim ():

        eta_lim ():
    """

    # To do: explain V_lim and eta_lim
    
    results = []
    cursor = conn.cursor()
    try:
        query = """\
SELECT t1.runcat
      ,t1.dataset
      ,t1.band
      ,t1.f_datapoints
      ,t1.wm_ra
      ,t1.wm_decl
      ,t1.wm_ra_err
      ,t1.wm_decl_err
      ,t1.V_int_inter / t1.avg_f_int AS V_int
      ,t1.eta_int_inter / t1.avg_f_int_weight AS eta_int
      ,t1.trigger_xtrsrc
      ,CASE WHEN m0.runcat IS NULL
            THEN FALSE
            ELSE TRUE
       END AS monitored
      ,tr0.id AS trid
  FROM (SELECT rf0.runcat
              ,im0.dataset
              ,im0.band
              ,f_datapoints
              ,wm_ra
              ,wm_decl
              ,wm_ra_err
              ,wm_decl_err
              ,avg_f_int
              ,avg_f_int_weight
              ,CASE WHEN rf0.f_datapoints = 1
                    THEN 0
                    ELSE SQRT(CAST(rf0.f_datapoints AS DOUBLE) * (avg_f_int_sq - avg_f_int * avg_f_int) 
                             / (CAST(rf0.f_datapoints AS DOUBLE) - 1.0)
                             )
               END AS V_int_inter
              ,CASE WHEN rf0.f_datapoints = 1
                    THEN 0
                    ELSE (CAST(rf0.f_datapoints AS DOUBLE) / (CAST(rf0.f_datapoints AS DOUBLE) - 1.0)) 
                         * (avg_f_int_weight * avg_weighted_f_int_sq - avg_weighted_f_int * avg_weighted_f_int)
               END AS eta_int_inter
              ,x0.id AS trigger_xtrsrc
          FROM runningcatalog rc0
              ,runningcatalog_flux rf0
              ,image im0
              ,extractedsource x0
              ,assocxtrsource a0
         WHERE im0.id = %s
           AND rc0.dataset = im0.dataset
           AND rc0.id = rf0.runcat
           AND rf0.band = im0.band
           AND a0.runcat = rc0.id
           AND x0.id = a0.xtrsrc
           AND x0.image = im0.id
       ) t1
       LEFT OUTER JOIN monitoringlist m0
       ON t1.runcat = m0.runcat 
       LEFT OUTER JOIN transient tr0
       ON t1.runcat = tr0.runcat
       AND t1.band = tr0.band
 WHERE t1.V_int_inter / t1.avg_f_int > %s
   AND t1.eta_int_inter / t1.avg_f_int_weight > %s
"""
        #print "Q:\n", query % (imageid,V_lim,eta_lim)
        #sys.exit()
        cursor.execute(query, (imageid, V_lim, eta_lim))
        results = cursor.fetchall()
        results = [dict(
            runcatid=x[0], npoints=x[3], V_int=x[8], eta_int=x[9], dataset=x[1],
            band=x[2], ra=x[4], dec=x[5], ra_err=x[6], dec_err=x[7], 
            trigger_xtrsrc=x[10], monitored=x[11], trid=x[12])
                   for x in results]
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error:
        query = query % (imageid, V_lim, eta_lim)
        logging.warn("Query failed:\n%s", query)
        raise
    finally:
        cursor.close()
    return results


def detect_variable_sources(conn, imageid, V_lim, eta_lim):
    """Detect variability in extracted sources compared to the previous
    detections"""

    return _select_variability_indices(conn, imageid, V_lim, eta_lim)


def transient_search(conn,
                     dataset,
                     eta_lim, V_lim,
                     probability_threshold,
                     minpoints,
                     imageid,
                     #image_ids=None,
                     logger=None):
    #results = dataset.detect_variables(V_lim, eta_lim)
    #print "imageid:",imageid
    results = detect_variable_sources(conn, imageid, V_lim, eta_lim)
    #print "results:",results
    transients = []
    if len(results) > 0:
        if logger is not None:
            logger.info("Found %d variable sources", len(results))

        # need (want) sorting by sigma
        # This is not pretty, but it works:
        tmpresults = dict((key,  [result[key] for result in results])
                       for key in ('runcatid', 'npoints', 'V_int', 'eta_int'))
        #print "tmpresults:", tmpresults
        runcatids = numpy.array(tmpresults['runcatid'])
        #print "runcatids:",runcatids
        weightedpeaks, dof = (numpy.array(tmpresults['V_int']),
                              numpy.array(tmpresults['npoints'])-1)
        #print "weightedpeaks:",weightedpeaks
        #print "dof:", dof
        #print "tmpresults['eta_int']:",tmpresults['eta_int']
        probability = 1 - chisqprob(tmpresults['eta_int'] * dof, dof)
        #print "probability:",probability
        #print "probability_threshold:",probability_threshold
        selection = probability > probability_threshold
        #print "selection:",selection
        selected_rcids = numpy.array(runcatids)[selection]
        #print "selected_rcids:",selected_rcids
        selected_results = numpy.array(results)[selection]
        #print "selected_results:",selected_results
        siglevels = probability[selection]
        #print "siglevels:",siglevels

        #print "zip(siglevels, selected_results):",zip(siglevels, selected_results)
        for siglevel, result in zip(siglevels, selected_results):
            #print "minpoints:",minpoints
            #print "result['npoints']:",result['npoints']
            #print "siglevel:",siglevel
            #print "result:",result
            if result['npoints'] < minpoints:
                continue
            position = Position(ra=result['ra'], dec=result['dec'],
                                error=(result['ra_err'], result['dec_err']))
            #print "position:",position
            transient = Transient(runcatid=result['runcatid'], position=position)
            #print "transient:",transient

            #FIXME: Monkey patching isn't exactly documentation friendly...
            # You need to see what is done here before you understand
            # the called function!
            transient.siglevel = siglevel
            transient.band = result['band']
            transient.eta_int = result['eta_int']
            transient.V_int = result['V_int']
            transient.dataset = result['dataset']
            transient.trigger_xtrsrc = result['trigger_xtrsrc']
            # We don't need it to be queried again, since
            # we can do it at once in _select_variability_indices()
            #transient.monitored = monitoringlist.is_monitored(
            #    conn, transient.runcatid)
            transient.monitored = result['monitored']
            transient.trid = result['trid']
            #TODO:Bart 1-10-2012, check image_ids
            #print "transient:",transient
            insert_transient(conn, transient,
                                 dataset.id, imageid)
            transients.append(transient)
    else:
        selected_rcids = numpy.array([], dtype=numpy.int)
        siglevels = numpy.array([], dtype=numpy.float)

    return selected_rcids, siglevels, transients
