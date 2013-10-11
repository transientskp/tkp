import unittest
import ConfigParser
import tkp.steps.quality
import tkp.accessors
from tkp.testutil.decorators import requires_data
from tkp.testutil.data import default_job_config, fits_file, casa_table
from tkp.conf import parse_to_dict


@requires_data()
class TestQuality(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.accessor = tkp.accessors.open(casa_table)
        cls.job_config = ConfigParser.SafeConfigParser()
        cls.job_config.read(default_job_config)

    def test_check(self):
        tkp.steps.quality.reject_check(self.accessor.url, self.job_config)

    def test_zero_integration(self):
        accessor = tkp.accessors.open(fits_file)
        accessor._tau_time = 0
        quality_parset = parse_to_dict(self.job_config, 'quality_lofar')
        result = tkp.steps.quality.reject_check_lofar(accessor, quality_parset)
        self.assertTrue(result)
