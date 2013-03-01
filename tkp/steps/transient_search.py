import logging

from lofar.parameterset import parameterset

from tkp.database.transients import multi_epoch_transient_search


logger = logging.getLogger(__name__)


def search_transients(image_id, parset):
    logger.info("Finding transient sources...")
    parset = parameterset(parset)
    eta_lim = parset.getFloat('probability.eta_lim')
    V_lim= parset.getFloat('probability.V_lim')
    prob_threshold = parset.getFloat('probability.threshold')
    minpoints = parset.getInt('probability.minpoints')

    transients = multi_epoch_transient_search(image_id = image_id,
                                      eta_lim = eta_lim,
                                      V_lim = V_lim,
                                      probability_threshold = prob_threshold)

    return transients


