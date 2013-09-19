import unittest2 as unittest
import os
import getpass
import ConfigParser

from tkp.config import database_config

DUMMY_VALUE = "dummy"
DUMMY_INT_VALUE = "666"

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

        self.pipeline_cfg = ConfigParser.ConfigParser()

    def tearDown(self):
        os.environ = self.old_environment

    def test_default_values(self):
        # Demonstrate that we get the expected default values
        username = getpass.getuser()
        db_config = database_config()
        self.assertEqual(db_config['engine'], "postgresql")
        self.assertEqual(db_config['database'], username)
        self.assertEqual(db_config['user'], username)
        self.assertEqual(db_config['password'], username)
        self.assertEqual(db_config['host'], "localhost")
        self.assertEqual(db_config['port'], 5432)

    def test_empty_pipeline_cfg(self):
        # Should not raise
        db_config = database_config(self.pipeline_cfg)

    def test_populated_pipeline_cfg(self):
        # Demonstrate that we correctly read a configparser
        self.pipeline_cfg.add_section('database')
        self.pipeline_cfg.set('database', 'engine', DUMMY_VALUE)
        self.pipeline_cfg.set('database', 'database', DUMMY_VALUE)
        self.pipeline_cfg.set('database', 'user', DUMMY_VALUE)
        self.pipeline_cfg.set('database', 'password', DUMMY_VALUE)
        self.pipeline_cfg.set('database', 'host', DUMMY_VALUE)
        self.pipeline_cfg.set('database', 'port', DUMMY_VALUE)
        db_config = database_config(self.pipeline_cfg)
        self._test_for_dummy_values(db_config)

    def test_env_vars(self):
        # Demonstrate that we correctly read the environment
        os.environ["TKP_DBENGINE"] = DUMMY_VALUE
        os.environ["TKP_DBNAME"] = DUMMY_VALUE
        os.environ["TKP_DBUSER"] = DUMMY_VALUE
        os.environ["TKP_DBPASSWORD"] = DUMMY_VALUE
        os.environ["TKP_DBHOST"] = DUMMY_VALUE
        db_config = database_config()
        self._test_for_dummy_values(db_config)

    def test_int_env_vars(self):
        os.environ["TKP_DBPORT"] = DUMMY_INT_VALUE
        db_config = database_config()
        self.assertEqual(db_config['port'], int(DUMMY_INT_VALUE))

    def test_use_username_as_default(self):
        # database name and password default to the username
        os.environ["TKP_DBUSER"] = DUMMY_VALUE
        os.environ["TKP_DBENGINE"] = DUMMY_VALUE
        os.environ["TKP_DBHOST"] = DUMMY_VALUE
        os.environ["TKP_DBPORT"] = DUMMY_INT_VALUE
        db_config = database_config()
        self._test_for_dummy_values(db_config)

    def _test_for_dummy_values(self, db_config):
        self.assertEqual(db_config['engine'], DUMMY_VALUE)
        self.assertEqual(db_config['database'], DUMMY_VALUE)
        self.assertEqual(db_config['user'], DUMMY_VALUE)
        self.assertEqual(db_config['password'], DUMMY_VALUE)
        self.assertEqual(db_config['host'], DUMMY_VALUE)
