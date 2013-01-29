import unittest
import tempfile
import trap.ingredients.source_extraction
from tkp.testutil import db_subs, db_queries, data

class TestSourceExtraction(unittest.TestCase):
    def __init__(self, *args):
        super(TestSourceExtraction, self).__init__(*args)
        self.dataset_id = db_subs.create_dataset_8images()
        self.parset = tempfile.NamedTemporaryFile()
        self.parset.write("detection.threshold = 15\n")
        self.parset.write("association.radius = 1\n")
        self.parset.flush()

    def test_extract_sources(self):
        image_path = data.fits_file
        trap.ingredients.source_extraction.extract_sources(image_path, self.parset.name)
