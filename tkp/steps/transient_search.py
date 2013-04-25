import logging
from tkp.db.transients import multi_epoch_transient_search
from lofar.parameterset import parameterset

logger = logging.getLogger(__name__)


def parse_parset(parset_file):
    parset = parameterset(parset_file)
    return {
        'eta_lim': parset.getFloat('eta_lim'),
        'V_lim': parset.getFloat('V_lim'),
        'threshold': parset.getFloat('threshold'),
        'minpoints': parset.getInt('minpoints'),
    }


def search_transients(image_id, parset):
   logger.info("Finding transient sources...")
   transients = multi_epoch_transient_search(image_id=image_id,
                                             eta_lim=parset['eta_lim'],
                                             V_lim=parset['V_lim'],
                                             probability_threshold=parset['threshold'],
                                             minpoints=parset['minpoints'])
   return transients


