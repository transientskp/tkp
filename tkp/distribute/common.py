import ConfigParser
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
