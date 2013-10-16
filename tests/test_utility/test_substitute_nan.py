import unittest2 as unittest
from tkp.utility import substitute_nan

class SubstituteNanTestCase(unittest.TestCase):
    def test_not_nan(self):
        """
        Non-NaN returned unchanged.
        """
        value = 1
        self.assertEqual(substitute_nan(value), value)

    def test_nan(self):
        """
        NaN substituted to 0.
        """
        value = float("nan")
        self.assertEqual(substitute_nan(value), 0.0)

    def test_non_default_subst(self):
        """
        NaN substitute to non default.
        """
        value = float("nan")
        self.assertEqual(substitute_nan(value, 99), 99)
