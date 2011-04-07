# By Thijs Coenen oktober 2007 for Research with the Transients Key Project
"""This file contains the unit tests that go with the tree.py module."""
import unittest
import tree

TRY_UNIVARIATE = 0
TRY_MULTIVARIATE = 1
TRY_FOREST_RI = 2
TRY_FOREST_RC = 3 

class test_build_tree(unittest.TestCase):
    def test1(self):
        """trivial 1d test data, check tree construction, do resubstitution test"""
        r1 = range(10)
        r2 = range(10, 20)
        test_data = [(x, x, 1, 0) for x in r1]
        test_data.extend([(x, x, 1, 1) for x in r2])
        total_weight = [10, 10]
        total_gini = 0.5 * 0.5 * 20
        method = {"TRY_UNIVARIATE" : True}
        MIN_LEAF_SIZE = 1
        MAX_DEPTH = 10

        tc = tree.tree_classifier(test_data, 2, MAX_DEPTH, MIN_LEAF_SIZE, method)
        for v in test_data:
            self.assertEqual(tc.run(v)[0], v[-1])
    def test2(self):
        """trivial 2d test data, check multivariate split tree construction, do resubsitution test"""
        pass  # first writing user.py
        
if __name__ == "__main__":
    unittest.main()