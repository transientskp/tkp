import os
import logging
from tkp.database import DataBase, DataSet
import tkp.database.utils as dbu
from lofar.parameterset import parameterset

logger = logging.getLogger(__name__)

def search_transients(image_ids, dataset_id, parset, tkpconfigdir=None):

    if tkpconfigdir:   # allow nodes to pick up the TKPCONFIGDIR
        os.environ['TKPCONFIGDIR'] = tkpconfigdir
    from tkp.config import config

    # parset default values:
    logger.info("Finding transient sources in the database")
    parset = parameterset(parset)
    database = DataBase()
    dataset = DataSet(id=dataset_id, database=database)
    eta_lim = parset.getFloat('probability.eta_lim', config['transient_search']['eta_lim'])
    V_lim= parset.getFloat('probability.V_lim', config['transient_search']['V_lim'])
    prob_threshold = parset.getFloat('probability.threshold', config['transient_search']['probability'])
    minpoints = parset.getInt('probability.minpoints', config['transient_search']['minpoints'])

    transient_ids, siglevels, transients = dbu.transient_search(
        conn = database.connection,
        dataset = dataset,
        eta_lim = eta_lim,
        V_lim = V_lim,
        probability_threshold = prob_threshold,
        minpoints = minpoints,
        image_ids=image_ids,
        logger=None)

    logger.info("found %s transients! woohoo! yeah!" % len(transients))

    return {
        'transient_ids': map(int, transient_ids),
        'siglevels': siglevels,
        'transients':transients,
    }


