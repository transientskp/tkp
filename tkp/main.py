"""
The main pipeline logic, from where all other components are called.
"""
import imp
import logging
import os
import sys
from tkp import steps
from tkp.config import initialize_pipeline_config, get_database_config
import tkp.db
from tkp.db import consistency as dbconsistency
from tkp.db import Image
from tkp.db import general as dbgen
from tkp.db import associations as dbass
from tkp.db.quality import sync_rejectreasons
from tkp.distribute import Runner
from tkp.steps.misc import (load_job_config, dump_configs_to_logdir,
                            check_job_configs_match,
                            setup_logging, dump_database_backup,
                            group_per_timestep
                            )
from tkp.db.configstore import store_config, fetch_config
from tkp.steps.persistence import create_dataset, store_images_in_db
import tkp.steps.forced_fitting as steps_ff
from tkp.steps.varmetric import execute_store_varmetric


logger = logging.getLogger(__name__)


def setup(job_name, supplied_mon_coords=None):
    """
    Initialises the pipeline run.
    """
    if not supplied_mon_coords:
        supplied_mon_coords = []

    pipe_config = initialize_pipeline_config(
        os.path.join(os.getcwd(), "pipeline.cfg"),
        job_name)

    # get parallelise props. Defaults to multiproc with autodetect num cores
    distributor = os.environ.get('TKP_PARALLELISE', pipe_config.parallelise.method)
    runner = Runner(distributor=distributor, cores=pipe_config.parallelise.cores)

    # Setup logfile before we do anything else
    log_dir = pipe_config.logging.log_dir
    setup_logging(log_dir, debug=pipe_config.logging.debug,
                  use_colorlog=pipe_config.logging.colorlog)

    job_dir = pipe_config.DEFAULT.job_directory
    if not os.access(job_dir, os.X_OK):
        msg = "can't access job folder %s" % job_dir
        logger.error(msg)
        sys.exit(1)
    logger.info("Job dir: %s", job_dir)

    db_config = get_database_config(pipe_config.database, apply=True)
    dump_database_backup(db_config, job_dir)

    job_config = load_job_config(pipe_config)
    dump_configs_to_logdir(log_dir, job_config, pipe_config)

    sync_rejectreasons(tkp.db.Database().Session())

    job_config, dataset_id = initialise_dataset(job_config, supplied_mon_coords)

    return job_dir, job_config, pipe_config, runner, dataset_id


def load_images(job_name, job_dir, job_config):

    if job_config.pipeline.mode == 'batch':
        path = os.path.join(job_dir, 'images_to_process.py')
        all_images = imp.load_source('images_to_process', path).images
        logger.info("dataset %s contains %s images" % (job_name,
                                                       len(all_images)))
    else:
        # this is where the AARTFAAC magic will happen
        all_images = []
    return all_images


def consistency_check():
    logger.info("performing database consistency check")
    if not dbconsistency.check():
        logger.error("Inconsistent database found; aborting")
        sys.exit(1)


def initialise_dataset(job_config, supplied_mon_coords):
    dataset_id = create_dataset(job_config.persistence.dataset_id,
                                job_config.persistence.description)

    if job_config.persistence.dataset_id == -1:
        store_config(job_config, dataset_id)  # new data set
        if supplied_mon_coords:
            dbgen.insert_monitor_positions(dataset_id, supplied_mon_coords)
    else:
        job_config_from_db = fetch_config(dataset_id)  # existing data set
        if check_job_configs_match(job_config, job_config_from_db):
            logger.debug("Job configs from file / database match OK.")
        else:
            logger.warn("Job config file has changed since dataset was "
                        "first loaded into database. ")
            logger.warn("Using job config settings loaded from database, see "
                        "log dir for details")
        job_config = job_config_from_db
        if supplied_mon_coords:
            logger.warn("Monitor positions supplied will be ignored. "
                        "(Previous dataset specified)")
    return job_config, dataset_id


def store_mongodb(pipe_config, all_images, runner):
    logger.info("Storing copy of images in MongoDB")
    imgs = [[img] for img in all_images]
    runner.map("save_to_mongodb", imgs, [pipe_config.image_cache])


def extra_metadata(job_config, accessors, runner):
    logger.info("Extracting metadata from images")
    imgs = [[a] for a in accessors]
    metadatas = runner.map("extract_metadatas",
                           imgs,
                           [job_config.persistence.rms_est_sigma,
                            job_config.persistence.rms_est_fraction])
    metadatas = [m[0] for m in metadatas if m]
    return metadatas


def storing_images(metadatas, job_config, dataset_id):
    logger.info("Storing image metadata in SQL database")
    r = job_config.source_extraction.extraction_radius_pix
    image_ids = store_images_in_db(metadatas, r, dataset_id)
    db_images = [Image(id=image_id) for image_id in image_ids]
    return db_images


def quality_check(db_images, accessors, job_config, runner):
    logger.info("performing quality check")
    arguments = [job_config]
    rejecteds = runner.map("quality_reject_check", accessors, arguments)

    good_images = []
    for db_image, rejected, accessor in zip(db_images, rejecteds, accessors):
        if rejected:
            reason, comment = rejected
            steps.quality.reject_image(db_image.id, reason, comment)
        else:
            good_images.append((db_image, accessor))

    if not good_images:
        logger.warn("No good images under these quality checking criteria")
        sys.exit(1)
    return good_images


def source_extraction(accessors, job_config, runner):
    """
    args:
        images: a list of accessors
    """
    logger.debug("performing source extraction")
    arguments = [job_config.source_extraction]
    extraction_results = runner.map("extract_sources", accessors, arguments)
    return extraction_results


def store_extractions(images, extraction_results, job_config):
    logger.debug("storing extracted sources to database")
    # we also set the image max,min RMS values which calculated during
    # source extraction
    detection_thresh = job_config.source_extraction['detection_threshold']
    analysis_thresh = job_config.source_extraction['analysis_threshold']
    for (db_image, accessor), results in zip(images, extraction_results):
        db_image.update(rms_min=results.rms_min, rms_max=results.rms_max,
                        detection_thresh=detection_thresh,
                        analysis_thresh=analysis_thresh)
        dbgen.insert_extracted_sources(db_image.id, results.sources, 'blind')


def image_db_operations(db_image, accessor, job_config):
    logger.info("performing DB operations for image {} ({})".format(db_image.id,
                                                                    db_image.url))

    r = job_config.association.deruiter_radius
    s = job_config.transient_search.new_source_sigma_margin
    dbass.associate_extracted_sources(db_image.id, deRuiter_r=r,
                                      new_source_sigma_margin=s)

    expiration = job_config.source_extraction.expiration
    all_fit_posns, all_fit_ids = steps_ff.get_forced_fit_requests(db_image,
                                                                  expiration)
    if all_fit_posns:
        successful_fits, successful_ids = steps_ff.perform_forced_fits(
            all_fit_posns, all_fit_ids, accessor, job_config.source_extraction)

        steps_ff.insert_and_associate_forced_fits(db_image.id, successful_fits,
                                                  successful_ids)


def finalise(dataset_id):
    dbgen.update_dataset_process_end_ts(dataset_id)
    logger.info("calculating variability metrics")
    execute_store_varmetric(dataset_id)


def get_accessors(runner, all_images):
    imgs = [[img] for img in all_images]
    accessors = runner.map("get_accessors", imgs)
    return [a[0] for a in accessors if a]


def run(job_name, supplied_mon_coords=None):
    s = setup(job_name, supplied_mon_coords)
    job_dir, job_config, pipe_config, runner, dataset_id = s

    all_images = load_images(job_name, job_dir, job_config)

    store_mongodb(pipe_config, all_images, runner)

    # gather all image info.
    accessors = get_accessors(runner, all_images)
    metadatas = extra_metadata(job_config, accessors, runner)
    db_images = storing_images(metadatas, job_config, dataset_id)
    error = "%s != %s != %s" % (len(accessors), len(metadatas), len(db_images))
    assert len(accessors) == len(metadatas) == len(db_images), error

    good_images = quality_check(db_images, accessors, job_config, runner)
    grouped_images = group_per_timestep(good_images)

    for n, (timestep, images) in enumerate(grouped_images):
        msg = "processing %s images in timestep %s (%s/%s)"
        logger.info(msg % (len(images), timestep, n + 1, len(grouped_images)))
        accessors = [i[1] for i in images]
        extraction_results = source_extraction(accessors, job_config, runner)
        store_extractions(images, extraction_results, job_config)

        for (db_image, accessor) in images:
            image_db_operations(db_image, accessor, job_config)

    finalise(dataset_id)