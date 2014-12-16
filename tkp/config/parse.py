"""Utilities for loading parameters from config files, with automatic type 
conversion."""

import ast
import logging
import datetime
from tkp.utility import adict

logger = logging.getLogger(__name__)


## Use prefix loads / dumps for 'load string', 'dump string', a la JSON.
dt_w_microsecond_format = '%Y-%m-%dT%H:%M:%S.%f'


def loads_timestamp_w_microseconds(dt_str):
    """Loads and returns timestamp with microsecond precission"""
    return datetime.datetime.strptime(dt_str, dt_w_microsecond_format)

loads_methods = (ast.literal_eval,
                  loads_timestamp_w_microseconds)


def parse_to_dict(config):
    """Loads the ConfigParser object as a nested dictionary.
    
    Automatically converts strings representing ints and floats to their
    respective types, through the magic of ast.literal_eval.
    This functionality is extensible via the loads_methods list.
    Each loads (load string) method is tested in turn to see if it 
    throws an exception. If all throw, we assume the value is meant to be
    string. 

    Any values that you don't want to be converted should simply be 
    surrounded with quote marks in the parset - then ast.literal_eval
    knows to load it as a string. 

    
    Args:
      config: A ConfigParser object.
      
    Returns:
        Nested dict {sections -> keys -> values } representing parsed params.
    
    """
    pars = adict()
    #'DEFAULT' section is not listed by ``sections()``,
    # but we sometimes (ab)use it.
    sections = config.sections()
    if len(config.items('DEFAULT')):
        sections.append('DEFAULT')

    for section_name in sections:
        if section_name not in pars:
            pars[section_name] = adict()
        for k, rawval in config.items(section_name):
            val = rawval
            for func in loads_methods:
                try:
                    val = func(rawval)
                    break  # Drop out of loop if exception not thrown
                except (ValueError, SyntaxError):
                    pass  # Try the next method
            if val == rawval:
                logger.debug("Parsing section: [%s]\n"
                             "Could not parse key-value pair:\n%s = %s\n"
                             "-assuming string value",
                             section_name, k, rawval)
            pars[section_name][k] = val

    return pars
