import unittest2 as unittest
import os
import getpass
import datetime
import StringIO
from ConfigParser import SafeConfigParser

from tkp.testutil.data import (default_job_config, default_pipeline_config,
                               default_header_inject_config)
from tkp.conf import dt_w_microsecond_format, parse_to_dict
from tkp.config import get_database_config, initialize_pipeline_config

DUMMY_VALUE = "dummy"
DUMMY_INT = 1234



class TestParsingCode(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Create manually parsed OrderedDict to check against"""

        example_config_str = """\
[test1]
float = 0.5 ; some comment
int = 1
string1 = bob               ; default to string when no other parsers work
time1 = 2007-07-20T14:18:09.909001    ; times are parsed if matching this format
#But must have at least a single digit after the decimal point:
time2 = 2007-07-20T14:18:09.0
[test2]
string2 = "0.235"           ; force string by enclosing in double-quotes

"""

        cls.config = SafeConfigParser()
        cls.config.readfp(StringIO.StringIO(example_config_str))

        cls.parset = {}
        cls.parset['test1']= {
            'float':0.5,
            'int':1,
            'string1':'bob',
            'time1':datetime.datetime.strptime('2007-07-20T14:18:09.909001',
                                                dt_w_microsecond_format),
            'time2':datetime.datetime.strptime('2007-07-20T14:18:09.0',
                                                dt_w_microsecond_format)
        }

        cls.parset['test2']= {'string2':'0.235'}


    def test_parser(self):
        parsed = parse_to_dict(self.config)
        self.assertEqual(parsed, self.parset)


class TestConfigParsing(unittest.TestCase):
    """Ensure that the default config files get parsed as expected"""
    def test_default_job_config(self):
        c = SafeConfigParser()
        c.read(default_job_config)
        job_config = parse_to_dict(c)

    def test_default_pipeline_config(self):
        pipe_config = initialize_pipeline_config(default_pipeline_config, 'test')

    def test_default_inject_config(self):
        c = SafeConfigParser()
        c.read(default_header_inject_config)
        inject_config = parse_to_dict(c)




class DatabaseConfigTestCase(unittest.TestCase):
    def setUp(self):
        # Wipe out any pre-existing environment settings
        self.old_environment = os.environ.copy()
        os.environ.pop("TKP_DBENGINE", None)
        os.environ.pop("TKP_DBNAME", None)
        os.environ.pop("TKP_DBUSER", None)
        os.environ.pop("TKP_DBPASSWORD", None)
        os.environ.pop("TKP_DBHOST", None)
        os.environ.pop("TKP_DBPORT", None)

        self.pipeline_cfg = initialize_pipeline_config(default_pipeline_config,
                                                       'test')

    def tearDown(self):
        os.environ = self.old_environment

    def test_unconfigured(self):
        # Should *not* raise.
        get_database_config()

    def test_invalid_dbengine(self):
        # Should *not* raise; database_config does not sanity check.
        os.environ["TKP_DBENGINE"] = DUMMY_VALUE
        get_database_config()

    def test_defaults_postgresql(self):
        # Demonstrate that we get the expected default values
        os.environ["TKP_DBENGINE"] = "postgresql"
        username = getpass.getuser()
        db_config = get_database_config()
        self.assertEqual(db_config['engine'], "postgresql")
        self.assertEqual(db_config['database'], username)
        self.assertEqual(db_config['user'], username)
        self.assertEqual(db_config['password'], username)
        self.assertEqual(db_config['host'], "localhost")
        self.assertEqual(db_config['port'], 5432)

    def test_defaults_monetdb(self):
        # Demonstrate that we get the expected default values
        os.environ["TKP_DBENGINE"] = "monetdb"
        username = getpass.getuser()
        db_config = get_database_config()
        self.assertEqual(db_config['engine'], "monetdb")
        self.assertEqual(db_config['database'], username)
        self.assertEqual(db_config['user'], username)
        self.assertEqual(db_config['password'], username)
        self.assertEqual(db_config['host'], "localhost")
        self.assertEqual(db_config['port'], 50000)

    def test_populated_pipeline_cfg(self):
        # Demonstrate that we correctly read a configparser
        self.pipeline_cfg['database']['engine'] =  "monetdb"
        self.pipeline_cfg['database']['database'] = DUMMY_VALUE
        self.pipeline_cfg['database']['user'] = DUMMY_VALUE
        self.pipeline_cfg['database']['password'] = DUMMY_VALUE
        self.pipeline_cfg['database']['host'] = DUMMY_VALUE
        self.pipeline_cfg['database']['port'] = DUMMY_INT
        self._test_for_dummy_values(self.pipeline_cfg['database'])

    def test_env_vars(self):
        # Demonstrate that we correctly read the environment
        os.environ["TKP_DBENGINE"] = "monetdb"
        os.environ["TKP_DBNAME"] = DUMMY_VALUE
        os.environ["TKP_DBUSER"] = DUMMY_VALUE
        os.environ["TKP_DBPASSWORD"] = DUMMY_VALUE
        os.environ["TKP_DBHOST"] = DUMMY_VALUE
        os.environ["TKP_DBPORT"] = DUMMY_INT
        db_config = get_database_config(self.pipeline_cfg['database'])
        self._test_for_dummy_values(db_config)

    def test_use_username_as_default(self):
        # database name and password default to the username
        os.environ["TKP_DBUSER"] = DUMMY_VALUE
        os.environ["TKP_DBENGINE"] = "monetdb"
        os.environ["TKP_DBHOST"] = DUMMY_VALUE
        os.environ["TKP_DBPORT"] = DUMMY_INT
        db_config = get_database_config(self.pipeline_cfg['database'])
        self._test_for_dummy_values(db_config)

    def _test_for_dummy_values(self, db_config):
        self.assertEqual(db_config['engine'], "monetdb")
        self.assertEqual(db_config['database'], DUMMY_VALUE)
        self.assertEqual(db_config['user'], DUMMY_VALUE)
        self.assertEqual(db_config['password'], DUMMY_VALUE)
        self.assertEqual(db_config['host'], DUMMY_VALUE)
        self.assertEqual(db_config['port'], int(DUMMY_INT))
