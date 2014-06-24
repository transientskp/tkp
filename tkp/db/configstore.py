"""
store and retrieve pipeline settings to/from database
"""
import logging
from tkp.db import execute
from tkp.utility import adict

# the types of values we accept
types = [str, int, float, bool]

logger = logging.getLogger(__name__)

store_query = """
INSERT INTO config (dataset, section, key, value, type)
  VALUES (%(dataset)s, %(section)s, %(key)s, %(value)s, %(type)s);
"""


def store_config(config, dataset_id):
    """
    Store a config defined in d into the database.

    Args:
        config (dict): nested dict containing config, [section][key] -> [value]
    """
    logger.info("storing config to database for dataset %s" % dataset_id)
    error = "type of value %s, key %s in section %s has type %s, we only do %s"
    for section, v in config.items():
        for key, value in v.items():
            if key == 'password':
                logger.debug("not storing %s password to DB" % section)
                continue
            if type(value) not in types:
                msg = error % (value, key, section, type(value).__name__,
                               ", ".join(t.__name__ for t in types))
                logger.error(msg)
                raise TypeError(msg)

            values = {'dataset': dataset_id, 'section': section, 'key': key,
                      'value': str(value), 'type': type(value).__name__}
            execute(store_query, values)


fetch_query = """
SELECT section, key, value, type FROM config where dataset=%(dataset)s;
"""


def fetch_config(dataset_id):
    """
    Retrieve the stored config for given dataset id

    Returns:
        nested dict [section][key] -> [value]
    """
    logger.info("fetching config from database for dataset %s" % dataset_id)
    error = "type in database is %s but we only support %s"
    result = execute(fetch_query, {'dataset': dataset_id}).fetchall()
    config = adict()
    for section, key, value, type_ in result:
        if type_ not in (t.__name__ for t in types):
            msg = error % (type_, ", ".join(t.__name__ for t in types))
            logger.error(msg)
            raise TypeError(msg)
        converted = eval(type_)(value)
        if not section in config:
            config[section] = adict()
        config[section][key] = converted
    return config
