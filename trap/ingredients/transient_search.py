import os
import logging
from tkp.database import DataBase, DataSet
import tkp.database.utils as dbu
from lofar.parameterset import parameterset

logger = logging.getLogger(__name__)

def search_transients_per_dataset(database, image_ids, dataset_id, parset, tkpconfigdir=None):

    if tkpconfigdir:   # allow nodes to pick up the TKPCONFIGDIR
        os.environ['TKPCONFIGDIR'] = tkpconfigdir
    from tkp.config import config

    # parset default values:
    logger.info("Finding transient sources in the database")
    parset = parameterset(parset)
    #database = DataBase()
    conn = database.connection
    #logger.info("Y: DATABASE CONNECTION: %s" % (conn))
    dataset = DataSet(id=dataset_id, database=database)
    eta_lim = parset.getFloat('probability.eta_lim', config['transient_search']['eta_lim'])
    V_lim= parset.getFloat('probability.V_lim', config['transient_search']['V_lim'])
    prob_threshold = parset.getFloat('probability.threshold', config['transient_search']['probability'])
    minpoints = parset.getInt('probability.minpoints', config['transient_search']['minpoints'])

    all_transient_ids = []
    all_siglevels = []
    all_transients = []
    for band in dataset.frequency_bands():
        if image_ids:
            transient_ids, siglevels, transients = dbu.transient_search_per_dataset(
                conn=database.connection,
                dsid=dataset.id,
                freq_band=band,
                eta_lim=eta_lim,
                V_lim=V_lim,
                probability_threshold=prob_threshold,
                minpoints=minpoints,
                imageid=image_ids[0])

        logger.info("Found %s transients in band %s." % (len(transients), band))
        all_transient_ids.extend(transient_ids)
        all_siglevels.extend(siglevels)
    
    return {
        'transient_ids': map(int, all_transient_ids),
        'siglevels': all_siglevels,
        'transients':all_transients,
    }

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


