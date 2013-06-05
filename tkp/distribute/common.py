import ConfigParser
def load_job_config(pipe_config):
    task_parsets_to_read = ['persistence',
                            'quality_check',
                            'source_extraction',
                            'null_detections',
                            'transient_search']
    parset_files_to_read = [pipe_config.get(taskname, 'parset')
                                for taskname in task_parsets_to_read]
    job_config = ConfigParser.SafeConfigParser()
    job_config.read(parset_files_to_read)
    return job_config
