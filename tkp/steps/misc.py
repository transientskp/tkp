"""
Various subroutines used in the main pipeline flow.

We keep them separately to make the pipeline logic easier to read at a glance.
"""

import datetime
import ConfigParser
import logging
import os
from pprint import pprint

from collections import defaultdict

from tkp.config import parse_to_dict
from tkp.db.dump import dump_db


logger = logging.getLogger(__name__)


def load_job_config(pipe_config):
    """
    Locates the job_params.cfg in 'job_directory' and loads via ConfigParser.
    """
    job_directory = pipe_config['DEFAULT']['job_directory']
    job_config = ConfigParser.SafeConfigParser()
    job_config.read(os.path.join(job_directory, 'job_params.cfg'))
    return parse_to_dict(job_config)


def dump_configs_to_logdir(log_dir, job_config, pipe_config):
    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)
    with open(os.path.join(log_dir, 'job_params.cfg'), 'w') as f:
        pprint(job_config, stream=f)
    with open(os.path.join(log_dir, 'pipeline.cfg'), 'w') as f:
        pprint(pipe_config, stream=f)


def check_job_configs_match(job_config_1, job_config_2):
    """
    Check if job configs match, except dataset_id which we expect to change.
    """
    jc_from_file = job_config_1.copy()
    jc_from_db = job_config_2.copy()
    del jc_from_file['persistence']['dataset_id']
    del jc_from_db['persistence']['dataset_id']
    return jc_from_file==jc_from_db


def setup_log_file(log_dir, debug=False, basename='trap.log'):
    """
    sets up a catch all logging handler which writes to `log_file`.

    :param log_file: log file to write
    :param debug: do we want debug level logging?
    :param basename: basename of the log file
    """
    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)
    log_file = os.path.join(log_dir, basename)
    global_logger = logging.getLogger()
    hdlr = logging.FileHandler(log_file)
    global_logger.addHandler(hdlr)
    formatter = logging.Formatter(
        '%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s',
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    hdlr.setFormatter(formatter)
    logger.info("logging to %s" % log_file)
    if debug:
        global_logger.setLevel(logging.DEBUG)
    else:
        global_logger.setLevel(logging.INFO)


def dump_database_backup(db_config, job_dir):
    if 'dump_backup_copy' in db_config:
        if db_config['dump_backup_copy']:
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

def group_per_timestep(images):
    """
    groups a list of TRAP images per time step.

    Per time step the images are order per frequency and then per stokes. The
    eventual order is:

    (t1, f1, s1), (t1, f1, s2), (t1, f2, s1), (t1, f2, s2), (t2, f1, s1), ...)
    where:

        * t is time sorted by old to new
        * f is frequency sorted from low to high
        * s is stokes, sorted by ID as defined in the database schema

    Args:
        images (list): Images to group.

    Returns:
        list: List of tuples. The list is sorted by timestamp.
            Each tuple has the timestamp as a first element,
            and a list of images sorted by frequency and then stokes
            as the second element.

    """
    timestamp_to_images_map = defaultdict(list)
    for image in images:
        timestamp_to_images_map[image.taustart_ts].append(image)

    #List of (timestamp, [images_at_timestamp]) tuples:
    grouped_images = timestamp_to_images_map.items()

    # sort the tuples by first element (timestamps)
    grouped_images.sort()

    # and then sort the nested items per freq and stokes
    [l[1].sort(key=lambda x: (x.freq_eff, x.stokes)) for l in grouped_images]
    return grouped_images
