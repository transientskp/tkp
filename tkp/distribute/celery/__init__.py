import os
import imp
import logging

from celery import group

from tkp.config import initialize_pipeline_config, database_config
from tkp.steps.monitoringlist import add_manual_monitoringlist_entries
from tkp import steps
from tkp.db.orm import Image
from tkp.db import general as dbgen
from tkp.db import monitoringlist as dbmon
from tkp.db import associations as dbass
from tkp.distribute.celery import tasks
from tkp.distribute.common import load_job_config, dump_job_config_to_logdir
import tkp.utility.parset as parset


logger = logging.getLogger(__name__)


def runner(func, iterable, arguments, local=False):
    """

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
    pipe_config = initialize_pipeline_config(
                             os.path.join(os.getcwd(), "pipeline.cfg"),
                             job_name)


    database_config(pipe_config, apply=True)

    job_dir = pipe_config.get('layout', 'job_directory')

    if not os.access(job_dir, os.X_OK):
        msg = "can't access job folder %s" % job_dir
        logger.error(msg)
        raise IOError(msg)

    logger.info("Job dir: %s", job_dir)
    all_images = imp.load_source('images_to_process', os.path.join(job_dir,
                             'images_to_process.py')).images

    logger.info("dataset %s contains %s images" % (job_name, len(all_images)))

    job_config = load_job_config(pipe_config)
    dump_job_config_to_logdir(pipe_config, job_config)

    p_parset = parset.load_section(job_config, 'persistence')
    se_parset = parset.load_section(job_config, 'source_extraction')
    nd_parset = parset.load_section(job_config, 'null_detections')
    tr_parset = parset.load_section(job_config, 'transient_search')


    # persistence
    imgs = [[img] for img in all_images]
    arguments = [p_parset]
    metadatas = runner(tasks.persistence_node_step, imgs, arguments, local)
    metadatas = [m[0] for m in metadatas]

    dataset_id, image_ids = steps.persistence.master_steps(metadatas,
                                                           se_parset['radius'],
                                                           p_parset)

    # manual monitoringlist entries
    if not add_manual_monitoringlist_entries(dataset_id, []):
        return 1

    db_images = [Image(id=image_id) for image_id in image_ids]

    # quality_check
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

        # Sourcefinding
        urls = [img.url for img in images]
        arguments = [se_parset]
        extract_sources = runner(tasks.extract_sources, urls, arguments, local)

        for image, sources in zip(images, extract_sources):
            dbgen.insert_extracted_sources(image.id, sources, 'blind')

        # null_detections
        deRuiter_radius = nd_parset['deruiter_radius']
        null_detectionss = [dbmon.get_nulldetections(image.id, deRuiter_radius)
                            for image in images]

        iters = zip([i.url for i in images], null_detectionss)
        arguments = [nd_parset]
        ff_nds = runner(tasks.forced_fits, iters, arguments, local)

        for image, ff_nd in zip(images, ff_nds):
            dbgen.insert_extracted_sources(image.id, ff_nd, 'ff_nd')

        for image in images:
            logger.info("performing DB operations for image %s" % image.id)
            dbass.associate_extracted_sources(image.id,
                                              deRuiter_r=deRuiter_radius)
            dbmon.add_nulldetections(image.id)
            transients = steps.transient_search.search_transients(image.id,
                                                                  tr_parset)
            dbmon.adjust_transients_in_monitoringlist(image.id, transients)

        dbgen.update_dataset_process_end_ts(dataset_id)
