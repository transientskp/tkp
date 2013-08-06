import unittest
import ConfigParser
import tkp.steps.quality
import tkp.accessors
import tkp.testutil.data as testdata
from tkp.testutil.decorators import requires_database
from tkp.testutil.data import default_parset_paths

@requires_database()
class TestQuality(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.accessor = tkp.accessors.open(testdata.casa_table)
        cls.job_config = ConfigParser.SafeConfigParser()
        cls.job_config.read(default_parset_paths['quality_check.parset'])

    def test_check(self):
        tkp.steps.quality.reject_check(self.accessor.url, self.job_config)
