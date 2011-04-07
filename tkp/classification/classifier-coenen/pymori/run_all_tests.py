# By Thijs Coenen oktober 2007 for Research with the Transients Key Project
"""Running this module will run all the available unittests for the decision
tree building functions."""
import unittest
import test_core, test_univariate, test_multivariate, test_tree
            
def create_test_suite():
    s = unittest.TestSuite()
    # test_core.py:
    s.addTests(unittest.makeSuite(test_core.test_initial_weights))
    s.addTests(unittest.makeSuite(test_core.test_multi_class_split))
    
    # test_univariate.py:
    s.addTests(unittest.makeSuite(test_univariate.test_univariate_split))
    s.addTests(unittest.makeSuite(test_univariate.test_forest_RI))
    # test_multivariate.py:
    s.addTests(unittest.makeSuite(test_multivariate.test_inner))
    s.addTests(unittest.makeSuite(test_multivariate.test_average))
    s.addTests(unittest.makeSuite(test_multivariate.test_mirror))
    s.addTests(unittest.makeSuite(test_multivariate.test_create_simplex_random))
    s.addTests(unittest.makeSuite(test_multivariate.test_simplex_on_sphere))
    s.addTests(unittest.makeSuite(test_multivariate.test_multivariate_split))
    # test_tree.py:
    s.addTests(unittest.makeSuite(test_tree.test_build_tree))
    return s

if __name__ == "__main__":
    unittest.main(defaultTest="create_test_suite")
