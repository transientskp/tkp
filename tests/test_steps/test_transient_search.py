import unittest
import tkp.steps.transient_search
from tkp.testutil import db_subs, db_queries
from tkp.testutil.decorators import requires_database
import tkp.db
import tkp.utility.parset as parset
from tkp.testutil.data import default_parset_paths

@requires_database()
class TestTransientSearch(unittest.TestCase):

    def tearDown(self):
        tkp.db.rollback()

    @classmethod
    def setUpClass(cls):
        cls.dataset_id = db_subs.create_dataset_8images(extract_sources=True)
        with open(default_parset_paths['transient_search.parset']) as f:
            cls.parset = parset.read_config_section(f, 'transient_search')

    def test_search_transients(self):
        image_ids = db_queries.dataset_images(self.dataset_id)
        tkp.steps.transient_search.search_transients(image_ids[0], self.parset)
