import unittest
from tkp.utility import substitute_nan, substitute_inf

class SubstituteInfTestCase(unittest.TestCase):
    def test_not_inf(self):
        """
        Non-inf returned unchanged.
        """
        value = 1
        self.assertEqual(substitute_inf(value), value)

    def test_inf(self):
        """
        inf substituted to "Infinity".
        """
        value = float("inf")
        self.assertEqual(substitute_inf(value), "Infinity")

    def test_non_default_subst(self):
        """
        NaN substitute to non default.
        """
        value = float("inf")
        self.assertEqual(substitute_inf(value, 99), 99)

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
