import unittest
import tkp.steps.classification
from tkp.testutil.decorators import requires_database
from tkp.conf import read_config_section
from tkp.testutil.data import default_job_config


@requires_database()
class TestClassification(unittest.TestCase):
    def setUp(self):
        #Clearly this is nonsense, but we're just testing syntax in a
        # non-functional library...
        self.transients = [{'runcat':'1', 'band':'1'}]

        with open(default_job_config) as f:
            self.parset = read_config_section(f, 'classification')

    def runTest(self):
        for t in self.transients:
            tkp.steps.classification.classify(t, self.parset)

