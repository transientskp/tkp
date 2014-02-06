"""
Various subroutines used in the main pipeline flow.

We keep them separately to make the pipeline logic easier to read at a glance.
"""

import datetime
import ConfigParser
import logging
import os
from pprint import pprint
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