# By Thijs Coenen oktober 2007 for Research with the Transients Key Project
"""This file contains the unit tests that go with the tree.py module."""
import unittest
import user
import dataset

TRY_UNIVARIATE = 0
TRY_MULTIVARIATE = 1
TRY_FOREST_RI = 2
TRY_FOREST_RC = 3 # don't use forest_RC algorithm yet

class test_RF_RI(unittest.TestCase):
    def test1(self):
        """trivial construct random forest test"""
        d = dataset.set1()
        fc = user.construct_random_forest_RI(d, 2, 5, 10, 1)

class test_RF_RC(unittest.TestCase):
    def test1(self):
        """trivial construct random forest test"""
        d = dataset.set1()
        fc = user.construct_random_forest_RC(d, 2, 5, 10, 2, 5)
        

        
if __name__ == "__main__":
    unittest.main()