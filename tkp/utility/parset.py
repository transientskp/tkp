import ConfigParser
import ast
import datetime

import logging
logger = logging.getLogger(__name__)

dt_w_microsecond_format = '%Y-%m-%dT%H:%M:%S.%f'

## Use prefix loads / dumps for 'load string', 'dump string', a la JSON.

def loads_timestamp_w_microseconds(dt_str):
    return datetime.datetime.strptime(dt_str, dt_w_microsecond_format)

def dumps_timestamp_w_microseconds(dt):
    return dt.strftime(dt_w_microsecond_format)

#NB default dumps_method is 'repr' (implemented in dump_section)
dumps_methods = { datetime.datetime : dumps_timestamp_w_microseconds}
loads_methods = [ ast.literal_eval,
                  loads_timestamp_w_microseconds]

def load_section(config, section):
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
            logger.warn("Parsing section: [%s]\n"
                        "Could not parse key-value pair:\n%s = %s\n"
                                "-assuming string value",
                                section, k, rawval)
        pars[k] = val

    return pars

def dump_section(config, section, params):
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



