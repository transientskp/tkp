from __future__ import absolute_import

from ConfigParser import SafeConfigParser
import datetime
import getpass
import logging
import os

from tkp.config.parse import parse_to_dict, dt_w_microsecond_format
import tkp.db

logger = logging.getLogger(__name__)


def initialize_pipeline_config(pipe_cfg_file, job_name):
    """
    Initializes the default variables and loads the ConfigParser file.

    Sets defaults for start_time, job_name and cwd; these can then be used
    via variable substitution in other config values.

    """
    start_time = datetime.datetime.utcnow().replace(microsecond=0).isoformat()
    config = SafeConfigParser({
        "job_name": job_name,
        "start_time": start_time,
        "cwd": os.getcwd(),
        })
    #NB we force sensible errors by attempting to open the pipeline.cfg file:
    config.read(pipe_cfg_file)
    return parse_to_dict(config)


def get_database_config(config_passed=None, apply=False):
    """
    Determine database config and (optionally) use to set up the Database.

    Determines a database configuration using the settings
    defined in a dict (if supplied) and possibly overridden by
    environment variables.
    The config resulting from the combination of defaults, supplied dict,
    and environment variables is returned as a dict. If apply==True,
    the Database singleton is configured using these resulting settings.

    The following environment variables are recognized, and take priority:

    - TKP_DBENGINE
    - TKP_DBNAME
    - TKP_DBUSER
    - TKP_DBPASSWORD
    - TKP_DBHOST
    - TKP_DBPORT

    :param config_passed: Dict of db settings.
        Relevant keys: (engine, database, user, password, host, port,
        passphrase )
    :param apply: apply settings (configure db connection) or not
    :return: Dict containing the resulting combined settings
        (resulting from defaults, ``config_passed`` and possibly environment
        variables.)
    """
    # Default values
    combined_config = {
        'engine': None, 'database': None, 'user': getpass.getuser(),
        'password': None, 'host': "localhost", 'port': None, 'passphrase': None
    }

    if config_passed:
        combined_config.update(config_passed)

    # The environment variables take precedence
    for env_var, key in [
        ("TKP_DBNAME", 'database'),
        ("TKP_DBUSER", 'user'),
        ("TKP_DBENGINE", 'engine'),
        ("TKP_DBPASSWORD", "password"),
        ("TKP_DBPASSPHRASE", "passphrase"),
        ("TKP_DBHOST", "host"),
        ("TKP_DBPORT", "port")
    ]:
        if env_var in os.environ:
            combined_config[key] = os.environ.get(env_var)

    # If only the username is defined, use that as a
    # default for the database name and password.
    if combined_config['user'] and not combined_config['database']:
        combined_config['database'] = combined_config['user']
    if combined_config['user'] and not combined_config['password']:
        combined_config['password'] = combined_config['user']

    if not combined_config['port']:
        if combined_config['engine'] == "monetdb":
            combined_config['port'] = 50000
        if combined_config['engine'] == "postgresql":
            combined_config['port'] = 5432
    else:
        # Port is always an integer
        combined_config['port'] = int(combined_config['port'])

    # Optionally, initiate a db connection with the settings determined
    if apply:
        tkp.db.Database(**combined_config)
        tkp.db.execute('select 1')
    return combined_config
