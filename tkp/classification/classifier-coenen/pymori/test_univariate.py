# By Thijs Coenen oktober 2007 for Research with the Transients Key Project
"""unit tests that go with test_univariate.py"""
import unittest
import univariate

class test_univariate_split(unittest.TestCase):
    def test1(self):
        """checks wether the split is performed on the right feature"""
        test_data = [(1, 0, 0, 1, 0), (1, 0, 1, 1, 0), (0, 0, 2, 1, 1), (0, 0, 3, 1, 1)]
        weights = [2, 2]
        r = univariate.univariate_split(test_data, weights, 1)
        self.assertEqual(r["AXIS"] , 0)
    def test2(self):
        """checks that all the relevant data is present in result"""
        test_data = [(1, 0, 0, 1, 0), (1, 0, 1, 1, 0), (0, 0, 2, 1, 1), (0, 0, 3, 1, 1)]
        weights = [2, 2]
        r = univariate.univariate_split(test_data, weights, 1)
        # stuff that was propagated up from core.multi_class_split
        self.failUnless(r.has_key("WEIGHT_LEFT"))
        self.failUnless(r.has_key("WEIGHT_RIGHT"))
        self.failUnless(r.has_key("GINI_LEFT"))
        self.failUnless(r.has_key("GINI_RIGHT"))
        self.failUnless(r.has_key("GINI"))
        self.failUnless(r.has_key("SPLIT"))
        # stuff calculated by univarate.univariate_split
        self.failUnless(r.has_key("AXIS"))
        self.failUnless(r.has_key("TYPE"))
        self.failUnless(r.has_key("SPLIT_AT_VALUE"))
    def test3(self):
        """checks wether thet split is performed in the right spot"""
        test_data = [(1, 0, 0, 1, 0), (1, 0, 1, 1, 0), (0, 0, 2, 1, 1), (0, 0, 3, 1, 1)]
        weights = [2, 2]
        r = univariate.univariate_split(test_data, weights, 1)
        self.assertAlmostEqual(r["SPLIT_AT_VALUE"], 0.5)

class test_forest_RI(unittest.TestCase):
    def test1(self):
        """checks that all the relevant data is present in result"""
        test_data = [(1, 0, 0, 1, 0), (1, 0, 1, 1, 0), (0, 0, 2, 1, 1), (0, 0, 3, 1, 1)]
        weights = [2, 2]
        r = univariate.univariate_split(test_data, weights, 1)
        # stuff that was propagated up from core.multi_class_split
        self.failUnless(r.has_key("WEIGHT_LEFT"))
        self.failUnless(r.has_key("WEIGHT_RIGHT"))
        self.failUnless(r.has_key("GINI_LEFT"))
        self.failUnless(r.has_key("GINI_RIGHT"))
        self.failUnless(r.has_key("GINI"))
        self.failUnless(r.has_key("SPLIT"))
        # stuff calculated by univarate.univariate_split
        self.failUnless(r.has_key("AXIS"))
        self.failUnless(r.has_key("TYPE"))
        self.failUnless(r.has_key("SPLIT_AT_VALUE"))
    def test2(self):
        """checks wether thet split is performed in the right spot"""
        # both feature 0 and 1 are best split at 0.5
        test_data = [(1, 0, 0, 1, 0), (1, 0, 1, 1, 0), (0, 0, 2, 1, 1), (0, 0, 3, 1, 1)]
        weights = [2, 2]
        r = univariate.univariate_split(test_data, weights, 1)
        self.assertAlmostEqual(r["SPLIT_AT_VALUE"], 0.5)
        

if __name__ == "__main__":
    unittest.main()