import logging
import json
from tkp.db.database import Database
from tkp.db.orm import DataSet

logger = logging.getLogger(__name__)


def add_manual_monitoringlist_entries(dataset_id, monitor_coords):
    """Parses co-ords from self.inputs, loads them into the monitoringlist"""
    if len(monitor_coords):
        logger.info( "You specified monitoring at coords:")
        for i in monitor_coords:
            logger.info( "RA, %f ; Dec, %f " % (i[0],i[1]))
    for c in monitor_coords:
        dataset = DataSet(id=dataset_id, database=Database())
        dataset.add_manual_entry_to_monitoringlist(c[0],c[1])
    return True
