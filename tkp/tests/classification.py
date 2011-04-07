from tkp.classification.manual.classification import SlowTransient
from tkp.classification.manual.classification import GRBPrompt
from tkp.classification.manual.classification import MainBranch, SpectralBranch
from tkp.classification.manual.classifier import Classifier
from tkp.classification.manual.transient import Transient
import unittest



class TestManual(unittest.TestCase):

    """Simple demo tests for manual classification"""

    def setUp(self):
        self.transient1 = Transient(5, 100, 10, 'GRBs')
        self.transient2 = Transient(6, 1e7, 1e6, spectralindex=-1)

    def test_grb_prompt(self):
        classifier = Classifier(self.transient1, GRBPrompt)
        self.assertEqual(classifier.classify(), [('GRB prompt emission', 1.2)])

    def test_all(self):
        classifier = Classifier(self.transient1, MainBranch)
        self.assertEqual(classifier.classify(),
                    [('Slow transient', 0), ('GRB prompt emission', 1.2)])
        classifier = Classifier(self.transient2, MainBranch)
        self.assertEqual(classifier.classify(),
                    [('Slow transient', 1.8), ('GRB prompt emission', 0)])

    def test_branching(self):
        self.assertEqual(SpectralBranch(self.transient2).classify(),
                         [('Slow transient', 1.8), ('GRB prompt emission', 0)])
        self.transient2.spectralindex = 1
        self.assertEqual(SpectralBranch(self.transient2).classify(), [])


if __name__ == "__main__":
    unittest.main()
