import logging
import tkp.accessors
from tkp.accessors import sourcefinder_image_from_accessor
import tkp.accessors
from tkp.db import general as dbgen
from tkp.db import monitoringlist as dbmon
from tkp.db import nulldetections as dbnd

logger = logging.getLogger(__name__)


def get_forced_fit_requests(image, expiration):
    nd_requested_fits = dbnd.get_nulldetections(image.id, expiration)
    logger.info("Found %s null detections" % len(nd_requested_fits))
    mon_entries = dbmon.get_monitor_entries(image.dataset.id)

    all_fit_positions = []
    all_fit_ids = []

    all_fit_positions.extend([(nd[1],nd[2]) for nd in nd_requested_fits])
    all_fit_ids.extend([ ('ff_nd', nd[0]) for nd in nd_requested_fits])

    all_fit_positions.extend([(ms[1],ms[2]) for ms in mon_entries])
    all_fit_ids.extend([('ff_ms',ms[0]) for ms in mon_entries])

    return all_fit_positions, all_fit_ids


def insert_and_associate_forced_fits(image_id,successful_fits,successful_ids):
    assert len(successful_ids) == len(successful_fits)

    nd_extractions=[]
    nd_runcats=[]

    ms_extractions=[]
    ms_ids = []

    for idx, id in enumerate(successful_ids):
        if id[0] == 'ff_nd':
            nd_extractions.append(successful_fits[idx])
            nd_runcats.append(id[1])
        elif id[0] == 'ff_ms':
            ms_extractions.append(successful_fits[idx])
            ms_ids.append(id[1])
        else:
            raise ValueError("Forced fit type id not recognised:" + id[0])

    if nd_extractions:
        logger.info("adding null detections")
        dbgen.insert_extracted_sources(image_id, nd_extractions,
                                       extract_type='ff_nd',
                                       ff_runcat_ids=nd_runcats)
        dbnd.associate_nd(image_id)
    else:
        logger.info("No successful nulldetection fits")

    if ms_extractions:
        dbgen.insert_extracted_sources(image_id, ms_extractions,
                                       extract_type='ff_ms',
                                       ff_monitor_ids=ms_ids)
        logger.info("adding monitoring sources")
        dbmon.associate_ms(image_id)
    else:
        logger.info("No successful monitor fits")



def perform_forced_fits(fit_posns, fit_ids,
                        image_path, extraction_params):
    """
    Perform forced source measurements on an image based on a list of
    positions.

    Args:
        fit_posns (list): List of (RA, Dec) tuples: Positions to be fit.
        fit_ids: List of identifiers for each requested fit position.
        image_path (str): path to image for measurements.
        extraction_params (dict): source extraction parameters, as a dictionary.

    Returns:
        tuple: A matched pair of lists (serialized_fits, ids), corresponding to
        successfully fitted positions.
        NB returned lists may be shorter than input lists
        if some fits are unsuccessful.
    """
    logger.info("Forced fitting in image: %s" % (image_path))
    fitsimage = tkp.accessors.open(image_path)

    data_image = sourcefinder_image_from_accessor(fitsimage,
                    margin=extraction_params['margin'],
                    radius=extraction_params['extraction_radius_pix'],
                    back_size_x=extraction_params['back_size_x'],
                    back_size_y=extraction_params['back_size_y'])


    boxsize = extraction_params['box_in_beampix'] * max(data_image.beam[0],
                                             data_image.beam[1])
    successful_fits, successful_ids = data_image.fit_fixed_positions(
                                                fit_posns, boxsize, ids=fit_ids)
    if successful_fits:
        serialized =[
            f.serialize(
                extraction_params['ew_sys_err'], extraction_params['ns_sys_err'])
            for f in successful_fits]
        return serialized, successful_ids
    else:
        return [],[]
