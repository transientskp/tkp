import unittest
import tempfile
from tkp.steps.source_extraction import extract_sources, parse_parset
from tkp.testutil import db_subs, data

class TestSourceExtraction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset_id = db_subs.create_dataset_8images()
        cls.parset = tempfile.NamedTemporaryFile()
        parset_text = """\
detection_threshold = 15
analysis_threshold = 5
backsize_x = 32
backsize_y = 32
margin = 10
deblend = False
deblend_nthresh = 32
radius = 280
ra_sys_err = 20
dec_sys_err = 20
"""
        cls.parset.write(parset_text)
        cls.parset.flush()

    def test_extract_sources(self):
        image_path = data.fits_file
        parset = parse_parset(self.parset.name)
        extract_sources(image_path, parset)
