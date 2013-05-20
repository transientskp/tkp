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


logger = logging.getLogger(__name__)


def string_to_list(my_string):
    """
    Convert a list-like string (as in pipeline.cfg) to a list of values.
    """
    return [x.strip() for x in my_string.strip('[] ').split(',') if x.strip()]


def run(job_name, local=False):
    here = os.getcwd()
    pipeline_file = os.path.join(here, "pipeline.cfg")
    start_time = datetime.datetime.utcnow().replace(microsecond=0).isoformat()
    config = ConfigParser.SafeConfigParser({
        "job_name": job_name,
        "start_time": start_time,
        "cwd": here,
    })
    config.read(pipeline_file)
    task_files = string_to_list(config.get('DEFAULT', "task_files"))
    config.read(task_files)

    job_dir = config.get('layout', 'job_directory')
    logger.info("Job dir: %s", job_dir)
    images = imp.load_source('images_to_process', os.path.join(job_dir,
                             'images_to_process.py')).images

    logging.info("dataset %s containts %s images" % (job_name, len(images)))

    p_parset_file = config.get("persistence", "parset")
    q_parset_file = config.get("quality_check", "parset")
    se_parset_file = config.get("source_extraction", "parset")
    nd_parset_file = config.get("null_detections", "parset")
    tr_parset_file = config.get("transient_search", "parset")

    p_parset = steps.persistence.parse_parset(p_parset_file)
    q_parset = steps.quality.parse_parset(q_parset_file)
    se_parset = steps.source_extraction.parse_parset(se_parset_file)
    nd_parset = steps.null_detections.parse_parset(nd_parset_file)
    tr_parset = steps.transient_search.parse_parset(tr_parset_file)

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
    rejecteds = group(tasks.quality_reject_check.s(img.url, q_parset)
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
    deRuiter_radius = nd_parset['deRuiter_radius']
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
