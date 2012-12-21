import unittest
import tempfile
import trap.ingredients.source_extraction
from tkp.testutil import db_subs, db_queries

class TestSourceExtraction(unittest.TestCase):
    def __init__(self, *args):
        super(TestSourceExtraction, self).__init__(*args)
        self.dataset_id = db_subs.create_dataset_8images()
        self.parset = tempfile.NamedTemporaryFile()
        self.parset.write("detection.threshold = 15\n")
        self.parset.write("association.radius = 1\n")
        self.parset.flush()

    def test_extract_sources(self):
        image_ids = db_queries.dataset_images(self.dataset_id)
        trap.ingredients.source_extraction.extract_sources(image_ids[0], self.parset.name)
