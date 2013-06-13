import logging
from tkp.db.transients import multi_epoch_transient_search
import tkp.utility.parset as parset
import ConfigParser
logger = logging.getLogger(__name__)


def search_transients(image_id, parset):
   logger.info("Finding transient sources...")
   transients = multi_epoch_transient_search(image_id=image_id,
                                             eta_lim=parset['eta_lim'],
                                             V_lim=parset['v_lim'],
                                             probability_threshold=parset['threshold'],
                                             minpoints=parset['minpoints'])
   return transients


