import unittest
import tkp.steps.transient_search
from tkp.testutil import db_subs, db_queries
from tkp.testutil.decorators import requires_database
import tkp.db
from ConfigParser import SafeConfigParser
from tkp.config import parse_to_dict
from tkp.testutil.data import default_job_config

@requires_database()
class TestTransientSearch(unittest.TestCase):

    def tearDown(self):
        tkp.db.rollback()

    @classmethod
    def setUpClass(cls):
        cls.dataset_id = db_subs.create_dataset_8images(extract_sources=True)
        config = SafeConfigParser()
        config.read(default_job_config)
        config = parse_to_dict(config)
        cls.parset =config['transient_search']

    def test_search_transients(self):
        image_ids = db_queries.dataset_images(self.dataset_id)
        tkp.steps.transient_search.search_transients(image_ids[0], self.parset)
