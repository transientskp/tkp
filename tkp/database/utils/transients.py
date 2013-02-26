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
from tkp.database import DataBase


logger = logging.getLogger(__name__)

AUTOCOMMIT = config['database']['autocommit']

def _update_known_transients(transients):
    """Update the known transient sources in the database.

    Used when new measurements were made, changing variability indices.

    *Args*:
       - list of dictionaries representing transient entries.

     *Returns:*
     Number of entries updated. 
    """

    conn = DataBase().connection

    query = """\
    UPDATE transient
       SET siglevel = %(siglevel)s
          ,V_int = %(v_int)s
          ,eta_int = %(eta_int)s
     WHERE runcat = %(runcat)s
       AND band = %(band)s
    """
    upd = 0
    cursor = conn.cursor()
    for tr in transients:
        try:
            upd += cursor.execute(query, tr)
            if not AUTOCOMMIT:
                conn.commit()
        except db.Error:
            query = query % tr
            logger.warn("Failed on query:\n%s", query)
            raise

    cursor.close()
    if upd > 0:
        logger.info("Updated %s known transients" % (upd,))
    return upd


def _insert_transients(transients):
    """Insert newly identified transient sources into the transients table.

    *Args*:
      - transients: list of dictionaries representing new transient entries. 

     *Returns:*
     Number of entries inserted. 
    """

    conn = DataBase().connection
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
      (%(runcat)s
      ,%(band)s
      ,%(siglevel)s
      ,%(v_int)s
      ,%(eta_int)s
      ,%(trigger_xtrsrc)s
      )
    """
    ins = 0
    cursor = conn.cursor()
    for entry in transients:
            try:
                ins += cursor.execute(query, entry)
                if not AUTOCOMMIT:
                    conn.commit()

            except db.Error:
                query = query % entry
                logger.warn("Failed on query:\n%s", query)
                raise
    cursor.close()
    logger.info("Inserted %s new transients in transients table" % (ins,))



def select_variability_indices(image_id, V_lim, eta_lim, minpoints):
    """
    Select sources and integrated flux variability indices from the running
    catalog, for a given frequency band (i.e. image_id)

    This comes relatively easily, since we have kept track of the
    average fluxes and the variance measures, and thus can quickly
    obtain any sources that exceed a constant flux by a certain amount.

    We select those sources that have integrated-flux V-indexes (variability) and
    eta-indexes (reduced-chi-sq values) larger than the specified limits,
    with a minimum number of points ('minpoints') in the lightcurve. 

    We also perform a left outer join with the transient table, 
    to determine if the source has been inserted into that table yet. 
    This allows us to distinguish newly identified transients.

    NB Variability index  = std.dev(flux) / mean(flux).
    In the pathological case where mean(flux)==0.0, we simply substitute
    variability index =  std.dev(flux) / 1e-6 (1 microJansky)
    to avoid division by zero errors.

    (TO DO: Return indices based on
    peak fluxes as well.)

    *Args*:
      - image_id: the image and thus frequency band being searched for variability
      - V_lim: Minimum normalised variance value for transients. 
      - eta_lim: Minimum reduced chi-sq value for transients.
      - minpoints: Minimum number of lightcurve points to be considered a candidate.

    *Returns*:
    A list of dicts with keys as follows:
        [{ runcat, band, f_datapoints,
        wm_ra, wm_decl, wm_ra_err, wm_decl_err,
        v_int, eta_int, trigger_xtrsrc, new_transient }]
    """

    results = []
    try:
        conn = DataBase().connection
        cursor = conn.cursor()
#        Note: We cannot trivially calculate an updated 'siglevel' probability,
#        and selecting it from transients gives the *old* value.
#        So; we recalculate it later, (using scipy.stats),
#        and apply a threshold there.

        query = """\
SELECT t1.runcat
      ,t1.band
      ,t1.f_datapoints
      ,t1.wm_ra
      ,t1.wm_decl
      ,t1.wm_ra_err
      ,t1.wm_decl_err
      ,t1.V_int_inter / t1.avg_f_int AS v_int
      ,t1.eta_int_inter / t1.avg_f_int_weight AS eta_int
      ,CASE WHEN tr0.trigger_xtrsrc IS NULL
            THEN t1.xtrsrc 
            ELSE tr0.trigger_xtrsrc 
       END AS trigger_xtrsrc
      ,CASE WHEN tr0.trigger_xtrsrc IS NULL
            THEN TRUE
            ELSE FALSE
       END AS new_transient
  FROM (SELECT rf0.runcat
              ,rf0.band
              ,f_datapoints
              ,wm_ra
              ,wm_decl
              ,wm_ra_err
              ,wm_decl_err
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
              ,a0.xtrsrc
          FROM runningcatalog rc0
              ,runningcatalog_flux rf0
              ,image i0
              ,assocxtrsource a0
              ,extractedsource x0
         WHERE i0.id = %(imgid)s
           AND rc0.dataset = i0.dataset
           AND rc0.id = rf0.runcat
           AND rf0.band = i0.band
           AND rc0.id = a0.runcat
           AND a0.xtrsrc = x0.id
           AND x0.image = %(imgid)s
           AND f_datapoints > %(minpoints)s
       ) t1
       LEFT OUTER JOIN transient tr0
       ON t1.runcat = tr0.runcat
       AND t1.band = tr0.band
 WHERE t1.V_int_inter / t1.avg_f_int > %(v_lim)s
   AND t1.eta_int_inter / t1.avg_f_int_weight > %(eta_lim)s
ORDER BY t1.runcat
        ,t1.band
"""
        qry_params = {'imgid':image_id, 'v_lim': V_lim, 'eta_lim': eta_lim,
                      'minpoints':minpoints}
        cursor.execute(query, qry_params)
        results = generic.get_db_rows_as_dicts(cursor)
        if not AUTOCOMMIT:
            conn.commit()
        cursor.close()
    except db.Error:
        query = query % qry_params
        logger.warn("Query failed:\n%s", query)
        raise

    return results


def transient_search(image_id,
                     eta_lim,
                     V_lim,
                     probability_threshold,
                     minpoints):
    """
    Calculates fresh variability indices, then updates transients table accordingly.

    Be aware of the difference between a newly detected source at 
    some epoch and a source turning into a variable/transient due
    to significant flux changes. The former is picked up by the
    association procedure, while the latter is picked up by
    the transient search procedure.

    Transients are stored in the transient table,
    as well as in the monitoringlist (done by the association recipe),
    to ensure it is measured even when it drops below the threshold.
    Transient behaviour is checked per frequency band,
    because we assume that fluxes are not comparable across bands.
    
    *Returns*:
    A list of dicts with keys as follows:
        [{ runcat, band, f_datapoints,
        wm_ra, wm_decl, wm_ra_err, wm_decl_err,
        v_int, eta_int, 'siglevel', 
        trigger_xtrsrc, new_transient }]
    """

    # TODO: We want the trigger_xtrsrc here as well
    results = select_variability_indices(image_id, V_lim, eta_lim, minpoints)

    transients = []
    for candidate in results:
        probability_not_flat = 1 - chisqprob(candidate['eta_int'] * (candidate['f_datapoints'] - 1),
                                             (candidate['f_datapoints'] - 1))
        candidate['siglevel'] = float(probability_not_flat) #Monetdb doesn't like numpy.float64
        if candidate['siglevel'] > probability_threshold:
            transients.append(candidate)
        # TODO: 
        # What do we do with transients that start as transient, but as
        # more data is collected the siglevel decreases below the threshold?
        # Should they get removed from the transient table?
    _update_known_transients(transients)
    new_transients = [entry for entry in transients if entry['new_transient']]
    _insert_transients(new_transients)

    return transients
