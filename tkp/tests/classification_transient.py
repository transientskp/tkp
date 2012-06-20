"""

Test the classification Transient class, and the Undefined helper class

"""

import unittest
try:
    unittest.TestCase.assertIsInstance
except AttributeError:
    import unittest2 as unittest
from tkp.classification.transient import Undefined



class TestUndefined(unittest.TestCase):

    """Test that Undefined() instances raise a TypeError in comparisons"""

    def setUp(self):
        pass

    def test_Undefined(self):
        """Contrast the None test case with this one"""
        with self.assertRaisesRegexp(
            TypeError, "Cannot compare an undefined value"):
            Undefined() < 0
        with self.assertRaisesRegexp(
            TypeError, "Cannot compare an undefined value"):
            Undefined() > 0
        with self.assertRaisesRegexp(
            TypeError, "Cannot compare an undefined value"):
            Undefined() == 0
        with self.assertRaisesRegexp(
            TypeError, "Cannot compare an undefined value"):
            Undefined() != 0
        # Test the other way 'round, just to be safe
        with self.assertRaisesRegexp(
            TypeError, "Cannot compare an undefined value"):
            0 > Undefined()
        with self.assertRaisesRegexp(
            TypeError, "Cannot compare an undefined value"):
            0 < Undefined()
        with self.assertRaisesRegexp(
            TypeError, "Cannot compare an undefined value"):
            0 == Undefined()
        with self.assertRaisesRegexp(
            TypeError, "Cannot compare an undefined value"):
            0 != Undefined()

    def test_None(self):
        """Contrast the Undefined test case with this one"""
        self.assertTrue(None < 0)   # Amazing; will it *always* evaluate to True?
        self.assertFalse(None > 0)
        self.assertFalse(None == 0)
        self.assertTrue(None != 0)
        

if __name__ == "__main__":
    unittest.main()
