import unittest
import numpy as np
from configparser import SafeConfigParser
from tkp.config import parse_to_dict
from tkp.testutil.data import default_job_config
from tkp.testutil.decorators import requires_data, requires_database
from tkp.testutil.mock import Mock
import tkp.steps.source_extraction
from tkp.db import DataSet
from tkp.testutil.data import fits_file


class MockImage(Mock):
    def extract(self, *args, **kwargs):
        return self.__call__(*args, **kwargs)
    @property
    def rmsmap(self, *args, **kwargs):
        return np.zeros((1))


class TestSourceExtraction(unittest.TestCase):
    @classmethod
    @requires_database()
    def setUpClass(cls):
        dataset = DataSet(data={'description': "Test source extraction step"})
        cls.dataset_id = dataset.id
        config = SafeConfigParser()
        config.read(default_job_config)
        config = parse_to_dict(config)
        cls.parset = config['source_extraction']

    @requires_data(fits_file)
    def test_extract_sources(self):
        image_path = fits_file
        accessor = tkp.accessors.open(image_path)
        tkp.steps.source_extraction.extract_sources(accessor, self.parset)

    @requires_data(fits_file)
    def test_for_appropriate_arguments(self):
        # sourcefinder_image_from_accessor() should get a single positional
        # argument, which is the accessor, and four kwargs: back_sizex,
        # back_sizey, margin and radius.
        # The object it returns has an extract() method, which should have
        # been called with det, anl, force_beam and deblend_nthresh kwargs.
        image_path = fits_file
        mock_method = Mock(MockImage([]))
        orig_method = tkp.steps.source_extraction.sourcefinder_image_from_accessor
        tkp.steps.source_extraction.sourcefinder_image_from_accessor = mock_method
        accessor = tkp.accessors.open(image_path)
        tkp.steps.source_extraction.extract_sources(accessor, self.parset)
        tkp.steps.source_extraction.sourcefinder_image_from_accessor = orig_method

        # Arguments to sourcefinder_image_from_accessor()
        self.assertIn('radius', mock_method.callvalues[0][1])
        self.assertIn('margin', mock_method.callvalues[0][1])
        self.assertIn('back_size_x', mock_method.callvalues[0][1])
        self.assertIn('back_size_y', mock_method.callvalues[0][1])

        # Arguments to extract()
        self.assertIn('det', mock_method.returnvalue.callvalues[0][1])
        self.assertIn('anl', mock_method.returnvalue.callvalues[0][1])
        self.assertIn('force_beam', mock_method.returnvalue.callvalues[0][1])
        self.assertIn('deblend_nthresh', mock_method.returnvalue.callvalues[0][1])
