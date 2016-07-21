import unittest
from ConfigParser import SafeConfigParser
import tkp.steps.quality
import tkp.accessors
from tkp.telescope.lofar.quality import reject_check_lofar
from tkp.testutil.decorators import requires_data
from tkp.testutil.data import default_job_config
from tkp.testutil.data import fits_file
from tkp.config import parse_to_dict


@requires_data(fits_file)
class TestQuality(unittest.TestCase):
    def setUp(self):
        self.accessor = tkp.accessors.open(fits_file)
        config = SafeConfigParser()
        config.read(default_job_config)
        self.job_config = parse_to_dict(config)

    def test_check(self):
        tkp.steps.quality.reject_check(self.accessor, self.job_config)

    def test_zero_integration(self):
        self.accessor._tau_time = 0
        result = reject_check_lofar(self.accessor, self.job_config)
        self.assertTrue(result)
