from __future__ import absolute_import

from ConfigParser import SafeConfigParser
import datetime
import getpass
import logging
import os

from tkp.config.parse import parse_to_dict, dt_w_microsecond_format
import tkp.db

logger = logging.getLogger(__name__)


def initialize_pipeline_config(pipe_cfg_file, job_name=False):
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


def get_database_config(pipeline_config=None, apply=None):
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

    args:
        pipeline_config: Dict of db settings.
            Relevant keys: (engine, database, user, password, host, port,
            passphrase )
        apply: apply settings (configure db connection) or not
    returns:
        dict: containing the resulting combined settings
            (resulting from defaults, ``config_passed`` and possibly environment
            variables.)
    """

    user = getpass.getuser()
    # Default values
    combined = {
        'engine': None,
        'database': user,
        'user': None,
        'password': None,
        'host': "localhost",
        'port': None,
        'passphrase': None
    }

    if pipeline_config:
        combined.update(pipeline_config)

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
            combined[key] = os.environ.get(env_var)

    if not combined['engine']:
        combined['engine'] = 'postgresql'

    if not combined['user']:
        if combined['engine'] == 'monetdb':
            combined['user'] = 'monetdb'
        else:
            combined['user'] = user

    if not combined['password']:
        combined['password'] = combined['user']

    if not combined['port']:
        if combined['engine'] == "monetdb":
            combined['port'] = 50000
        if combined['engine'] == "postgresql":
            combined['port'] = 5432
    else:
        # Port is always an integer
        combined['port'] = int(combined['port'])

    if not combined['database']:
        combined['database'] = combined['user']

    # Optionally, initiate a db connection with the settings determined
    if apply:
        tkp.db.Database(**combined)
    return combined
