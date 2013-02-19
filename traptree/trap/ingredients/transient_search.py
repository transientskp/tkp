import os
import logging
import tkp.database.utils as dbu
from lofar.parameterset import parameterset

logger = logging.getLogger(__name__)


def search_transients(image_id, parset):
    logger.info("Finding transient sources...")
    parset = parameterset(parset)
    eta_lim = parset.getFloat('probability.eta_lim')
    V_lim= parset.getFloat('probability.V_lim')
    prob_threshold = parset.getFloat('probability.threshold')
    minpoints = parset.getInt('probability.minpoints')

    transients = dbu.transient_search(image_id = image_id,
                                      eta_lim = eta_lim,
                                      V_lim = V_lim,
                                      probability_threshold = prob_threshold,
                                      minpoints = minpoints)

    return transients


