"""
A collection of back end subroutines (mostly SQL queries).

This module contains the routines dealing with analysis of transients,
mostly involving the 'transient' table.

"""
import logging
import monetdb.sql as db
from tkp.config import config
from scipy.stats import chisqprob
from tkp.database.database import DataBase
from tkp.classification.transient import Transient

logger = logging.getLogger(__name__)

AUTOCOMMIT = config['database']['autocommit']

def _update_known_transients(transients): 
    """Update the known transient sources in the database,
    ie. for which the runcatid is known.
    
    New measurements were made, changing positions and variability indices.
    
    If they are not known, ie, a new source was detected, 
    they have been picked up by the association procedure, and
    inserted in all the corresponding tables:
    runcat, runcat_flux, assocxtrsource, monlist, transient.
    
    Transients are stored in the transient table,
    as well as in the monitoringlist (done by the association recipe),
    to ensure it is measured even when it drops below the threshold.
    Transient behaviour is checked per frequency band,
    because we assume that fluxes are not comparable across bands.
    """

    try:
        conn = DataBase().connection
        cursor = conn.cursor()
        query = """\
        UPDATE transient
           SET siglevel = %s
              ,V_int = %s
              ,eta_int = %s
         WHERE runcat = %s
           AND band = %s
        """
        upd = 0
        for i in range(len(transients)):
            upd += cursor.execute(query, (float(transients[i].siglevel),
                                          float(transients[i].V_int),
                                          float(transients[i].eta_int),
                                          transients[i].runcatid,
                                          transients[i].band))
            if not AUTOCOMMIT:
                conn.commit()
        cursor.close()
        if upd > 0:
            logger.info("Updated %s known transients" % (upd,))
    except db.Error:
        query = query % (float(transients[i].siglevel),
                         float(transients[i].V_int),
                         float(transients[i].eta_int),
                         transients[i].runcat,
                         transients[i].band)
        logger.warn("Failed on query:\n%s", query)
        raise

def _insert_new_transients(image_id, transients, prob_threshold): 
    """Insert new transient sources in the database,
    ie those for which no runcat id exists yet.
    
    If there are known, picked up at an earlier epoch, 
    they will be updated by _update_known_transients().
    
    Be aware of the difference between a newly detected source at 
    some epoch and a source turning into a variable/transient due
    to significant flux changes. The former is picked up by the
    association procedure, while the latter is picked up by
    the transient search procedure.

    Transients are stored in the transient table,
    as well as in the monitoringlist (done by the association recipe),
    to ensure it is measured even when it drops below the threshold.
    Transient behaviour is checked per frequency band,
    Transient behaviour is checked per frequency band,
    because we assume that fluxes are not comparable across bands.
    """

    try:
        conn = DataBase().connection
        cursor = conn.cursor()
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
        ins = 0
        for i in range(len(transients)):
            if not transients[i].monitored:
                if transients[i].siglevel > prob_threshold:
                    ins += cursor.execute(query, (transients[i].runcatid,
                                              transients[i].band,
                                              float(transients[i].siglevel),
                                              float(transients[i].V_int),
                                              float(transients[i].eta_int),
                                              transients[i].trigger_xtrsrc))
                    if not AUTOCOMMIT:
                        conn.commit()
        cursor.close()
        if ins == 0:
            logger.info("No new transients found in image %s" % (image_id))
        else:
            logger.info("Inserted %s new transients in transients table" % (ins,))
    except db.Error:
        query = query % (transients[i].runcat,
                         transients[i].band,
                         float(transients[i].siglevel),
                         float(transients[i].V_int),
                         float(transients[i].eta_int),
                         transients[i].trigger_xtrsrc,
                         transients[i].runcat)
        logger.warn("Failed on query:\n%s", query)
        raise


def select_variability_indices(image_id, V_lim, eta_lim, prob_threshold):
    """
    Select sources and integrated flux variability indices from the running
    catalog, for a given frequency band (i.e. image_id)

    This comes relatively easily, since we have kept track of the
    average fluxes and the variance measures, and thus can quickly
    obtain any sources that exceed a constant flux by a certain amount.

    We select those sources that have integrated-flux V-indexes (variability) and
    eta-indexes (reduced-chi-sq values) larger than the specified limits.

    We also perform a left outer join with the monitoringlist and the
    transient tables, to determine if the source has been inserted into those
    tables yet. TODO: Why?
    
    NB Variability index  = std.dev(flux) / mean(flux).
    In the pathological case where mean(flux)==0.0, we simply substitute
    variability index =  std.dev(flux) / 1e-6 (1 microJansky)
    to avoid division by zero errors.

    (TO DO: Return indices based on
    peak fluxes as well.)

    Args:

        dsid (int): dataset of interest

        image_id: the image and thus frequency band being searched for variability

        V_lim (): 

        eta_lim ():
    """

    results = []
    try:
        conn = DataBase().connection
        cursor = conn.cursor()
        query = """\
SELECT t1.runcat
      ,t1.band
      ,t1.f_datapoints
      ,t1.wm_ra
      ,t1.wm_decl
      ,t1.wm_ra_err
      ,t1.wm_decl_err
      ,t1.V_int_inter / t1.avg_f_int AS V_int
      ,t1.eta_int_inter / t1.avg_f_int_weight AS eta_int
      ,CASE WHEN tr0.trigger_xtrsrc IS NULL
            THEN t1.xtrsrc 
            ELSE tr0.trigger_xtrsrc 
       END AS trigger_xtrsrc
      ,CASE WHEN tr0.trigger_xtrsrc IS NULL
            THEN FALSE 
            ELSE TRUE
       END AS monitored
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
         WHERE i0.id = %s
           AND rc0.dataset = i0.dataset
           AND rc0.id = rf0.runcat
           AND rf0.band = i0.band
           AND rc0.id = a0.runcat
           AND a0.xtrsrc = x0.id
           AND x0.image = %s
       ) t1
       LEFT OUTER JOIN transient tr0
       ON t1.runcat = tr0.runcat
       AND t1.band = tr0.band
 WHERE t1.V_int_inter / t1.avg_f_int > %s
   AND t1.eta_int_inter / t1.avg_f_int_weight > %s
   AND (tr0.siglevel > %s
        OR tr0.siglevel IS NULL)
ORDER BY t1.runcat
        ,t1.band
"""
        cursor.execute(query, (image_id, image_id, V_lim, eta_lim, prob_threshold))

        results = zip(*cursor.fetchall())
        if not AUTOCOMMIT:
            conn.commit()
        cursor.close()
    except db.Error:
        query = query % (image_id, image_id, V_lim, eta_lim, prob_threshold)
        logger.warn("Query failed:\n%s", query)
        raise
    
    return results

def transient_search(image_id,
                     eta_lim,
                     V_lim,
                     probability_threshold,
                     minpoints):

    # TODO: We want the trigger_xtrsrc here as well
    results = select_variability_indices(image_id, V_lim, eta_lim, probability_threshold)
    
    transients = []
    if len(results) > 0:
        runcatid = results[0]
        band = results[1][0] # all from same band, one (eg the first) is enough
        f_datapoints = results[2]
        wm_ra = results[3]
        wm_decl = results[4]
        wm_ra_err = results[5]
        wm_decl_err = results[6]
        V_int = results[7]
        eta_int = results[8]
        trigger_xtrsrc = results[9]
        monitored = results[10]

        for i in range(len(runcatid)):
            prob = 1 - chisqprob(eta_int[i] * (f_datapoints[i] - 1), (f_datapoints[i] - 1))
            transient = Transient()
            transient.runcatid = runcatid[i]
            transient.band = band
            transient.f_datapoints = f_datapoints[i]
            transient.ra = wm_ra[i]
            transient.decl = wm_decl[i]
            transient.V_int = V_int[i]
            transient.eta_int = eta_int[i]
            transient.trigger_xtrsrc = trigger_xtrsrc[i]
            transient.monitored = monitored[i]
            # TODO: Why is this called siglevel, while it is a probability?
            transient.siglevel = prob
            transients.append(transient)

        #for i in range(len(transients)):
        #    print "transients[",i,"].runcat =", transients[i].runcat, \
        #          "; band =", transients[i].band, \
        #          "; trigger_xtrsrc =", transients[i].trigger_xtrsrc, \
        #          "; monitored =", transients[i].monitored, \
        #          "; siglevel (prob) =", transients[i].siglevel

        # TODO: 
        # What do we do with transients that start as transient, but as
        # more data is collected the siglevel decreases below the threshold?
        # Should they get removed from the transient table?
        _update_known_transients(transients)
        _insert_new_transients(image_id, transients, probability_threshold)

    return transients
