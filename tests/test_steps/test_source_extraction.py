import unittest
from tkp.steps.source_extraction import extract_sources
from tkp.testutil import db_subs, data
from ConfigParser import SafeConfigParser
from tkp.config import parse_to_dict
from tkp.testutil.data import default_job_config


class TestSourceExtraction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset_id = db_subs.create_dataset_8images()
        config = SafeConfigParser()
        config.read(default_job_config)
        config = parse_to_dict(config)
        cls.parset = config['source_extraction']

    def test_extract_sources(self):
        image_path = data.fits_file
        extract_sources(image_path, self.parset)
