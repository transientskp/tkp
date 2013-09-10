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
    task_parsets_to_read = ['db_dump',
                            'persistence',
                            'quality_check',
                            'source_association',
                            'source_extraction',
                            'null_detections',
                            'transient_search']
    parset_directory = pipe_config.get('layout', 'parset_directory')
    parset_files_to_read = [os.path.join(parset_directory, taskname + '.parset')
                                for taskname in task_parsets_to_read]
    job_config = ConfigParser.SafeConfigParser()
    job_config.read(parset_files_to_read)
    return job_config


def dump_job_config_to_logdir(log_dir, job_config):
    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)
    with open(os.path.join(log_dir, 'jobpars.parset'), 'w') as f:
        job_config.write(f)


def setup_file_logging(log_dir, debug=False):
    """
    sets up a catch all logging handler which writes to a file in `log_dir`.

    :param log_dir: where to store the log file
    :param debug: do we want debug level logging?
    """
    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)
    global_logger = logging.getLogger()
    hdlr = logging.FileHandler(os.path.join(log_dir, 'output.log'))
    global_logger.addHandler(hdlr)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')
    hdlr.setFormatter(formatter)
    logger.info("logging to %s" % log_dir)
    if debug:
        global_logger.setLevel(logging.DEBUG)
    else:
        global_logger.setLevel(logging.INFO)