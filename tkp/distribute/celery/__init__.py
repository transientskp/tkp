import ConfigParser
import os
import datetime
import imp
from celery import group
from tkp.steps.monitoringlist import add_manual_monitoringlist_entries
from tkp import steps
from tkp.db.orm import Image
from tkp.db import general as dbgen
from tkp.db import monitoringlist as dbmon
from tkp.db import associations as dbass
from tkp.distribute.celery import tasks


def string_to_list(my_string):
    """
    Convert a list-like string (as in pipeline.cfg) to a list of values.
    """
    return [x.strip() for x in my_string.strip('[] ').split(',') if x.strip()]


def run():
    here = os.getcwd()
    job_name = 'devel'
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
    images = imp.load_source('images_to_process', os.path.join(job_dir,
                             'images_to_process.py')).images

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
    s1 = tasks.persistence_node_step.s(images[0], p_parset)
    res = s1.delay()
    res.get()
    #metadatas = group(tasks.persistence_node_step.s(img, p_parset) for img in images)().get()

    #metadatas = tasks.persistence_node_steps(images, p_parset)
    dataset_id, image_ids = steps.persistence.master_steps(metadatas,
                                                           se_parset['radius'],
                                                           p_parset)

    # manual monitoringlist entries
    if not add_manual_monitoringlist_entries(dataset_id, []):
        return 1

    # quality_check
    good_image_ids = []
    for image_id in image_ids:
        image = Image(id=image_id)
        rejected = steps.quality.reject_check(image.url, q_parset)
        if rejected:
            reason, comment = rejected
            steps.quality.reject_image(image_id, reason, comment)
        else:
            good_image_ids.append(image_id)

    # Sourcefinding
    good_images = []
    transients = []
    for image_id in good_image_ids:
        image = Image(id=image_id)
        good_images.append(image)
        extracted_sources = steps.source_extraction.extract_sources(
                                                 image.url, se_parset)
        dbgen.insert_extracted_sources(image_id, extracted_sources,
                                       'blind')

        # null_detections
        deRuiter_radius = nd_parset['deRuiter_radius']

        #for image in good_images:
        image_id = image.id
        image_path = image.url

        null_detections = dbmon.get_nulldetections(image_id,
                                                   deRuiter_radius)
        ff_nd = steps.source_extraction.forced_fits(image_path,
                                                    null_detections,
                                                    nd_parset)
        dbgen.insert_extracted_sources(image_id, ff_nd, 'ff_nd')

        # Source_association
        dbass.associate_extracted_sources(image_id,
                                          deRuiter_r=deRuiter_radius)
        dbmon.add_nulldetections(image_id)

        # Transient_search
        transients = steps.transient_search.search_transients(image_id,
                                                              tr_parset)
        dbmon.adjust_transients_in_monitoringlist(image_id, transients)

    # Classification
    for transient in transients:
        steps.feature_extraction.extract_features(transient)
#            ingred.classification.classify(transient, cl_parset)

    now = datetime.datetime.utcnow()
    dbgen.update_dataset_process_ts(dataset_id, now)
