import unittest
from tkp.steps.source_extraction import extract_sources
from tkp.testutil import db_subs, data
import tkp.utility.parset as parset
from tkp.testutil.data import default_parset_paths


class TestSourceExtraction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset_id = db_subs.create_dataset_8images()
        with open(default_parset_paths['source_extraction.parset']) as f:
            cls.parset = parset.read_config_section(f, 'source_extraction')

    def test_extract_sources(self):
        image_path = data.fits_file
        extract_sources(image_path, self.parset)
