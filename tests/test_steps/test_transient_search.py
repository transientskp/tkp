import unittest
import tempfile
import tkp.steps.transient_search
from tkp.testutil import db_subs, db_queries
from tkp.testutil.decorators import requires_database
import tkp.db

@requires_database()
class TestTransientSearch(unittest.TestCase):

    def tearDown(self):
        tkp.db.rollback()

    @classmethod
    def setUpClass(cls):
        cls.dataset_id = db_subs.create_dataset_8images(extract_sources=True)
        cls.fake_parset = tempfile.NamedTemporaryFile()
        parset_text = """\
threshold = 0.5
minpoints = 1
eta_lim = 0.0
V_lim = 0.00
"""
        cls.fake_parset.write(parset_text)
        cls.fake_parset.flush()
        cls.parset = {
            'threshold': 0.5,
            'minpoints': 1,
            'eta_lim': 0.0,
            'V_lim': 0.00,
        }

    def test_parse_parset(self):
        tkp.steps.transient_search.parse_parset(self.fake_parset)

    def test_search_transients(self):
        image_ids = db_queries.dataset_images(self.dataset_id)
        tkp.steps.transient_search.search_transients(image_ids[0], self.parset)
