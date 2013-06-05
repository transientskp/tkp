import ConfigParser
import os
import datetime
import imp
import logging
from celery import group
from tkp.steps.monitoringlist import add_manual_monitoringlist_entries
from tkp import steps
from tkp.db.orm import Image
from tkp.db import general as dbgen
from tkp.db import monitoringlist as dbmon
from tkp.db import associations as dbass
from tkp.distribute.celery import tasks
from tkp.distribute.common import load_job_config, dump_job_config_to_logdir
import tkp.utility.parset as parset
import sys


logger = logging.getLogger(__name__)


def string_to_list(my_string):
    """
    Convert a list-like string (as in pipeline.cfg) to a list of values.
    """
    return [x.strip() for x in my_string.strip('[] ').split(',') if x.strip()]

def initialize_pipeline_config(pipe_cfg_file, job_name):
    start_time = datetime.datetime.utcnow().replace(microsecond=0).isoformat()
    if not os.path.isfile(pipe_cfg_file):
            logger.warn("Could not find pipeline config at: %s", pipe_cfg_file)
            sys.exit(1)
    config = ConfigParser.SafeConfigParser({
        "job_name": job_name,
        "start_time": start_time,
        "cwd": os.getcwd(),
    })
    config.read(pipe_cfg_file)
    task_files = string_to_list(config.get('DEFAULT', "task_files"))
    for f in task_files:
        if not os.path.isfile(f):
            logger.warn("Could not find task file: %s", f)
    config.read(task_files)
    return config

def run(job_name, local=False):
    pipe_config = initialize_pipeline_config(
                             os.path.join(os.getcwd(), "pipeline.cfg"),
                             job_name)

    job_dir = pipe_config.get('layout', 'job_directory')

    logger.info("Job dir: %s", job_dir)
    images = imp.load_source('images_to_process', os.path.join(job_dir,
                             'images_to_process.py')).images

    logger.info("dataset %s containts %s images" % (job_name, len(images)))

    job_config = load_job_config(pipe_config)
    dump_job_config_to_logdir(pipe_config, job_config)

    p_parset = parset.load_section(job_config, 'persistence')
    q_lofar_parset = parset.load_section(job_config, 'quality_lofar')
    se_parset = parset.load_section(job_config, 'source_extraction')
    nd_parset = parset.load_section(job_config, 'null_detections')
    tr_parset = parset.load_section(job_config, 'transient_search')


    # persistence
    metadatas = group(tasks.persistence_node_step.s([img], p_parset)
                      for img in images)().get()
    metadatas = [m[0] for m in metadatas]

    dataset_id, image_ids = steps.persistence.master_steps(metadatas,
                                                           se_parset['radius'],
                                                           p_parset)

    # manual monitoringlist entries
    if not add_manual_monitoringlist_entries(dataset_id, []):
        return 1

    images = [Image(id=image_id) for image_id in image_ids]

    # quality_check
    rejecteds = group(tasks.quality_reject_check.s(img.url, q_lofar_parset)
                      for img in images)().get()
    good_images = []
    for image, rejected in zip(images, rejecteds):
        if rejected:
            reason, comment = rejected
            steps.quality.reject_image(image.id, reason, comment)
        else:
            good_images.append(image)

    if not good_images:
        logger.warn("No good images under these quality checking criteria")
        return

    # Sourcefinding
    extract_sources = group(tasks.extract_sources.s(img.url, se_parset)
                            for img in good_images)().get()

    for image, sources in zip(good_images, extract_sources):
        dbgen.insert_extracted_sources(image.id, sources, 'blind')


    # null_detections
    deRuiter_radius = nd_parset['deruiter_radius']
    null_detectionss = [dbmon.get_nulldetections(image.id, deRuiter_radius)
                        for image in good_images]
    ff_nds = group(tasks.forced_fits.s(img.url, null_detections, nd_parset)
                   for img, null_detections in zip(good_images,
                                                   null_detectionss))().get()

    for image, ff_nd in zip(good_images, ff_nds):
        dbgen.insert_extracted_sources(image.id, ff_nd, 'ff_nd')

    for image in good_images:
        logger.info("performing DB operations for image %s" % image.id)
        dbass.associate_extracted_sources(image.id,
                                          deRuiter_r=deRuiter_radius)
        dbmon.add_nulldetections(image.id)
        transients = steps.transient_search.search_transients(image.id,
                                                              tr_parset)
        dbmon.adjust_transients_in_monitoringlist(image.id, transients)

    for transient in transients:
        steps.feature_extraction.extract_features(transient)
#            ingred.classification.classify(transient, cl_parset)

    now = datetime.datetime.utcnow()
    dbgen.update_dataset_process_ts(dataset_id, now)
