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
from . import monitoringlist


AUTOCOMMIT = config['database']['autocommit']
DERUITER_R = config['source_association']['deruiter_radius']
BG_DENSITY = config['source_association']['bg-density']



def insert_transient(conn, transient, dataset_id, image_ids=None):
    """Insert a transient source in the database.
    Transients are stored in the transients table, as well as in
    the monitoring list.

    A check is performed on the runcat id. If there is an entry for this 
    runcat id already in the
    table, we replace that transient by this one.

    We also call the monitoringlist insertion routine to ensure its flux
    will be measured even when the transient drops below the detection
    threshold. 
    """

    runcatid = transient.runcatid
    cursor = conn.cursor()
    try:  # Find the possible transient associated with the current source
        query = """\
        SELECT id 
          FROM transient
         WHERE runcat = %s
        """
        cursor.execute(query, (runcatid,))
        transientid = cursor.fetchone()
        if transientid:  # update/replace existing source
            query = """\
            UPDATE transient
               SET eta = %s
                  ,V = %s
             WHERE id = %s
            """
            cursor.execute(query, (transient.eta, transient.V, transientid[0]))
        else:  # insert new source
            ## FIXME: ASSUMES ONLY INPUT ONE IMAGE AT A TIME
            ## SEE ISSUE #3531
            # https://support.astron.nl/lofar_issuetracker/issues/3531
            
            # First, let's find the current xtrsrc_id that belongs to the
            # current image: this is the trigger source id
            if image_ids is None:
                image_set = ""
            else:
                image_set = ", ".join([str(image) for image in image_ids])
            query = """\
            SELECT ex.id 
              FROM extractedsource ex
                  ,assocxtrsource ax
             WHERE ex.image IN (%s) 
               AND ex.id = ax.xtrsrc 
               AND ax.runcat = %%s
            """ % image_set
            cursor.execute(query, (runcatid,))
            trigger_srcid = cursor.fetchone()[0]
            query = """\
            INSERT INTO transient
              (runcat
              ,eta
              ,V
              ,trigger_xtrsrc
              )
            VALUES 
              (%s
              ,%s
              ,%s
              ,%s
              )
            """
            cursor.execute(query, (runcatid, transient.eta, transient.V, trigger_srcid))
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error:
        logging.warn("Query %s failed", query)
        cursor.close()
        raise
    cursor.close()
    
    monitoringlist.add_runcat_sources_to_monitoringlist(conn,
                                                        dataset_id, 
                                                        [runcatid])



def _select_variability_indices(conn, dsid, V_lim, eta_lim):
    """Select sources and variability indices in the running catalog

    This comes relatively easily, since we have kept track of the
    average fluxes and the variance measures, and thus can quickly
    obtain any sources that exceed a constant flux by a certain amount.

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
SELECT runcat
      ,dataset
      ,f_datapoints
      ,wm_ra
      ,wm_decl
      ,wm_ra_err
      ,wm_decl_err
      ,t1.V_inter / t1.avg_f_peak AS V
      ,t1.eta_inter / t1.avg_f_peak_weight AS eta
  FROM (SELECT runcat
              ,dataset
              ,f_datapoints
              ,wm_ra
              ,wm_decl
              ,wm_ra_err
              ,wm_decl_err
              ,avg_f_peak
              ,avg_f_peak_weight
              ,CASE WHEN rf0.f_datapoints = 1
                    THEN 0
                    ELSE SQRT(CAST(rf0.f_datapoints AS DOUBLE) * (avg_f_peak_sq - avg_f_peak * avg_f_peak) 
                             / (CAST(rf0.f_datapoints AS DOUBLE) - 1.0)
                             )
               END AS V_inter
              ,CASE WHEN rf0.f_datapoints = 1
                    THEN 0
                    ELSE (CAST(rf0.f_datapoints AS DOUBLE) / (CAST(rf0.f_datapoints AS DOUBLE) - 1.0)) 
                         * (avg_f_peak_weight * avg_weighted_f_peak_sq - avg_weighted_f_peak * avg_weighted_f_peak)
               END AS eta_inter
          FROM runningcatalog rc0
              ,runningcatalog_flux rf0
         WHERE rc0.dataset = %s
           AND rc0.id = rf0.runcat
       ) t1
 WHERE t1.V_inter / t1.avg_f_peak > %s
   AND t1.eta_inter / t1.avg_f_peak_weight > %s
"""
        cursor.execute(query, (dsid, V_lim, eta_lim))
        results = cursor.fetchall()
        results = [dict(
            runcatid=x[0], npoints=x[2], v_nu=x[7], eta_nu=x[8], dataset=x[1],
            ra=x[3], dec=x[4], ra_err=x[5], dec_err=x[6])
                   for x in results]
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error:
        query = query % (dsid, V_lim, eta_lim)
        logging.warn("Query failed:\n%s", query)
        raise
    finally:
        cursor.close()
    return results

        
def detect_variable_sources(conn, dsid, V_lim, eta_lim):
    """Detect variability in extracted sources compared to the previous
    detections"""

    return _select_variability_indices(conn, dsid, V_lim, eta_lim)


def transient_search(dataset, 
                     eta_lim, V_lim,
                     detection_threshold, 
                     minpoints,
                     logger):
    results = dataset.detect_variables(eta_lim, V_lim)
    transients = []
    if len(results) > 0:
        logger.info("Found %d variable sources", len(results))
        
        # need (want) sorting by sigma
        # This is not pretty, but it works:
        tmpresults = dict((key,  [result[key] for result in results])
                       for key in ('runcatid', 'npoints', 'v_nu', 'eta_nu'))
        runcatids = numpy.array(tmpresults['runcatid'])
        weightedpeaks, dof = (numpy.array(tmpresults['v_nu']),
                              numpy.array(tmpresults['npoints'])-1)
        probability = 1 - chisqprob(tmpresults['eta_nu'] * dof, dof)
        selection = probability > detection_threshold
        selected_rcids = numpy.array(runcatids)[selection]
        selected_results = numpy.array(results)[selection]
        siglevels = probability[selection]
        
        for siglevel, result in zip(siglevels, selected_results):
            if result['npoints'] < minpoints:
                continue
            position = Position(ra=result['ra'], dec=result['dec'],
                                error=(result['ra_err'], result['dec_err']))
            transient = Transient(runcatid=result['runcatid'], position=position)
            transient.siglevel = siglevel
            transient.eta = result['eta_nu']
            transient.V = result['v_nu']
            transient.dataset = result['dataset']
            transient.monitored = dbu.is_monitored(
                self.database.connection, transient.srcid)
            insert_transient(self.database.connection, transient,
                                 dataset_id, images=self.inputs['image_ids'])
            transients.append(transient)
    else:
        selected_rcids = numpy.array([], dtype=numpy.int)
        siglevels = numpy.array([], dtype=numpy.float)
        
    return selected_rcids, siglevels, transients