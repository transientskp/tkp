import unittest
import tempfile
import trap.ingredients.transient_search
from tkp.testutil import db_subs, db_queries

class TestTransientSearch(unittest.TestCase):
    def __init__(self, *args):
        super(TestTransientSearch, self).__init__(*args)
        self.dataset_id = db_subs.create_dataset_8images(extract_sources=True)
        self.parset = tempfile.NamedTemporaryFile()
        self.parset.flush()

    def test_search_transients(self):
        image_ids = db_queries.dataset_images(self.dataset_id)
        trap.ingredients.transient_search.search_transients(image_ids,
                                            self.dataset_id, self.parset.name)
