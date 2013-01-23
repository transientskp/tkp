"""
A collection of back end subroutines (mostly SQL queries).

This module contains the routines dealing with analysis of transients,
mostly involving the 'transient' table.

"""
import logging
import monetdb.sql as db
from tkp.config import config
from . import generic
import numpy
from scipy.stats import chisqprob
from . import monitoringlist
from tkp.classification.transient import Transient
from tkp.classification.transient import Position

logger = logging.getLogger(__name__)

AUTOCOMMIT = config['database']['autocommit']


def insert_transient(conn, transient, dataset_id):
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

    try:
        cursor = conn.cursor()
        if transient['trid'] is not None:  # update/replace existing source
            query = """\
            UPDATE transient
               SET siglevel = %s
                  ,V_int = %s
                  ,eta_int = %s
             WHERE id = %s
            """
            cursor.execute(query, (numpy.float(transient['siglevel']),
                               transient['v_int'], transient['eta_int'],
                               transient['trid']))
        else:
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
            cursor.execute(query, (transient['runcat'],
                                   transient['band'],
                                   numpy.float(transient['siglevel']),
                                   transient['v_int'],
                                   transient['eta_int'],
                                   transient['trigger_xtrsrc']))
        if not AUTOCOMMIT:
            conn.commit()
        cursor.close()
    except db.Error:
        logger.warn("Query %s failed", query)
        raise

    monitoringlist.add_runcat_sources_to_monitoringlist(conn,
                                                        dataset_id,
                                                        [transient['runcat']])



def select_variability_indices(conn, dsid, freq_band, V_lim, eta_lim):
    """
    Select sources and integrated flux variability indices from the running
    catalog, for a given frequency band.

    This comes relatively easily, since we have kept track of the
    average fluxes and the variance measures, and thus can quickly
    obtain any sources that exceed a constant flux by a certain amount.

    We select those sources that have integrated-flux V-indexes (variability) and
    eta-indexes (reduced-chi-sq values) larger than the specified limits.

    We also perform a left outer join with the monitoringlist and the
    transient tables, to determine if the source has been inserted into those
    tables yet.
    
    NB Variability index  = std.dev(flux) / mean(flux).
    In the pathological case where mean(flux)==0.0, we simply substitute
    variability index =  std.dev(flux) / 1e-6 (1 microJansky)
    to avoid division by zero errors.

    (TO DO: Return indices based on
    peak fluxes as well.)

    Args:

        dsid (int): dataset of interest

        freq_band(): frequency band being searched for variability

        V_lim ():

        eta_lim ():
    """

    # To do: explain V_lim and eta_lim

    results = []
    cursor = conn.cursor()
    try:
        query = """\
SELECT t1.runcat
      ,t1.f_datapoints
      ,t1.V_int_inter / t1.avg_f_int AS V_int
      ,t1.eta_int_inter / t1.avg_f_int_weight AS eta_int
      ,CASE WHEN m0.runcat IS NULL
            THEN FALSE
            ELSE TRUE
       END AS monitored
      ,tr0.id AS trid
  FROM (SELECT rf0.runcat
              ,rf0.band
              ,f_datapoints
              ,CASE WHEN avg_f_int = 0.0
                    THEN 0.000001
                    ELSE avg_f_int
               END AS avg_f_int
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
          FROM runningcatalog rc0
              ,runningcatalog_flux rf0
         WHERE rc0.dataset = %s
           AND rc0.id = rf0.runcat
           AND rf0.band = %s
       ) t1
       LEFT OUTER JOIN monitoringlist m0
       ON t1.runcat = m0.runcat
       LEFT OUTER JOIN transient tr0
       ON t1.runcat = tr0.runcat
       AND t1.band = tr0.band
 WHERE t1.V_int_inter / t1.avg_f_int > %s
   AND t1.eta_int_inter / t1.avg_f_int_weight > %s
"""
        cursor.execute(query, (dsid, freq_band, V_lim, eta_lim))

        results = cursor.fetchall()
        result_dicts = generic.convert_db_rows_to_dicts(results,
                                            [d[0] for d in cursor.description])

        if not AUTOCOMMIT:
            conn.commit()
    except db.Error:
        query = query % (dsid, freq_band, V_lim, eta_lim)
        logger.warn("Query failed:\n%s", query)
        raise
    finally:
        cursor.close()
    return result_dicts


def transient_search(conn,
                     dsid,
                     freq_band,
                     eta_lim, V_lim,
                     probability_threshold,
                     minpoints,
                     imageid=None):

    results = select_variability_indices(conn, dsid, freq_band, V_lim, eta_lim)
    transients = []
    if len(results) > 0:
        if logger is not None:
            logger.info("Found %d variable sources", len(results))

        # need (want) sorting by sigma
        # This is not pretty, but it works:
        tmpresults = dict((key, [r[key] for r in results])
                       for key in ('runcat', 'f_datapoints', 'v_int', 'eta_int'))
        runcatids = numpy.array(tmpresults['runcat'])
        weightedpeaks, dof = (numpy.array(tmpresults['v_int']),
                              numpy.array(tmpresults['f_datapoints']) - 1)
        probability = 1 - chisqprob(tmpresults['eta_int'] * dof, dof)
        selection = probability > probability_threshold
        selected_rcids = numpy.array(runcatids)[selection]
        selected_results = numpy.array(results)[selection]
        siglevels = probability[selection]

        for siglevel, transient in zip(siglevels, selected_results):
            if transient['f_datapoints'] < minpoints:
                continue

            transient['siglevel'] = siglevel
            transient['band'] = freq_band

            #TODO:Bart 1-10-2012, check image_ids

            #TODO: Move this database op. outside the loop.
            if imageid is not None:
                #Trigger results from ingestion of one image
                cursor = conn.cursor()
                try:
                    query = """\
                    SELECT ex.id
                        FROM extractedsource ex
                            ,assocxtrsource ax
                        WHERE ax.runcat = %s
                          AND ex.image = %s
                          AND ax.xtrsrc = ex.id
                    """
                    cursor.execute(query, (transient['runcat'], imageid))
                    trigger_xtrsrc = cursor.fetchall()[0][0]
                except db.Error:
                    raise
                finally:
                    cursor.close()
                transient['trigger_xtrsrc'] = trigger_xtrsrc
            else:
                #Trigger results from analysis of multiple ingested images
                transient['trigger_xtrsrc'] = None

            insert_transient(conn, transient, dsid)
            transients.append(transient)
    else:
        selected_rcids = numpy.array([], dtype=numpy.int)
        siglevels = numpy.array([], dtype=numpy.float)

    return selected_rcids, siglevels, transients
