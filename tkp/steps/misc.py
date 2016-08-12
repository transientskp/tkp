"""
Various subroutines used in the main pipeline flow.

We keep them separately to make the pipeline logic easier to read at a glance.
"""

import datetime
import ConfigParser
import logging
import os
from pprint import pprint

from collections import defaultdict, namedtuple

from tkp.config import parse_to_dict
from tkp.db.dump import dump_db

import colorlog

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


def setup_logging(log_dir, debug, use_colorlog,
                  basename='trap'):
    """
    Sets up logging to stdout, + info/debug level logfiles in log_dir.

    Args:
        log_dir (string): log directory
        debug (bool): do we want debug level logging on stdout?
        basename (string): basename of the log file
    """
    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)
    info_log_file = os.path.join(log_dir, basename+'.log')
    debug_log_file = os.path.join(log_dir, basename+'.debug.log')

    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s %(name)s: %(message)s',
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    debug_formatter = logging.Formatter(
        '%(asctime)s %(levelname)s %(name)s %(funcName)s() process %(processName)s '
        '(%(process)d) thread %(threadName)s (%(thread)d) : %(message)s',
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    info_hdlr = logging.FileHandler(info_log_file)
    info_hdlr.setLevel(logging.INFO)
    info_hdlr.setFormatter(formatter)

    debug_hdlr = logging.FileHandler(debug_log_file)
    debug_hdlr.setLevel(logging.DEBUG)
    debug_hdlr.setFormatter(debug_formatter)

    stdout_handler = logging.StreamHandler()

    if debug:
        stdout_handler.setLevel(logging.DEBUG)
        formatter = debug_formatter
    else:
        stdout_handler.setLevel(logging.INFO)
        formatter = formatter

    if use_colorlog:
        formatter = colorlog.ColoredFormatter(
            "%(log_color)s" + formatter._fmt,
            datefmt="%H:%M:%S",
            reset=True,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red',
            }
        )
    stdout_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    # We set level to debug, and handle output via handler-levels
    root_logger.setLevel(logging.DEBUG)
    # Trash any preset handlers and start fresh
    root_logger.handlers = []
    root_logger.addHandler(stdout_handler)
    root_logger.addHandler(info_hdlr)
    root_logger.addHandler(debug_hdlr)

    logger.info("logging to %s" % log_dir)
    # Suppress noisy streams
    logging.getLogger('tkp.sourcefinder.image.sigmaclip').setLevel(logging.INFO)


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

ImageMetadataForSort = namedtuple('ImageMetadataForSort', [
    'url',
    'timestamp',
    'frequency',
])


def group_per_timestep(metadatas):
    """
    groups a list of TRAP images per time step.

    Per time step the images are order per frequency. We could add other
    ordering logic (per stoke) later on.

    Args:
        metadatas (list): list of ImageMetadataForSort

    Returns:
        list: List of tuples. The list is sorted by timestamp.
            Each tuple has the timestamp as a first element,
            and a list of ImageMetadataForSort sorted by frequency as the
            second element.

    """
    grouped_dict = defaultdict(list)
    for metadata in metadatas:
        grouped_dict[metadata.timestamp].append(metadata)

    grouped_tuple = grouped_dict.items()

    # sort for timestamp
    grouped_tuple.sort()

    # and then sort the nested items per freq and stokes
    [l[1].sort(key=lambda x: x.frequency) for l in grouped_tuple]

    # only return the urls
    return [(stamp, [m.url for m in metas]) for stamp, metas in grouped_tuple]

