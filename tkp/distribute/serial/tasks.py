from __future__ import absolute_import
import logging
import tkp.steps
from tkp.steps.misc import ImageMetadataForSort
from tkp.steps.forced_fitting import perform_forced_fits

logger = logging.getLogger(__name__)


def extract_metadatas(accessors, sigma, f):
    logger.debug("running extract metadatas task")
    return tkp.steps.persistence.extract_metadatas(accessors, sigma, f)


def open_as_fits(images):
    logger.debug("opening files as fits objects")
    return tkp.steps.persistence.paths_to_fits(images)


def quality_reject_check(accessor, job_config):
    logger.debug("running quality task")
    return tkp.steps.quality.reject_check(accessor, job_config)


def extract_sources(accessor, extraction_params):
    logger.debug("running extracted sources task")
    return tkp.steps.source_extraction.extract_sources(accessor,
                                                       extraction_params)


def get_accessors(images):
    logger.debug("Creating accessors for images")
    return tkp.steps.persistence.get_accessors(images)


def get_metadata_for_ordering(images):
    """
    args:
        images (list): list of image urls
    returns:
        list: of ImageMetadataForSort
    """
    logger.debug("Retrieving ordering metadata from accessors")
    l = []
    for a in tkp.steps.persistence.get_accessors(images):
        l.append(ImageMetadataForSort(url=a.url, timestamp=a.taustart_ts,
                                      frequency=a.freq_eff))
    return l


def forced_fits(zipped):
    logger.debug("running forced fits task")
    accessor, db_image_id, fit_posns, fit_ids, extraction_params = zipped
    successful_fits, successful_ids = perform_forced_fits(fit_posns, fit_ids,
                                                          accessor,
                                                          extraction_params)
    return successful_fits, successful_ids, db_image_id