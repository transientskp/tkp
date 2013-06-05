import ConfigParser
import os

def load_job_config(pipe_config):
    """Pulls the parset filenames as defined in the tasks.cfg config file.

    Since each parset has its own section, these can all be read into a 
    combined ConfigParser object representing the 'job settings', i.e.
    the parameters relating to this particular data reduction run.
    """
    task_parsets_to_read = ['persistence',
                            'quality_check',
                            'source_association',
                            'source_extraction',
                            'null_detections',
                            'transient_search']
    parset_files_to_read = [pipe_config.get(taskname, 'parset')
                                for taskname in task_parsets_to_read]
    job_config = ConfigParser.SafeConfigParser()
    job_config.read(parset_files_to_read)
    return job_config

def dump_job_config_to_logdir(pipe_config, job_config):
    log_dir = os.path.dirname(pipe_config.get('logging', 'log_file'))
    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)
    with open(os.path.join(log_dir, 'jobpars.parset'), 'w') as f:
        job_config.write(f)
