"""
Main pipeline logic is defined here.

The science logic is a bit entwined with celery-specific functionality.
This is somewhat unavoidable, since how a task is parallelised (or not) has
implications for the resulting logic.

In general, we try to keep functions elsewhere so this file is succinct.
The exceptions are a couple of celery-specific subroutines.
"""
import imp
import logging
import os
from celery import group
from tkp import steps
from tkp.config import initialize_pipeline_config, get_database_config
from tkp.db import consistency as dbconsistency
from tkp.db import Image
from tkp.db import general as dbgen
from tkp.db import monitoringlist as dbmon
from tkp.db import associations as dbass
from tkp.distribute.celery import celery_app
from tkp.distribute.celery import tasks
from tkp.distribute.celery.log import setup_event_listening
from tkp.distribute.common import setup_log_file, dump_database_backup
from tkp.distribute.common import load_job_config, dump_configs_to_logdir
from tkp.distribute.common import group_per_timestep
from tkp.steps.source_extraction import forced_fits


logger = logging.getLogger(__name__)


def runner(func, iterable, arguments, local=False):
    """
    A wrapper for mapping your iterable over a function. If local is False,
    the mapping is performed using celery, else it will be performed locally.

    :param func: The function to be called, should have task decorator
    :param iterable: a list of objects to iterate over
    :param arguments: list of arguments to give to the function
    :param local: False if you want to use celery, True if local run
    :return: the result of the func mapped
    """
    if local:
        return [func(i, *arguments) for i in iterable]
    else:
        if iterable:
            return group(func.s(i, *arguments) for i in iterable)().get()
        else:
            # group()() returns None if group is called with no arguments,
            # leading to an AttributeError with get().
            return []


def run(job_name, local=False):
    setup_event_listening(celery_app)
    pipe_config = initialize_pipeline_config(
        os.path.join(os.getcwd(), "pipeline.cfg"),
        job_name)

    debug = pipe_config['logging']['debug']
    #Setup logfile before we do anything else
    log_dir = pipe_config['logging']['log_dir']
    setup_log_file(log_dir, debug)

    job_dir = pipe_config['DEFAULT']['job_directory']
    if not os.access(job_dir, os.X_OK):
        msg = "can't access job folder %s" % job_dir
        logger.error(msg)
        raise IOError(msg)
    logger.info("Job dir: %s", job_dir)

    db_config = get_database_config(pipe_config['database'], apply=True)
    dump_database_backup(db_config, job_dir)

    job_config = load_job_config(pipe_config)
    se_parset = job_config['source_extraction']
    deRuiter_radius = job_config['association']['deruiter_radius']


    all_images = imp.load_source('images_to_process',
                                 os.path.join(job_dir,
                                              'images_to_process.py')
                                 ).images

    logger.info("dataset %s contains %s images" % (job_name, len(all_images)))

    dump_configs_to_logdir(log_dir, job_config, pipe_config)


    logger.info("performing database consistency check")
    if not dbconsistency.check():
        logger.error("Inconsistent database found; aborting")
        return 1

    logger.info("performing persistence step")
    image_cache_params = pipe_config['image_cache']
    imgs = [[img] for img in all_images]
    metadatas = runner(tasks.persistence_node_step,imgs, [image_cache_params],
                       local)
    metadatas = [m[0] for m in metadatas]

    persistence = job_config['persistence']
    dataset_id, image_ids = steps.persistence.master_steps(metadatas,
                                                           se_parset['extraction_radius_pix'],
                                                           persistence)

    db_images = [Image(id=image_id) for image_id in image_ids]

    logger.info("performing quality check")
    urls = [img.url for img in db_images]
    arguments = [job_config]
    rejecteds = runner(tasks.quality_reject_check, urls, arguments, local)

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
        logging.info("processing %s images in timestep %s (%s/%s)" % (len(images),
                                                                      timestep, n+1,
                                                                      timestep_num))

        logger.info("performing source extraction")
        urls = [img.url for img in images]
        arguments = [se_parset]
        extract_sources = runner(tasks.extract_sources, urls, arguments, local)

        logger.info("storing extracted to database")
        for image, sources in zip(images, extract_sources):
            dbgen.insert_extracted_sources(image.id, sources, 'blind')

        logger.info("performing database operations")
        for image in images:
            logger.info("performing DB operations for image %s" % image.id)
            logger.info("performing null detections")
            null_detections = dbmon.get_nulldetections(image.id, deRuiter_radius)

            logger.info("performing forced fits")
            ff_nd = forced_fits(image.url, null_detections, se_parset)
            dbgen.insert_extracted_sources(image.id, ff_nd, 'ff_nd')

            logger.info("performing source association")
            dbass.associate_extracted_sources(image.id,
                                              deRuiter_r=deRuiter_radius)
            dbmon.add_nulldetections(image.id)
            transients = steps.transient_search.search_transients(image.id,
                                                                  job_config['transient_search'])
            dbmon.adjust_transients_in_monitoringlist(image.id, transients)

        dbgen.update_dataset_process_end_ts(dataset_id)