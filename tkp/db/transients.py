"""
A collection of back end subroutines (mostly SQL queries).

This module contains the routines dealing with analysis of transients,
mostly involving the 'transient' table.

"""
import logging
from scipy.stats import chisqprob

import tkp.db
from tkp.db.generic import get_db_rows_as_dicts
from tkp.utility import substitute_nan


logger = logging.getLogger(__name__)


def _update_known_transients(transients):
    """Update the known transient sources in the database.

    Used when new measurements were made, changing variability indices.

    *Args*:
       - list of dictionaries representing transient entries.

     *Returns:*
     Number of entries updated.
    """
    query = """\
UPDATE transient
   SET siglevel = %(siglevel)s
      ,V_int = %(v_int)s
      ,eta_int = %(eta_int)s
 WHERE runcat = %(runcat)s
   AND band = %(band)s
    """
    upd = 0
    for tr in transients:
        cursor = tkp.db.execute(query, tr, commit=False)
        upd += cursor.rowcount
    tkp.db.commit()
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
    for entry in transients:
        cursor = tkp.db.execute(query, entry, commit=False)
        ins += cursor.rowcount
    tkp.db.commit()
    logger.info("Inserted %s new transients in transients table" % (ins,))


def _select_updated_variability_indices(image_id):
    """
    Select sources and integrated flux variability indices, for sources which
    have had an extra datapoint added by the specified image.

    As part of the results we return a field 'new_transient' which is TRUE
    if the runcat-source/band combination does not yet have an entry in the
    transient table.

    NB Variability index  = std.dev(flux) / mean(flux).
    In the pathological case where mean(flux)==0.0, we simply substitute
    variability index =  std.dev(flux) / 1e-6 (1 microJansky)
    to avoid division by zero errors.

    (TO DO: Return indices based on
    peak fluxes as well.)

    *Args*:
      - image_id: the image and thus frequency band being searched for variability

    *Returns*:
    A list of dicts with keys as follows:
        [{ runcat, band, f_datapoints,
        wm_ra, wm_decl, wm_uncertainty_ew, wm_uncertainty_ns,
        v_int, eta_int, trigger_xtrsrc, new_transient }]
    """

    #  Note: We cannot trivially calculate an updated 'siglevel' probability,
    #  and selecting it from transients gives the *old* value.
    #  So; we recalculate it later, (using scipy.stats),
    #  and apply a threshold there.
    #  NB We also perform a left outer join with the transient table,
    #  to determine if the source has been inserted into that table yet.
    #  This allows us to distinguish newly identified transients.
    query = """\
SELECT t1.runcat
      ,t1.band
      ,t1.f_datapoints
      ,t1.wm_ra
      ,t1.wm_decl
      ,t1.wm_uncertainty_ew
      ,t1.wm_uncertainty_ns
      ,t1.v_int
      ,t1.eta_int
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
              ,wm_uncertainty_ew
              ,wm_uncertainty_ns
              ,a0.v_int
              ,a0.eta_int
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
       ) t1
       LEFT OUTER JOIN transient tr0
       ON t1.runcat = tr0.runcat
       AND t1.band = tr0.band
ORDER BY t1.runcat
        ,t1.band
"""
    qry_params = {'imgid':image_id}
    cursor = tkp.db.execute(query, qry_params)
    results = get_db_rows_as_dicts(cursor)
    return results


def multi_epoch_transient_search(image_id,
                     eta_lim,
                     V_lim,
                     probability_threshold,
                     minpoints):
    """
    Updates transients table and returns a list of all currently valid
    multiple-epoch transients.

    (Be aware of the difference between a newly detected source at
    some epoch and a source turning into a variable/transient due
    to significant flux changes. The former is identified in the
    association procedure, while the latter is identified inspecting the
    variability indices, here.)

    Transients are stored in the transient table,
    as well as in the monitoringlist (done by the association recipe),
    to ensure it is measured even when it drops below the threshold.

    Transient behaviour is checked per frequency band,
    because we assume that fluxes are not comparable across bands.

    *Returns*:
    A list of dicts representing currently valid transients, i.e. those that
    satisfy the variability criteria given,
    with keys as follows:
        [{ runcat, band, f_datapoints,
        wm_ra, wm_decl, wm_uncertainty_ew, wm_uncertainty_ns,
        v_int, eta_int, 'siglevel',
        trigger_xtrsrc, new_transient }]
    """
    ##Bit of a kludge here:
    ## We want to update *all* transient entries, even if they have dropped below
    ## the 'new transient' selection criteria.
    ## Since the updating is done in a separate query anyway, we might as well just
    ## select all variability indices, and filter the results in python.

    ## NB we cannot even sensibly limit our indices query by minpoints,
    ## since we must update old entries which only just received their
    ## second datapoint (i.e. transients in last timestep).


    updated_variability_indices = _select_updated_variability_indices(image_id)

    #Calculate updated siglevels:
    for entry in updated_variability_indices:
        probability_not_flat = 1 - chisqprob(entry['eta_int'] * (entry['f_datapoints'] - 1),
                                             (entry['f_datapoints'] - 1))

        # If the above is not NaN, we use it; otherwise, 0.
        # The call to float() converts to a type suits the DB-API.
        entry['siglevel'] = float(substitute_nan(probability_not_flat))

    old_transients = [entry for entry in updated_variability_indices
                            if not entry['new_transient']]
    _update_known_transients(old_transients)

    filtered_transients = []
    for candidate in updated_variability_indices:
        if candidate['v_int'] > V_lim:
            if candidate['eta_int'] > eta_lim:
                if candidate['siglevel'] > probability_threshold:
                    if candidate['f_datapoints'] > minpoints:
                        filtered_transients.append(candidate)

    new_transients = [entry for entry in filtered_transients if entry['new_transient']]
    _insert_transients(new_transients)
    return filtered_transients
