import unittest
import tempfile
import tkp.steps.transient_search
from tkp.testutil import db_subs, db_queries
from tkp.testutil.decorators import requires_database

@requires_database()
class TestTransientSearch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset_id = db_subs.create_dataset_8images(extract_sources=True)
        cls.parset = tempfile.NamedTemporaryFile()
        parset_text = """\
# set the probability threshold (0 to 1) that a source is a transient (i.e. not a constant flux)
probability.threshold = 0.5
probability.minpoints = 1
probability.eta_lim = 0.0
probability.V_lim = 0.00

"""
        cls.parset.write(parset_text)
        cls.parset.flush()

    def test_search_transients(self):
        image_ids = db_queries.dataset_images(self.dataset_id)
        tkp.steps.transient_search.search_transients(image_ids[0],
                                                self.parset.name)
