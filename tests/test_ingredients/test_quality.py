import unittest
import tempfile
import trap.ingredients.quality
from tkp.testutil import db_subs, db_queries
import tkp.utility.accessors
import tkp.testutil.data as testdata

class TestQuality(unittest.TestCase):
    def __init__(self, *args):
        super(TestQuality, self).__init__(*args)
        self.dataset_id = db_subs.create_dataset_8images()
        self.parset = tempfile.NamedTemporaryFile()
        self.parset.flush()
        self.accessor = tkp.utility.accessors.open(testdata.fits_file)

    def test_parse_parset(self):
        trap.ingredients.quality.parse_parset(self.parset.name)

    def test_parse_parset_with_accessor(self):
        trap.ingredients.quality.parse_parset(self.parset.name, self.accessor)

    def test_check(self):
        image_ids = db_queries.dataset_images(self.dataset_id)
        trap.ingredients.quality.check(image_ids[0], self.parset.name)
