import unittest
import numpy
from collections import OrderedDict
from tkp.utility import substitute_nan, substitute_inf
from tkp.db import sanitize_db_inputs

class SanitizeDBInputsTestCase(unittest.TestCase):
    TEST_DATA = OrderedDict({
        "float": numpy.float64(1), # Should be converted to float
        "infty": float('inf'),     # Should be converted to "Infinity"
          "int": 1,                # Should not be converted
          "str": "A string"        # Should not be converted
    })

    def test_dict(self):
        cleaned = sanitize_db_inputs(self.TEST_DATA)
        self.assertEqual(len(cleaned), len(self.TEST_DATA))
        self.assertEqual(cleaned['str'], "A string")
        self.assertEqual(cleaned['int'], 1)
        self.assertEqual(cleaned['infty'], "Infinity")
        self.assertEqual(cleaned['float'], 1.0)
        self.assertFalse(isinstance(cleaned['float'], numpy.floating))

    def test_tuple(self):
        cleaned = sanitize_db_inputs(tuple(self.TEST_DATA.values()))
        self.assertEqual(len(cleaned), len(self.TEST_DATA))
        self.assertEqual(cleaned[0], 1.0)
        self.assertFalse(isinstance(cleaned[0], numpy.floating))
        self.assertEqual(cleaned[1], "Infinity")
        self.assertEqual(cleaned[2], 1)
        self.assertEqual(cleaned[3], "A string")


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
