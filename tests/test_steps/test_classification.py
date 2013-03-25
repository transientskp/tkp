import unittest
import tempfile
import tkp.steps.classification
from tkp.testutil.decorators import requires_database


@requires_database()
class TestClassification(unittest.TestCase):
    def setUp(self):
        #Clearly this is nonsense, but we're just testing syntax in a 
        # non-functional library...
        self.transients = [{'runcat':'1', 'band':'1'}]

        self.parset = tempfile.NamedTemporaryFile()
        self.parset.write("weighting.cutoff = 0.2\n")
        self.parset.flush()

    def runTest(self):
        for t in self.transients:
            tkp.steps.classification.classify(t, self.parset.name)

