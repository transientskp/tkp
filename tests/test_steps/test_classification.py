import unittest
import tkp.steps.classification
from tkp.testutil.decorators import requires_database
import tkp.utility.parset as parset
from tkp.testutil.data import default_parset_paths


@requires_database()
class TestClassification(unittest.TestCase):
    def setUp(self):
        #Clearly this is nonsense, but we're just testing syntax in a
        # non-functional library...
        self.transients = [{'runcat':'1', 'band':'1'}]

        with open(default_parset_paths['classification.parset']) as f:
            self.parset = parset.read_config_section(f, 'classification')

    def runTest(self):
        for t in self.transients:
            tkp.steps.classification.classify(t, self.parset)

