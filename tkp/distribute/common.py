import ConfigParser
import logging
import os

logger = logging.getLogger(__name__)


def load_job_config(pipe_config):
    """Adds a predefined list of config files to the pipeline configuration

    Since each file has its own section, these can all be read into a
    combined ConfigParser object representing the 'job settings', i.e.
    the parameters relating to this particular data reduction run.
    """
    job_directory = pipe_config.get('DEFAULT', 'job_directory')
    job_config = ConfigParser.SafeConfigParser()
    job_config.read(os.path.join(job_directory, 'job_params.cfg'))
    return job_config


def dump_job_config_to_logdir(log_dir, job_config):
    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)
    with open(os.path.join(log_dir, 'job_and_pipeline_params.cfg'), 'w') as f:
        job_config.write(f)


def setup_file_logging(log_file, debug=False):
    """
    sets up a catch all logging handler which writes to `log_file`.

    :param log_file: log file to write
    :param debug: do we want debug level logging?
    """
    if not os.path.isdir(os.path.dirname(log_file)):
        os.makedirs(os.path.dirname(log_file))
    global_logger = logging.getLogger()
    hdlr = logging.FileHandler(log_file)
    global_logger.addHandler(hdlr)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')
    hdlr.setFormatter(formatter)
    logger.info("logging to %s" % log_file)
    if debug:
        global_logger.setLevel(logging.DEBUG)
    else:
        global_logger.setLevel(logging.INFO)
