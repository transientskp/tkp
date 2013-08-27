import ConfigParser
import os
import datetime
import tkp.db
import tkp.utility.parset as parset

def initialize_pipeline_config(pipe_cfg_file, job_name):
    """Replaces the sort of background bookkeeping that cuisine would do"""
    start_time = datetime.datetime.utcnow().replace(microsecond=0).isoformat()
    config = ConfigParser.SafeConfigParser({
        "job_name": job_name,
        "start_time": start_time,
        "cwd": os.getcwd(),
    })
    #NB we force sensible errors by attempting to open the pipeline.cfg file:
    with open(pipe_cfg_file) as f:
        config.readfp(f)
    return config


def database_config(pipe_config, apply=False):
    """
    sets up a database configuration using the settings defined in a pipeline.cfg

    :param pipe_config: a ConfigParser object
    :param apply: apply settings (configure db connection) or not
    :return:
    """
    kwargs = {}
    db_parset = parset.load_section(pipe_config, 'database')
    interests = ('engine', 'database', 'user', 'password', 'host', 'port')
    for key, value in db_parset.iteritems():
        if key in interests:
            kwargs[key] = value
    if apply:
        tkp.db.configure(**kwargs)
        tkp.db.execute('select 1')
    return kwargs
