"""
The main pipeline logic, from where all other components are called.
"""
import imp
import logging
import atexit
import os
from tkp import steps
from tkp.config import initialize_pipeline_config, get_database_config
import tkp.db
from tkp.db.image_store import store_fits
from astropy.io.fits.hdu import HDUList
from itertools import chain
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
from tkp.stream import stream_generator
from tkp.quality.rms import reject_historical_rms


logger = logging.getLogger(__name__)


def get_pipe_config(job_name):
    return initialize_pipeline_config(os.path.join(os.getcwd(), "pipeline.cfg"),
                                      job_name)


def setup(pipe_config, supplied_mon_coords=None):
    """
    Initialises the pipeline run.
    """
    if not supplied_mon_coords:
        supplied_mon_coords = []

    # Setup logfile before we do anything else
    log_dir = pipe_config.logging.log_dir
    setup_logging(log_dir, debug=pipe_config.logging.debug,
                  use_colorlog=pipe_config.logging.colorlog)

    job_dir = pipe_config.DEFAULT.job_directory
    if not os.access(job_dir, os.X_OK):
        msg = "can't access job folder %s" % job_dir
        logger.error(msg)
        raise IOError(msg)
    logger.info("Job dir: %s", job_dir)

    db_config = get_database_config(pipe_config.database, apply=True)
    dump_database_backup(db_config, job_dir)

    job_config = load_job_config(pipe_config)
    dump_configs_to_logdir(log_dir, job_config, pipe_config)

    sync_rejectreasons(tkp.db.Database().Session())

    job_config, dataset_id = initialise_dataset(job_config, supplied_mon_coords)

    return job_dir, job_config, dataset_id


def get_runner(pipe_config):
    """
    get parallelise props. Defaults to multiproc with autodetect num cores. Wil
    initialise the distributor.

    One should not mix threads and multiprocessing, but for example AstroPy uses
    threads internally. Best practice then is to first do multiprocessing,
    and then threading per process. This is the reason why this function
    should be called as one of the first functions the in the TraP pipeline
    lifespan.
    """
    para = pipe_config.parallelise
    logging.info("using '{}' method for parallellisation".format(para.method))
    distributor = os.environ.get('TKP_PARALLELISE', para.method)
    return Runner(distributor=distributor, cores=para.cores)


def load_images(job_name, job_dir):
    """
    Load all the images for a specific TraP job.

    returns:
        list: a list of paths
    """
    path = os.path.join(job_dir, 'images_to_process.py')
    images = imp.load_source('images_to_process', path).images
    logger.info("dataset %s contains %s images" % (job_name,
                                                   len(images)))
    return images


def consistency_check():
    logger.info("performing database consistency check")
    if not dbconsistency.check():
        msg = "Inconsistent database found; aborting"
        logger.error(msg)
        raise RuntimeError(msg)


def initialise_dataset(job_config, supplied_mon_coords):
    """
    sets up a dataset in the database.

    if the dataset already exists it will return the job_config from the
    previous dataset run.

    args:
        job_config: a job configuration object
        supplied_mon_coords (list): a list of monitoring positions

    returns:
        tuple: job_config and dataset ID
    """
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


def extract_metadata(job_config, accessors, runner):
    """

    args:
        job_config: a TKP config object
        accessors (list): list of tkp.Accessor objects
        runner (tkp.distribute.Runner): the runner to use

    returns:
        list: a list of metadata dicts
    """
    logger.debug("Extracting metadata from images")
    imgs = [[a] for a in accessors]
    metadatas = runner.map("extract_metadatas",
                           imgs,
                           [job_config.persistence.rms_est_sigma,
                            job_config.persistence.rms_est_fraction])
    metadatas = [m[0] for m in metadatas if m]
    return metadatas


def store_image_metadata(metadatas, job_config, dataset_id):
    logger.debug("Storing image metadata in SQL database")
    r = job_config.source_extraction.extraction_radius_pix
    image_ids = store_images_in_db(metadatas, r, dataset_id,
                                   job_config.persistence.bandwidth_max)
    db_images = [Image(id=image_id) for image_id in image_ids]
    return db_images


def extract_fits_from_files(runner, paths):
    # we assume pahtss is uniform
    if type(paths[0]) == str:
        fitss = runner.map("open_as_fits", [[p] for p in paths])
        return zip(*list(chain.from_iterable(fitss)))
    elif type(paths[0]) == HDUList:
        return [f[0].data for f in paths], [str(f[0].header) for f in paths]
    else:
        logging.error('unknown type')


def quality_check(db_images, accessors, job_config, runner):
    """
    returns:
        list: a list of db_image and accessor tuples
    """
    logger.debug("performing quality check")
    arguments = [job_config]
    rejecteds = runner.map("quality_reject_check", accessors, arguments)

    db = tkp.db.Database()
    history = job_config.persistence.rms_est_history
    rms_max = job_config.persistence.rms_est_max
    rms_min = job_config.persistence.rms_est_min
    est_sigma = job_config.persistence.rms_est_sigma
    good_images = []
    for db_image, rejected, accessor in zip(db_images, rejecteds, accessors):
        if not rejected:
            rejected = reject_historical_rms(db_image.id, db.session,
                                             history, est_sigma, rms_max, rms_min)

        if rejected:
            reason, comment = rejected
            steps.quality.reject_image(db_image.id, reason, comment)
        else:
            good_images.append((db_image, accessor))

    if not good_images:
        msg = "No good images under these quality checking criteria"
        logger.warn(msg)
    return good_images


def source_extraction(accessors, job_config, runner):
    logger.debug("performing source extraction")
    arguments = [job_config.source_extraction]
    extraction_results = runner.map("extract_sources", accessors, arguments)
    total = sum(len(i[0]) for i in extraction_results)
    logger.info('found {} blind sources in {} images'.format(total, len(extraction_results)))
    return extraction_results


def do_forced_fits(runner, all_forced_fits):
    logger.debug('performing forced fitting')
    returned = runner.map("forced_fits", all_forced_fits)
    total = sum(len(i[0]) for i in returned)
    logger.info('performed {} forced fits in {} images'.format(total, len(returned)))
    return returned


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


def assocate_and_get_force_fits(db_image, job_config):
    logger.debug("performing DB operations for image {} ({})".format(db_image.id,
                                                                    db_image.url))

    r = job_config.association.deruiter_radius
    s = job_config.transient_search.new_source_sigma_margin
    dbass.associate_extracted_sources(db_image.id, deRuiter_r=r,
                                      new_source_sigma_margin=s)

    expiration = job_config.source_extraction.expiration
    all_fit_posns, all_fit_ids = steps_ff.get_forced_fit_requests(db_image,
                                                                  expiration)
    return all_fit_posns, all_fit_ids


def varmetric(dataset_id):
    logger.info("calculating variability metrics")
    execute_store_varmetric(dataset_id)


def close_database(dataset_id):
    dbgen.update_dataset_process_end_ts(dataset_id)
    db = tkp.db.Database()
    db.session.commit()
    db.close()


def get_accessors(runner, all_images):
    imgs = [[img] for img in all_images]
    accessors = runner.map("get_accessors", imgs)
    return [a[0] for a in accessors if a]


def get_metadata_for_sorting(runner, image_paths):
    """
    Group images per timestamp. Will open all images in parallel using runner.

    args:
        runner (tkp.distribute.Runner): Runner to use for distribution
        image_paths (list): list of image paths
    returns:
        list: list of tuples, (timestamp, [list_of_images])
    """
    nested_img = [[i] for i in image_paths]
    results = runner.map("get_metadata_for_ordering", nested_img)
    if results and results[0]:
        metadatas = [t[0] for t in results]
        return metadatas
    else:
        logger.warning("no images to process!")
        return []


def store_image_data(db_images, fits_datas, fits_headers):
    logger.info("storing {} images to database".format(len(db_images)))
    store_fits(db_images, fits_datas, fits_headers)


def timestamp_step(runner, images, job_config, dataset_id, copy_images):
    """
    Called from the main loop with all images in a certain timestep

    args:
         runner (tkp.distribute.Runner): Runner to use for distribution
         images (list): list of things tkp.accessors can handle, like image
                        paths or fits objects
         job_config: a tkp job config object
         dataset_id (int): The ``tkp.db.model.Dataset`` id

    returns:
        list: of tuples (rms_qc, band)
    """
    # gather all image info
    accessors = get_accessors(runner, images)
    metadatas = extract_metadata(job_config, accessors, runner)
    db_images = store_image_metadata(metadatas, job_config, dataset_id)
    error = "%s != %s != %s" % (len(accessors), len(metadatas), len(db_images))
    assert len(accessors) == len(metadatas) == len(db_images), error

    # store copy of image data in database
    if copy_images:
        fits_datas, fits_headers = extract_fits_from_files(runner, images)
        store_image_data(db_images, fits_datas, fits_headers)

    # filter out the bad ones
    good_images = quality_check(db_images, accessors, job_config, runner)
    good_accessors = [i[1] for i in good_images]

    # do the source extractions
    extraction_results = source_extraction(good_accessors, job_config, runner)

    store_extractions(good_images, extraction_results, job_config)

    all_forced_fits = []
    # assocate the sources
    for (db_image, accessor) in good_images:
        fit_poss, fit_ids = assocate_and_get_force_fits(db_image, job_config)
        all_forced_fits.append((accessor, db_image.id, fit_poss, fit_ids,
                               job_config.source_extraction))

    # do the forced fitting
    all_forced_fits_results = do_forced_fits(runner, all_forced_fits)

    # store and associate the forced fits
    for (successful_fits, successful_ids, db_image_id) in all_forced_fits_results:
        steps_ff.insert_and_associate_forced_fits(db_image_id,
                                                  successful_fits,
                                                  successful_ids)

    # update the variable metrics for running catalogs
    varmetric(dataset_id)


def run_stream(runner, job_config, dataset_id, copy_images):
    """
    Run the pipeline in stream mode.

    Daemon function, doesn't return.

    args:
         runner (tkp.distribute.Runner): Runner to use for distribution
         job_config: a job configuration object
         dataset_id (int): The dataset ID to use
    """
    hosts = job_config.pipeline.hosts.split(',')
    ports = [int(p) for p in job_config.pipeline.ports.split(',')]
    from datetime import datetime
    for images in stream_generator(hosts=hosts, ports=ports):
        logger.info("processing {} stream images...".format(len(images)))
        trap_start = datetime.now()
        try:
            timestamp_step(runner, images, job_config, dataset_id, copy_images)
        except Exception as e:
            logger.error("timestep raised {} exception: {}".format(type(e), str(e)))
        else:
            trap_end = datetime.now()
            delta = (trap_end - trap_start).microseconds/1000
            logging.info("trap iteration took {} ms".format(delta))


def run_batch(image_paths, job_config, runner, dataset_id, copy_images):
    """
    Run the pipeline in batch mode.

    args:
        job_name (str): job name, used for locating images script
        pipe_config: the pipeline configuration object
        job_config: a job configuration object
        runner (tkp.distribute.Runner): Runner to use for distribution
        dataset_id (int): The dataset ID to use
    """
    sorting_metadata = get_metadata_for_sorting(runner, image_paths)
    grouped_images = group_per_timestep(sorting_metadata)

    for n, (timestep, images) in enumerate(grouped_images):
        msg = "processing %s images in timestep %s (%s/%s)"
        logger.info(msg % (len(images), timestep, n + 1, len(grouped_images)))
        try:
            timestamp_step(runner, images, job_config, dataset_id, copy_images)
        except Exception as e:
            logger.error("timestep raised {} exception: {}".format(type(e), str(e)))


def run(job_name, supplied_mon_coords=None):
    """
    TKP pipeline main loop entry point.

    args:
        job_name (str): name of the jbo to run
        supplied_mon_coords (list): list of coordinates to monitor
    """
    pipe_config = get_pipe_config(job_name)
    runner = get_runner(pipe_config)
    job_dir, job_config, dataset_id = setup(pipe_config, supplied_mon_coords)

    # make sure we close the database connection at program exit
    atexit.register(close_database, dataset_id)

    copy_images = pipe_config.image_cache['copy_images']
    if job_config.pipeline.mode == 'stream':
        run_stream(runner, job_config, dataset_id, copy_images)
    elif job_config.pipeline.mode == 'batch':
        image_paths = load_images(job_name, job_dir)
        run_batch(image_paths, job_config, runner, dataset_id, copy_images)


