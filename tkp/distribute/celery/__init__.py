import os
import imp
import threading
import datetime
import time
import logging

from celery import group
from celery.signals import after_setup_logger, after_setup_task_logger

from tkp.config import initialize_pipeline_config, database_config
from tkp.distribute.celery.tasklog import setup_task_log_emitter, monitor_events
from tkp.steps.monitoringlist import add_manual_monitoringlist_entries
from tkp import steps
from tkp.db.orm import Image
from tkp.db import consistency as dbconsistency
from tkp.db import general as dbgen
from tkp.db import monitoringlist as dbmon
from tkp.db import associations as dbass
from tkp.db.dump import dump_db
from tkp.distribute.celery import tasks
from tkp.distribute.common import load_job_config, dump_job_config_to_logdir, setup_file_logging
from tkp.conf import parse_to_dict


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


def string_to_list(my_string):
    """
    Convert a list-like string (as in pipeline.cfg) to a list of values.
    """
    return [x.strip() for x in my_string.strip('[] ').split(',') if x.strip()]


def setup_log_broadcasting():
    # capture celery log events in the background
    after_setup_logger.connect(setup_task_log_emitter)
    after_setup_task_logger.connect(setup_task_log_emitter)
    monitoring_thread = threading.Thread(target=monitor_events,
                                         args=[tasks.trap])
    monitoring_thread.daemon = True
    monitoring_thread.start()

    # we need to wait for the thread to release the import lock
    time.sleep(2)


def group_per_timestep(images):
    """
    groups a list of TRAP images per timestep
    """
    img_dict = {}
    for image in images:
        t = image.taustart_ts
        if t in img_dict:
            img_dict[t].append(image)
        else:
            img_dict[t] = [image]

    grouped_images = img_dict.items()
    grouped_images.sort()
    return grouped_images



def run(job_name, local=False):

    setup_log_broadcasting()
    pipe_config = initialize_pipeline_config(
                             os.path.join(os.getcwd(), "pipeline.cfg"),
                             job_name)

    db_config = database_config(pipe_config, apply=True)
    job_dir = pipe_config.get('DEFAULT', 'job_directory')
    debug = pipe_config.getboolean('logging', 'debug')
    log_dir = os.path.dirname(pipe_config.get('logging', 'log_file'))
    setup_file_logging(log_dir, debug)

    if not os.access(job_dir, os.X_OK):
        msg = "can't access job folder %s" % job_dir
        logger.error(msg)
        raise IOError(msg)

    logger.info("Job dir: %s", job_dir)

    job_config = load_job_config(pipe_config)

    # Dump the database to the job directory if:
    # a) we have a job config section called "db_dump", and
    # b) that section contains a "db_dump" option which is True.
    if job_config.has_section("db_dump"):
        dump_cfg = parse_to_dict(job_config, 'db_dump')
    else:
        dump_cfg = {}
    if 'db_dump' in dump_cfg and dump_cfg['db_dump']:
        output_name = os.path.join(
            job_dir, "%s_%s_%s.dump" % (
                db_config['host'], db_config['database'],
                datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            )
        )
        dump_db(
            db_config['engine'], db_config['host'], str(db_config['port']),
            db_config['database'], db_config['user'], db_config['password'],
            output_name
        )

    all_images = imp.load_source('images_to_process', os.path.join(job_dir,
                             'images_to_process.py')).images

    logger.info("dataset %s contains %s images" % (job_name, len(all_images)))

    dump_job_config_to_logdir(log_dir, job_config)

    p_parset = parse_to_dict(job_config, 'persistence')
    se_parset = parse_to_dict(job_config, 'source_extraction')
    tr_parset = parse_to_dict(job_config, 'transient_search')
    deRuiter_radius = parse_to_dict(job_config, 'association')['deruiter_radius']

    logger.info("performing database consistency check")
    if not dbconsistency.check():
        logger.error("Inconsistent database found; aborting")
        return 1

    logger.info("performing persistence step")
    imgs = [[img] for img in all_images]
    arguments = [p_parset]
    metadatas = runner(tasks.persistence_node_step, imgs, arguments, local)
    metadatas = [m[0] for m in metadatas]

    dataset_id, image_ids = steps.persistence.master_steps(metadatas,
                                           se_parset['extraction_radius_pix'],
                                           p_parset)

    # As of the current release, we do not support a "monitoring list"
    #if not add_manual_monitoringlist_entries(dataset_id, monitor_coords):
    #    return 1

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

        logger.info("performing null detections")
        null_detectionss = [dbmon.get_nulldetections(image.id, deRuiter_radius)
                            for image in images]

        logger.info("performing forced fits")
        iters = zip([i.url for i in images], null_detectionss)
        arguments = [se_parset]
        ff_nds = runner(tasks.forced_fits, iters, arguments, local)

        for image, ff_nd in zip(images, ff_nds):
            dbgen.insert_extracted_sources(image.id, ff_nd, 'ff_nd')

        logger.info("performing database operations")
        for image in images:
            logger.info("performing DB operations for image %s" % image.id)
            dbass.associate_extracted_sources(image.id,
                                              deRuiter_r=deRuiter_radius)
            dbmon.add_nulldetections(image.id)
            transients = steps.transient_search.search_transients(image.id,
                                                                  tr_parset)
            dbmon.adjust_transients_in_monitoringlist(image.id, transients)

        dbgen.update_dataset_process_end_ts(dataset_id)
