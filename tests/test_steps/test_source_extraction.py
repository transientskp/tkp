import unittest
from tkp.steps.source_extraction import extract_sources
from tkp.testutil import db_subs, data
from tkp.conf import read_config_section
from tkp.testutil.data import default_job_config


class TestSourceExtraction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset_id = db_subs.create_dataset_8images()
        with open(default_job_config) as f:
            cls.parset = read_config_section(f, 'source_extraction')

    def test_extract_sources(self):
        image_path = data.fits_file
        extract_sources(image_path, self.parset)
