import unittest
try:
    unittest.TestCase.assertIsInstance
except AttributeError:
    import unittest2 as unittest
from tkp.classification.manual.classification import SlowTransient
from tkp.classification.manual.classification import GRBPrompt
from tkp.classification.manual.classification import MainBranch
from tkp.classification.manual.classification import SpectralBranch
from tkp.classification.manual.classifier import Classifier
from tkp.classification.manual.transient import Transient



class TestManual(unittest.TestCase):

    """Simple demo tests for manual classification"""

    def setUp(self):
        self.transient1 = Transient(5, 100, 10, 'GRBs')
        self.transient2 = Transient(6, 1e7, 1e6, spectralindex=-1)

    def test_grb_prompt(self):
        """Only check whether this is a GRB prompt event"""
        
        classifier = Classifier(self.transient1, GRBPrompt)
        self.assertEqual(classifier.classify(), [('GRB prompt emission', 1.2)])
        classifier = Classifier(self.transient2, GRBPrompt)
        self.assertEqual(classifier.classify(), [('GRB prompt emission', 0.)])

    def test_spectrum(self):
        """Test whether this source has a negative index.
        If so, proceed with next tests.
        """

        classifier = Classifier(self.transient1, SpectralBranch)
        self.assertEqual(classifier.classify(), [])
        classifier = Classifier(self.transient2, SpectralBranch)
        self.assertEqual(classifier.classify(), [('Slow transient', 1.8), ('GRB prompt emission', 0.)])
        
    def test_all(self):
        """Test for all defined classifications"""
        
        classifier = Classifier(self.transient1, MainBranch)
        self.assertEqual(classifier.classify(),
                    [('Slow transient', 0.), ('Fast transient', 1.8), ('GRB prompt emission', 1.2),
                     ('Any transient that can be associated with a database', 1.0)])
        classifier = Classifier(self.transient2, MainBranch)
        self.assertEqual(classifier.classify(),
                    [('Slow transient', 1.8), ('Fast transient', 0.), ('GRB prompt emission', 0),
                     ('Any transient that can be associated with a database', 0.)])

    def test_branching(self):
        self.assertEqual(SpectralBranch(self.transient2).classify(),
                         [('Slow transient', 1.8), ('GRB prompt emission', 0)])
        self.transient2.spectralindex = 1
        self.assertEqual(SpectralBranch(self.transient2).classify(), [])


if __name__ == "__main__":
    unittest.main()
