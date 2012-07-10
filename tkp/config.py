"""

The config module stores the default values for various tunable parameters
in the TKP Python package.

The module also tries to read (in order):

- a :file:`.transientskp/tkp.cfg` file in the users home directory

- a :file:`.tkp.cfg` file in the users home directory,

where parameters can be overriden (such as the database login details).

There are three sections in the configuration:

- database

- source_association

- source_extraction

The parameters are stored in a dictionary, with each section as keyword.
Each value in itself is another dictionary, with (option, value) pairs.

The config module can be imported by the various subpackages of the
TKP package.  Since the :file:`.transientskp/tkp.cfg` or
:file:`.tkp.cfg` file is only read on first import, after which the
variable HAS_READ is set to False, there are no multiple reads of this
file.

"""

from __future__ import with_statement
import ConfigParser
import os
import os.path
import logging


_TO_DO = """\

To do:

- avoid the HAS_READ / NameError trick below,
  possibly by use of a singleton

- (optional) use class instead of dictionary to store options

"""


CONFIGFILE = ''
CONFIGDIR = None
CONFIGFILES = ['~/.transientskp/tkp.cfg', '~/.tkp.cfg']
if 'TKPCONFIGDIR' in os.environ:
    CONFIGDIR = os.environ['TKPCONFIGDIR']
    if os.path.exists(os.path.join(CONFIGDIR, 'tkp.cfg')):
        CONFIGFILES.insert(0, os.path.join(CONFIGDIR, 'tkp.cfg'))

# Avoid eval
# This is very simple, and likely may be fooled by incorrect
# input
def double_list_from_string(text, contenttype=str):
    """Helper function to parse a double list from a string"""

    origtext = text[:]
    if contenttype not in (str, int, float, bool):
        raise ValueError("unknown or not allowed contenttype")
    text = origtext.strip()
    if text[0] != '[':
        raise ValueError("%s does not start with a list" % origtext)
    text = text[1:].strip()
    if text[0] != '[':
        raise ValueError("%s is not a valid double list" % origtext)
    text = text[1:].strip()
    elements = []
    while True:
        i = text.find(']')
        part = text[:i]
        #elements.append(map(contenttype, part.split(',')))
        elements.append([contenttype(var) for var in part.split(',')])
        try:
            text = text[i+1:].strip()
        except IndexError:
            raise ValueError("%s is incorrect format" % origtext)
        if text[0] == ']':  # closing outer list
            break
        tmptext = text.lstrip(',').strip()
        if tmptext == text:
            raise ValueError("missing separating comma in %s" % origtext)
        text = tmptext.lstrip('[').strip()
        if tmptext == text:
            raise ValueError("missing opening bracket in %s" % origtext)

    return elements


def set_default_config():
    """Set up the default configuration"""

    config = ConfigParser.SafeConfigParser()

    config.add_section('database')
    config.set('database', 'enabled', 'True')
    config.set('database', 'host', 'ldb001')
    config.set('database', 'name', 'tkp')
    config.set('database', 'user', 'tkp')
    config.set('database', 'password', 'tkp')
    config.set('database', 'port', '0')
    config.set('database', 'autocommit', 'False')
    config.set('database', 'engine', 'monetdb')

    config.add_section('source_association')
    config.set('source_association', 'deruiter_radius', '3.7')
    #config.set('source_association', 'deruiter_radius', '0.00112')
    #config.set('source_association', 'deruiter_radius', '0.065')
    config.set('source_association', 'bg-density', '4.02439375e-06')  # NVSS density

    config.add_section('source_extraction')
    config.set('source_extraction', 'back_sizex', '32')
    config.set('source_extraction', 'back_sizey', '32')
    config.set('source_extraction', 'median_filter', '0')
    config.set('source_extraction', 'mf_threshold', '0')
    config.set('source_extraction', 'interpolate_order', '1')
    config.set('source_extraction', 'margin', '0')
    config.set('source_extraction', 'max_degradation', '0.2')
    config.set('source_extraction', 'fdr_alpha', '1e-2')
    config.set('source_extraction', 'structuring_element',
               '[[0,1,0], [1,1,1], [0,1,0]]')
    config.set('source_extraction', 'deblend', 'False')
    config.set('source_extraction', 'deblend_nthresh', '32')
    config.set('source_extraction', 'deblend_mincont', '0.005')
    config.set('source_extraction', 'detection_threshold', '10.0')
    config.set('source_extraction', 'analysis_threshold', '3.0')
    config.set('source_extraction', 'residuals', 'True')
    config.set('source_extraction', 'alpha_maj1', '2.5')
    config.set('source_extraction', 'alpha_min1', '0.5')
    config.set('source_extraction', 'alpha_maj2', '0.5')
    config.set('source_extraction', 'alpha_min2', '2.5')
    config.set('source_extraction', 'alpha_maj3', '1.5')
    config.set('source_extraction', 'alpha_min3', '1.5')
    config.set('source_extraction', 'clean_bias', '0.0')
    config.set('source_extraction', 'clean_bias_error', '0.0')
    config.set('source_extraction', 'frac_flux_cal_error', '0.0')
    config.set('source_extraction', 'eps_ra', '0.')
    config.set('source_extraction', 'eps_dec', '0.')

    config.add_section('transient_search')
    config.set('transient_search', 'probability', '0.99')
    config.set('transient_search', 'minpoints', '2')
    config.set('transient_search', 'eta_lim', '3.')
    config.set('transient_search', 'V_lim', '0.')

    config.add_section('logging')
    config.set('logging', 'level', 'ERROR')
    config.set('logging', 'format',
               '%%(asctime)s - %%(name)s - %%(levelname)s - %%(message)s')
    config.set('logging', 'filename', '')

    config.add_section('alerts')
    config.set('alerts', 'login', '')
    config.set('alerts', 'password', '')
    config.set('alerts', 'server', '')
    config.set('alerts', 'port', '0')

    from tkp import __path__ as testpath
    config.add_section('test')
    config.set('test', 'datapath', os.path.join(testpath[0], "tests", "data"))
    config.set('test', 'test_database_name', 'testdb')
    config.set('test', 'reset_test_database', 'False')
    config.set('test', 'test_database_dump_dir', 'None')
    return config


def write_config(config=None, filename=CONFIGFILES[0]):
    """
    Dump configuration to file.

    Convenient for generating an initial template configuration file for the
    user to edit to suit their requirements.
    """
    if not config:
        config=set_default_config()
    filename = os.path.expanduser(filename)
    try:
        os.makedirs(os.path.dirname(filename))
    except OSError:   # directory already exists, presumably
        pass
    with open(filename, "w") as cfg_file:
        config.write(cfg_file)


def read_config(default_config):
    """Attempt to read a user configuration file"""

    global CONFIGFILE
    config = ConfigParser.SafeConfigParser()
    # Don't try and read multiple files (which can be done with
    # ConfigParser.read()); instead, if one is missing, try the other:
    for filename in CONFIGFILES:
        if config.read(os.path.expanduser(filename)):
            CONFIGFILE = os.path.expanduser(filename)
            break

    # Check for unknown sections or options
    for section in config.sections():
        if not default_config.has_section(section):
            raise ConfigParser.Error("unknown section %s" % section)
        for option in config.options(section):
            if not default_config.has_option(section, option):
                raise ConfigParser.Error(
                    "unknown option %s in section %s" % (option, section))
    # Now overwrite default options
    for section in default_config.sections():
        if not config.has_section(section):
            config.add_section(section)
        for option in default_config.options(section):
            if not config.has_option(section, option):
                config.set(section, option,
                           default_config.get(section, option))

    return config


def parse_config(config):
    """Parse the various config parameters into a dictionary,
    including type conversion"""

    # On to do list: create an inherited configparser that stores a type with
    # the options, and then does the parsing behind the scenes
    configuration = dict(database={}, source_association={},
                         source_extraction={})
    booleans = (('database', 'enabled'), ('database', 'autocommit'),
                ('source_extraction', 'deblend'),
                ('source_extraction', 'residuals'))
    integers = (('database', 'port'), ('source_extraction', 'back_sizex'),
                ('source_extraction', 'back_sizey'),
                ('source_extraction', 'median_filter'),
                ('source_extraction', 'interpolate_order'),
                ('source_extraction', 'deblend_nthresh'),
                ('transient_search', 'minpoints'),
                ('alerts', 'port'),
                )
    floats = (('source_association', 'deruiter_radius'),
              ('source_extraction', 'mf_threshold'),
              ('source_extraction', 'margin'),
              ('source_extraction', 'max_degradation'),
              ('source_extraction', 'fdr_alpha'),
              ('source_extraction', 'deblend_mincont'),
              ('source_extraction', 'detection_threshold'),
              ('source_extraction', 'analysis_threshold'),
              ('source_extraction', 'alpha_maj1'),
              ('source_extraction', 'alpha_min1'),
              ('source_extraction', 'alpha_maj2'),
              ('source_extraction', 'alpha_min2'),
              ('source_extraction', 'alpha_maj3'),
              ('source_extraction', 'alpha_min3'),
              ('source_extraction', 'clean_bias'),
              ('source_extraction', 'clean_bias_error'),
              ('source_extraction', 'frac_flux_cal_error'),
              ('source_extraction', 'eps_ra'),
              ('source_extraction', 'eps_dec'),
              ('transient_search', 'probability'),
              ('transient_search', 'eta_lim'),
              ('transient_search', 'V_lim'),
              )
    configuration.update(dict([(section, dict(config.items(section, raw=True)))
                               for section in config.sections()]))
    for section, option in booleans:
        try:
            configuration[section][option] = config.getboolean(section, option)
        except ValueError:
            raise ValueError(
        "incorrect type for option %s in section %s; must be boolean "
        "(True/False)" % (option, section))
    for section, option in integers:
        try:
            configuration[section][option] = config.getint(section, option)
        except ValueError:
            raise ValueError(
        "incorrect type for option %s in section %s; must be an integer" %
        (option, section))
    for section, option in floats:
        try:
            configuration[section][option] = config.getfloat(section, option)
        except ValueError:
            raise ValueError(
        "incorrect type for option %s in section %s; must be a real number" %
        (option, section))
    elements = double_list_from_string(config.get(
        'source_extraction', 'structuring_element'), contenttype=float)
    if (len(elements) != 3 or len(elements[0]) != 3 or len(elements[1]) != 3
        or len(elements[2]) != 3):
        raise ValueError("""\
incorrect type for structuring_element in section source_extraction""")
    configuration['source_extraction']['structuring_element'] = elements
    if configuration['database']['engine'] == 'postgresql':
        # PostgreSQL does not have autocommit
        configuration['database']['autocommit'] = False
    return configuration


def configure_logger(config):
    """Configure the TKP logger"""

    levels = {
        'CRITICAL': logging.CRITICAL,
        'ERROR': logging.ERROR,
        'WARNING': logging.WARNING,
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG
        }
    # Don't simply take the dict as is.
    # Eg, an empty filename means using a StreamHandler, otherwise a FileHandler
    if config['filename']:
        handler = logging.FileHandler(config['filename'])
    else:
        handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(config['format']))
    logger = logging.getLogger('tkp')
    logger.addHandler(handler)
    logger.setLevel(levels[config['level'].upper()])


# This is a bit of a dirty trick; using some kind of singleton class
# with a class variable may be better, though I guess it's currently
# similar: a singleton module with module variable.
try:
    HAS_READ
except NameError, exc:
    config = read_config(set_default_config())
    config = parse_config(config)
    configure_logger(config['logging'])
    HAS_READ = True
else:
    pass
