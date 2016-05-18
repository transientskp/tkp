"""
The main pipeline logic, from where all other components are called.
"""
import imp
import logging
import os
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
from tkp.steps.persistence import create_dataset, store_images
import tkp.steps.forced_fitting as steps_ff
from tkp.steps.varmetric import execute_store_varmetric


logger = logging.getLogger(__name__)


def run(job_name, supplied_mon_coords=[]):
    pipe_config = initialize_pipeline_config(
        os.path.join(os.getcwd(), "pipeline.cfg"),
        job_name)

    # get parallelise props. Defaults to multiproc with autodetect num cores
    parallelise = pipe_config.get('parallelise', {})
    distributor = os.environ.get('TKP_PARALLELISE', parallelise.get('method',
                                                                    'multiproc'))
    runner = Runner(distributor=distributor,
                    cores=parallelise.get('cores', 0))


    #Setup logfile before we do anything else
    log_dir = pipe_config.logging.log_dir
    setup_logging(log_dir,
                  debug=pipe_config.logging.debug,
                  use_colorlog=pipe_config.logging.colorlog
                  )

    job_dir = pipe_config.DEFAULT.job_directory
    if not os.access(job_dir, os.X_OK):
        msg = "can't access job folder %s" % job_dir
        logger.error(msg)
        raise IOError(msg)
    logger.info("Job dir: %s", job_dir)

    db_config = get_database_config(pipe_config.database, apply=True)
    dump_database_backup(db_config, job_dir)

    job_config = load_job_config(pipe_config)
    se_parset = job_config.source_extraction
    deruiter_radius = job_config.association.deruiter_radius
    beamwidths_limit = job_config.association.beamwidths_limit
    new_src_sigma = job_config.transient_search.new_source_sigma_margin

    all_images = imp.load_source('images_to_process',
                                 os.path.join(job_dir,
                                              'images_to_process.py')).images

    logger.info("dataset %s contains %s images" % (job_name, len(all_images)))

    logger.info("performing database consistency check")
    if not dbconsistency.check():
        logger.error("Inconsistent database found; aborting")
        return 1

    sync_rejectreasons(tkp.db.Database().Session())

    dataset_id = create_dataset(job_config.persistence.dataset_id,
                                job_config.persistence.description)

    if job_config.persistence.dataset_id == -1:
        store_config(job_config, dataset_id)  # new data set
        if supplied_mon_coords:
            dbgen.insert_monitor_positions(dataset_id,supplied_mon_coords)
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

    dump_configs_to_logdir(log_dir, job_config, pipe_config)

    logger.info("performing persistence step")
    image_cache_params = pipe_config.image_cache
    imgs = [[img] for img in all_images]

    rms_est_sigma = job_config.persistence.rms_est_sigma
    rms_est_fraction = job_config.persistence.rms_est_fraction
    metadatas = runner.map("persistence_node_step", imgs,
                           [image_cache_params, rms_est_sigma, rms_est_fraction])
    metadatas = [m[0] for m in metadatas if m]

    logger.info("Storing images")
    image_ids = store_images(metadatas,
                             job_config.source_extraction.extraction_radius_pix,
                             dataset_id)

    db_images = [Image(id=image_id) for image_id in image_ids]

    logger.info("performing quality check")
    urls = [img.url for img in db_images]
    arguments = [job_config]
    rejecteds = runner.map("quality_reject_check", urls, arguments)

    good_images = []
    for image, rejected in zip(db_images, rejecteds):
        if rejected:
            reason, comment = rejected
            steps.quality.reject_image(image.id, reason, comment)
        else:
            good_images.append(image)

    if not good_images:
        logger.warn("No good images under these quality checking criteria")
        return

    grouped_images = group_per_timestep(good_images)
    timestep_num = len(grouped_images)
    for n, (timestep, images) in enumerate(grouped_images):
        msg = "processing %s images in timestep %s (%s/%s)"
        logger.info(msg % (len(images), timestep, n+1, timestep_num))

        logger.debug("performing source extraction")
        urls = [img.url for img in images]
        arguments = [se_parset]

        extraction_results = runner.map("extract_sources", urls, arguments)

        logger.debug("storing extracted sources to database")
        # we also set the image max,min RMS values which calculated during
        # source extraction
        for image, results in zip(images, extraction_results):
            image.update(rms_min=results.rms_min, rms_max=results.rms_max,
                detection_thresh=se_parset['detection_threshold'],
                analysis_thresh=se_parset['analysis_threshold'])
            dbgen.insert_extracted_sources(image.id, results.sources, 'blind')

        for image in images:
            logger.info("performing DB operations for image {} ({})".format(
                image.id, image.url))

            dbass.associate_extracted_sources(image.id,
                                              deRuiter_r=deruiter_radius,
                                              new_source_sigma_margin=new_src_sigma)

            expiration = job_config.source_extraction.expiration
            all_fit_posns, all_fit_ids = steps_ff.get_forced_fit_requests(image,
                                                                          expiration)
            if all_fit_posns:
                successful_fits, successful_ids = steps_ff.perform_forced_fits(
                    all_fit_posns, all_fit_ids, image.url, se_parset)

                steps_ff.insert_and_associate_forced_fits(image.id,successful_fits,
                                                          successful_ids)


        dbgen.update_dataset_process_end_ts(dataset_id)

    logger.info("calculating variability metrics")
    execute_store_varmetric(dataset_id)
