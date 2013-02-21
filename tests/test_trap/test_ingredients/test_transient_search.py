import unittest
import tempfile
import trap.steps.transient_search
from tkp.testutil import db_subs, db_queries
from tkp.testutil.decorators import requires_database

@requires_database()
class TestTransientSearch(unittest.TestCase):
    def __init__(self, *args):
        super(TestTransientSearch, self).__init__(*args)
        self.dataset_id = db_subs.create_dataset_8images(extract_sources=True)
        self.parset = tempfile.NamedTemporaryFile()
        parset_text = """\
# set the probability threshold (0 to 1) that a source is a transient (i.e. not a constant flux)
probability.threshold = 0.5
probability.minpoints = 1
probability.eta_lim = 0.0
probability.V_lim = 0.00

"""
        self.parset.write(parset_text)
        self.parset.flush()

    def test_search_transients(self):
        image_ids = db_queries.dataset_images(self.dataset_id)
        trap.steps.transient_search.search_transients(image_ids[0],
                                                self.parset.name)
