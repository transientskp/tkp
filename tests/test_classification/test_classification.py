import unittest
from tkp.classification.manual.classifier import Classifier
from tkp.classification.transient import Transient


# Set up the classification system.
# Normally, this would be done in an external file (module), but that
# would complicate things, since we would have to set the TKPCONFIGDIR
# environment variable, and that module would have to be called
# classification.py, the same name as this unit test.
from tkp.classification.manual.classifier import Branch
from tkp.classification.manual.classifier import ClassifiedObject


class ShortTransient(ClassifiedObject):
    """Short duration transient"""

    def test_duration(self):
        if self.duration < 1e3:
            return 1


class ShortRapidTransient(ClassifiedObject):
    """Short duration, high activity transient"""

    def test_activity(self):
        if self.activity > 0.5:
            return 1

    def test_duration(self):
        if self.duration < 1e3:
            return 1


class ShortSlowTransient(ClassifiedObject):
    """Short duration, low activity transient"""

    def test_activity(self):
        if self.activity < 0.5:
            return 1

    def test_duration(self):
        if self.duration < 1e3:
            return 1


class LongTransient(ClassifiedObject):
    """Long duration transient"""

    def test_duration(self):
        if self.duration > 1e3:
            return 1


class LongRapidTransient(ClassifiedObject):
    """Long duration, high activity transient"""

    def test(self):
        if self.activity > 0.5 and self.duration > 1e3:
            return 1


class LongSlowTransient(ClassifiedObject):
    """Long duration, low activity transient"""

    def test(self):
        if self.activity <= 0.5 and self.duration > 1e3:
            return 1


class RapidTransient(ClassifiedObject):
    """High activity transient"""

    def test(self):
        if self.activity > 0.5:
            return 1

        
class SlowTransient(ClassifiedObject):
    """Low activity transient"""

    def test(self):
        if self.activity > 0.5:
            return 1

        
class ShortDurationBranch(Branch):
    """Branch on short transients"""

    def test_duration(self):
        if self.duration < 1e3:
            self.eval(RapidTransient, SlowTransient)
            return 1


class LongDurationBranch(Branch):
    """Branch on short transients"""

    def test_duration(self):
        if self.duration > 1e3:
            self.eval(RapidTransient, SlowTransient)
            return 1


class DurationBranch(Branch):
    """Branch on short/long transient duration"""

    def test_duration(self):
        if self.duration < 1e3:
            self.eval(ShortTransient, ShortRapidTransient, ShortSlowTransient)
        else:
            self.eval(LongTransient, LongRapidTransient, LongSlowTransient)


class Main(Branch):
    """Starting point"""

    def test(self):
        self.eval(DurationBranch)



# This is where the unit tests really start!
class TestManual(unittest.TestCase):
    """Simple demo tests for manual classification"""

    def setUp(self):
        self.grb_db = {
            'ra': 123.123, 'dec': 45.45, 'ra_err': 2., 'decl_err': 3.2,
            'dist_arcsec': 12.3, 'assoc_r': 3.6, 'catname': 'GRB',
            'catsrcname': 'GRB012345A', 'catsrcid': 1234}
        self.vlss_db = {
            'decl': 55.91, 'catid': 4, 'dist_arcsec': 13.34, 'decl_err': 3.2,
            'ra_err': 3.02, 'assoc_r': 4.0, 'catname': 'VLSS', 'ra': 53.08,
            'catsrcname': '0332.3+5555', 'catsrcid': 1783982}
        self.nvss_db =  {
            'decl': 55.92, 'catid': 3, 'dist_arcsec': 13.57, 'decl_err': 0.60,
            'ra_err': 0.42, 'assoc_r': 5.5, 'catname': 'NVSS', 'ra': 53.08,
            'catsrcname': 'J033220+555509', 'catsrcid': 261940}
        self.transient1 = Transient(1, duration=100, activity=0.8)
        self.transient2 = Transient(2, duration=100, activity=0.4,
                                    database={'GRB': self.grb_db})
        self.transient3 = Transient(3, duration=1e7, activity=0.4, spectralindex=-1)
        self.transient4 = Transient(4, duration=1e8, activity=1.0,
                                    database={'VLSS': self.vlss_db,
                                              'NVSS': self.nvss_db})


    def test_shortduration(self):
        """Short duration"""
        classifier = Classifier(self.transient1, ShortTransient)
        self.assertDictEqual({'Short duration transient': 1},
                             classifier.classify())
        classifier = Classifier(self.transient2, ShortTransient)
        self.assertDictEqual({'Short duration transient': 1},
                             classifier.classify())
        classifier = Classifier(self.transient3, ShortTransient)
        self.assertDictEqual({'Short duration transient': 0},
                             classifier.classify())
        classifier = Classifier(self.transient4, ShortTransient)
        self.assertDictEqual({'Short duration transient': 0},
                             classifier.classify())

    def test_shortrapidduration(self):
        """Short duration, high activity"""
        classifier = Classifier(self.transient1, ShortRapidTransient)
        self.assertDictEqual({'Short duration, high activity transient': 2},
                             classifier.classify())
        classifier = Classifier(self.transient2, ShortRapidTransient)
        self.assertDictEqual({'Short duration, high activity transient': 1},
                             classifier.classify())
        classifier = Classifier(self.transient3, ShortRapidTransient)
        self.assertDictEqual({'Short duration, high activity transient': 0},
                             classifier.classify())
        classifier = Classifier(self.transient4, ShortRapidTransient)
        self.assertDictEqual({'Short duration, high activity transient': 1},
                             classifier.classify())

    def test_branching(self):
        self.assertDictEqual(
            {'Short duration transient': 1,
             'Short duration, high activity transient': 2,
             'Short duration, low activity transient': 1},
            Classifier(self.transient1, DurationBranch).classify())
        self.assertDictEqual(
            {'Short duration transient': 1,
             'Short duration, high activity transient': 1,
             'Short duration, low activity transient': 2},
            Classifier(self.transient2, DurationBranch).classify())
        self.assertDictEqual(
            {'Long duration transient': 1,
             'Long duration, high activity transient': 0,
             'Long duration, low activity transient': 1},
            Classifier(self.transient3, DurationBranch).classify())
        self.assertDictEqual(
            {'Long duration transient': 1,
             'Long duration, high activity transient': 1,
             'Long duration, low activity transient': 0},
            Classifier(self.transient4, DurationBranch).classify())

    def test_selective_branching(self):
        self.assertDictEqual(
            {'High activity transient': 2, 'Low activity transient': 2},
            Classifier(self.transient1, ShortDurationBranch).classify())
        self.assertDictEqual(
            {'High activity transient': 1, 'Low activity transient': 1},
            Classifier(self.transient2, ShortDurationBranch).classify())
        self.assertDictEqual(
            {}, Classifier(self.transient3, ShortDurationBranch).classify())
        self.assertDictEqual(
            {}, Classifier(self.transient4, ShortDurationBranch).classify())
        self.assertDictEqual(
            {}, Classifier(self.transient1, LongDurationBranch).classify())
        self.assertDictEqual(
            {}, Classifier(self.transient2, LongDurationBranch).classify())
        self.assertDictEqual(
            {'High activity transient': 1, 'Low activity transient': 1},
            Classifier(self.transient3, LongDurationBranch).classify())
        self.assertDictEqual(
            {'High activity transient': 2, 'Low activity transient': 2},
            Classifier(self.transient4, LongDurationBranch).classify())

    def test_fullclassifier(self):
        self.assertDictEqual(
            {'Short duration transient': 1,
             'Short duration, high activity transient': 2,
             'Short duration, low activity transient': 1},
            Classifier(self.transient1, Main).classify())
        self.assertDictEqual(
            {'Short duration transient': 1,
             'Short duration, high activity transient': 1,
             'Short duration, low activity transient': 2},
            Classifier(self.transient2, Main).classify())
        self.assertDictEqual(
            {'Long duration transient': 1,
             'Long duration, high activity transient': 0,
             'Long duration, low activity transient': 1},
            Classifier(self.transient3, Main).classify())
        self.assertDictEqual(
            {'Long duration transient': 1,
             'Long duration, high activity transient': 1,
             'Long duration, low activity transient': 0},
            Classifier(self.transient4, Main).classify())

#    def test_configdir(self):
#        print Classifier(self.transient1, paths=["/home/evert/.transientskp"]).classify()
#        print Classifier(self.transient2, paths=["/home/evert"]).classify()
#        print Classifier(self.transient3).classify()
#        print Classifier(self.transient4, base=Main).classify()

        
if __name__ == "__main__":
    unittest.main()
