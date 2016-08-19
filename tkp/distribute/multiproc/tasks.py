"""
Parallisable tasks used with python multiprocessing
"""
from __future__ import absolute_import
import logging
import tkp.steps
from tkp.steps.misc import ImageMetadataForSort
from tkp.steps.forced_fitting import perform_forced_fits

logger = logging.getLogger(__name__)


def extract_metadatas(zipped):
    logger.debug("running extract metadatas task")
    images, args = zipped
    sigma, f = args
    return tkp.steps.persistence.extract_metadatas(images, sigma, f)


def open_as_fits(zipped):
    logger.debug("opening files as fits objects")
    images, args = zipped
    return list(tkp.steps.persistence.paths_to_fits(images))


def quality_reject_check(zipped):
    logger.debug("running quality task")
    url, args = zipped
    job_config = args[0]
    return tkp.steps.quality.reject_check(url, job_config)


def extract_sources(zipped):
    logger.debug("running extracted sources task")
    accessor, args = zipped
    extraction_params = args[0]
    return tkp.steps.source_extraction.extract_sources(accessor,
                                                       extraction_params)


def forced_fits(zipped):
    logger.debug("running forced fits task")
    accessor, db_image_id, fit_posns, fit_ids, extraction_params = zipped[0]
    successful_fits, successful_ids = perform_forced_fits(fit_posns, fit_ids,
                                                          accessor,
                                                          extraction_params)
    return successful_fits, successful_ids, db_image_id


def get_accessors(zipped):
    logger.debug("Creating accessors for images")
    images, args = zipped
    return tkp.steps.persistence.get_accessors(images)


def get_metadata_for_ordering(zipped):
    logger.debug("Retrieving ordering metadata from accessors")
    images, args = zipped
    l = []
    for a in tkp.steps.persistence.get_accessors(images):
        l.append(ImageMetadataForSort(url=a.url, timestamp=a.taustart_ts,
                                      frequency=a.freq_eff))
    return l
