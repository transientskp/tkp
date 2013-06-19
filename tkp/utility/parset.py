"""Utilities for loading parameters from config files, with automatic type 
conversion."""

import ConfigParser
import ast
import logging

import datetime

logger = logging.getLogger(__name__)

dt_w_microsecond_format = '%Y-%m-%dT%H:%M:%S.%f'

## Use prefix loads / dumps for 'load string', 'dump string', a la JSON.

def loads_timestamp_w_microseconds(dt_str):
    return datetime.datetime.strptime(dt_str, dt_w_microsecond_format)

def dumps_timestamp_w_microseconds(dt):
    return dt.strftime(dt_w_microsecond_format)

#NB default dumps_method is 'repr' (implemented in dump_section)
dumps_methods = { datetime.datetime : dumps_timestamp_w_microseconds}
loads_methods = (ast.literal_eval,
                  loads_timestamp_w_microseconds)

def load_section(config, section):
    """Loads the specified section of a parset file as a dictionary.
    
    Automatically converts strings representing ints and floats to their
    respective types, through the magic of ast.literal_eval.
    This functionality is extensible via the loads_methods list.
    Each loads (load string) method is tested in turn to see if it 
    throws an exception. If all throw, we assume the value is meant to be
    string. 

    Any values that you don't want to be converted should simply be 
    surrounded with quote marks in the parset - then ast.literal_eval
    knows to load it as a string. 

    Note that as a feature of ConfigParser, and variable defined in 
    the section 'DEFAULT' are present in all other sections, 
    so you might get more than you expected.
    """
    pars = {}
    for k, rawval in config.items(section):
        val = rawval
        for func in loads_methods:
            try:
                val = func(rawval)
                break #Drop out of loop if exception not thrown
            except (ValueError, SyntaxError):
                pass #Try the next method
        if val == rawval:
            logger.debug("Parsing section: [%s]\n"
                        "Could not parse key-value pair:\n%s = %s\n"
                                "-assuming string value",
                                section, k, rawval)
        pars[k] = val

    return pars

def dump_section(config, section, params):
    """
    Writes a dictionary (params) into a ConfigParser object, 
    under the specified section header.
    
    Normally ConfigParser only accepts string values, but here
    type conversion to string is handled automatically via the dumps_methods
    (dump string methods). This uses the type of a variable to check if 
    we have defined a specific output method. Otherwise, we try the 
    standard 'repr' function.
    
    """
    if not section in config.sections():
        config.add_section(section)
    for k, v in params.iteritems():
        dumps_func = dumps_methods.get(type(v), repr)
        config.set(section, k, dumps_func(v))


def read_config_section(fp, section):
    conf = ConfigParser.SafeConfigParser()
    conf.readfp(fp)
    return load_section(conf, section)

def write_config_section(fp, section, params):
    conf = ConfigParser.SafeConfigParser()
    dump_section(conf, section, params)
    conf.write(fp)



