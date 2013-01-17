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
        self.accessor = tkp.utility.accessors.open(testdata.fits_file)

    def test_parse_parset(self):
        parset = tempfile.NamedTemporaryFile()
        parset.flush()
        trap.ingredients.quality.parse_parset(parset.name)

    def test_check(self):
        parset = tempfile.NamedTemporaryFile()
        parset.flush()
        image_ids = db_queries.dataset_images(self.dataset_id)
        trap.ingredients.quality.check(image_ids[0], parset.name)
