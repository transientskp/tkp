import os
import logging
import tkp.database.utils as dbu
from lofar.parameterset import parameterset

logger = logging.getLogger(__name__)


def search_transients(image_id, parset, tkpconfigdir=None):
    if tkpconfigdir:   # allow nodes to pick up the TKPCONFIGDIR
        os.environ['TKPCONFIGDIR'] = tkpconfigdir
    from tkp.config import config

    # parset default values:
    logger.info("Finding transient sources...")
    parset = parameterset(parset)
    eta_lim = parset.getFloat('probability.eta_lim', config['transient_search']['eta_lim'])
    V_lim= parset.getFloat('probability.V_lim', config['transient_search']['V_lim'])
    prob_threshold = parset.getFloat('probability.threshold', config['transient_search']['probability'])
    minpoints = parset.getInt('probability.minpoints', config['transient_search']['minpoints'])

    transients = dbu.transient_search(image_id = image_id,
                                      eta_lim = eta_lim,
                                      V_lim = V_lim,
                                      probability_threshold = prob_threshold,
                                      minpoints = minpoints)

    return transients


