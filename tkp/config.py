import ConfigParser
import os
import datetime
import tkp.db
import tkp.utility.parset as parset
import getpass

import logging

logger = logging.getLogger(__name__)

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


def database_config(pipe_config=None, apply=False):
    """
    sets up a database configuration using the settings defined in a
    pipeline.cfg (if supplied) and optionally overriden by the environment.
    The following environment variables are recognized::

      * TKP_DBENGINE
      * TKP_DBNAME
      * TKP_DBUSER
      * TKP_DBPASS
      * TKP_DBHOST
      * TKP_DBPORT

    :param pipe_config: a ConfigParser object
    :param apply: apply settings (configure db connection) or not
    :return:
    """
    # Default values
    kwargs = {
        'engine': "postgresql", 'database': None, 'user': getpass.getuser(),
        'password': None, 'host': "localhost", 'port': "5432", 'passphrase': None
    }

    # Try loading a config file, if any
    if pipe_config and pipe_config.has_section('database'):
        db_parset = parset.load_section(pipe_config, 'database')
        for key, value in db_parset.iteritems():
            if key in kwargs:
                kwargs[key] = value

    # The environment takes precedence over the config file
    for env_var, key in [
        ("TKP_DBNAME", 'database'),
        ("TKP_DBUSER", 'user'),
        ("TKP_DBENGINE", 'engine'),
        ("TKP_DBPASSWORD", "password"),
        ("TKP_DBHOST", "host"),
        ("TKP_DBPORT", "port")
    ]:
        if env_var in os.environ:
            kwargs[key] = os.environ.get(env_var)

    # If only the username is defined, use that as a
    # default for the database name and password.
    if kwargs['user'] and not kwargs['database']:
        kwargs['database'] = kwargs['user']
    if kwargs['user'] and not kwargs['password']:
        kwargs['password'] = kwargs['user']

    # Optionally, initiate a db connection with the settings determined
    if apply:
        tkp.db.Database(**kwargs)
        tkp.db.execute('select 1')

    return kwargs
