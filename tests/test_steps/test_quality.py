import unittest
import tempfile
import tkp.steps.quality
import tkp.utility.accessors
import tkp.testutil.data as testdata
from tkp.testutil.decorators import requires_database

@requires_database()
class TestQuality(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.accessor = tkp.utility.accessors.open(testdata.casa_table)

    def test_parse_parset(self):
        parset = tempfile.NamedTemporaryFile()
        parset.flush()
        tkp.steps.quality.parse_parset(parset.name)

    def test_check(self):
        parset = {
            'sigma': 3,
            'f': 4,
            'low_bound': 1,
            'high_bound': 200,
            'oversampled_x': 30,
            'elliptical_x': 2.0,
            'min_separation': 20,
        }
        tkp.steps.quality.reject_check(self.accessor.url, parset)
