# By Thijs Coenen oktober 2007 for Research with the Transients Key Project
"""unit tests that go with multivariate.py"""
import unittest
import multivariate
import math

class test_inner(unittest.TestCase):
    def test1(self):
        """check wether the innerproduct is calculated correctly"""
        m = range(10)
        n_dim = 10
        v1 = tuple([1 for i in xrange(12)])
        v2 = tuple([1 for i in xrange(12)])
        self.assertEqual(multivariate.inner(v1, v2, m), 10)
        m = [1, 4, 5]
        self.assertEqual(multivariate.inner(v1, v2, m), 3)
        m = range(10)        
        v2 = tuple([0 for i in xrange(10)])
        self.assertEqual(multivariate.inner(v1, v2, m), 0)

class test_average(unittest.TestCase):
    def test1(self):
        """check trivial example of averaging two unit vectors"""
        mask = range(2)
        n_dim = 2
        v1 = (1, 0)
        v2 = (0, 1)
        out = multivariate.average([v1, v2], n_dim, mask)
        self.assertAlmostEqual(out[0], 0.5 * math.sqrt(2))
        self.assertAlmostEqual(out[1], 0.5 * math.sqrt(2))
    def test2(self):
        """check wether a list of unit vectors is accepted"""
        mask = range(3)
        n_dim = 3
        l = [(1, 0, 0), (1, 0, 0), (1, 0, 0), (1, 0, 0), (1, 0, 0)]
        out = multivariate.average(l, n_dim, mask)
        self.assertEqual(out, [1, 0, 0])
        
class test_mirror(unittest.TestCase):
    def test1(self):
        """test the mirroring of two vectors"""
        mask = range(2)
        n_dim = 2
        v1 = (1, 0)
        v2 = (0, 1)
        out = multivariate.mirror(v1, v2, n_dim, mask)
        self.assertEqual(out[0], -1)
        self.assertEqual(out[1], 0)
        out1 = multivariate.mirror(v2, v1, n_dim, mask)
        self.assertEqual(out1[0], 0)
        self.assertEqual(out1[1], -1)

class test_create_simplex_random(unittest.TestCase):
    def test1(self):
        """check that simplex created has the appropriate number of elements"""
        simplex = multivariate.create_simplex_random(4, range(3))
        self.assertEqual(len(simplex), 3)
    def test2(self):
        """check that each vector in simplex has enough elements"""
        simplex = multivariate.create_simplex_random(5, range(3))
        for vector in simplex:
            self.assertEqual(len(vector), 5)
        
class test_simplex_on_sphere(unittest.TestCase):
    def test1(self):
        """sanity test or trivial split"""
        test_data = [(1, 0, 0, 1, 0), (1, 0, 1, 1, 0), (0, 0, 2, 1, 1), (0, 0, 3, 1, 1)]
        weights = [2, 2]
        n_dim = 2
        mask = [0, 1]
        r = multivariate.simplex_on_sphere(test_data, weights, n_dim, mask, 1)
    def test2(self):
        """check that all required info is in result dictionary """
        test_data = [(1, 0, 0,  1, 0), (1, 0, 1, 1, 0), (0, 0, 2, 1, 1), (0, 0, 3, 1, 1)]
        weights = [2, 2]
        n_dim = 2
        mask = [0, 1]
        r = multivariate.simplex_on_sphere(test_data, weights, n_dim, mask, 1)
        for k in ["WEIGHT_LEFT", "WEIGHT_RIGHT", "GINI_LEFT", "GINI_RIGHT", 
            "GINI", "SPLIT", "VECTOR", "SPLIT_AT_VALUE", "TYPE", "MASK"]:
            self.failUnless(r.has_key(k))
    def test3(self):
        """checks wether that multivariate split is performed in the right spot"""
        test_data = [(1, 0, 0, 1, 0), (1, 0, 1, 1, 0), (0, 0, 2, 1, 1), (0, 0, 3, 1, 1)]
        weights = [2, 2]
        n_dim = 2
        mask = [0, 1]
        r = multivariate.simplex_on_sphere(test_data, weights, n_dim, mask, 1)
        self.assertAlmostEqual(r["SPLIT"], 2)
        self.assertEqual(r["MASK"], mask)
        self.assertEqual(len(r["VECTOR"]), len(mask))

    def test4(self):
        """same as test2 and test3 but with variables masked out"""
        test_data = [(1, 0, 4, 5, 0, 1, 0), (1, 0,1,3, 1, 1, 0), (0, 0, 8,9,2, 1, 1), (0, 0, 1333,200,3, 1, 1)]
        weights = [2, 2]
        n_dim = 2
        mask = [0, 1]
        r = multivariate.simplex_on_sphere(test_data, weights, n_dim, mask, 1)
        for k in ["WEIGHT_LEFT", "WEIGHT_RIGHT", "GINI_LEFT", "GINI_RIGHT", 
            "GINI", "SPLIT", "VECTOR", "SPLIT_AT_VALUE", "TYPE", "MASK"]:
            self.failUnless(r.has_key(k))
        self.assertAlmostEqual(r["SPLIT"], 2)
        self.assertEqual(r["MASK"], mask)
        self.assertEqual(len(r["VECTOR"]), len(mask))
        
class test_multivariate_split(unittest.TestCase):
    def test1(self):
        """check multivariate splitting with trivial example"""
        test_data = [(1, 0, 0, 1, 0), (1, 0, 1, 1, 0), (0, 0, 2, 1, 1), (0, 0, 3, 1, 1)]
        weights = [2, 2]
        MIN_LEAF_SIZE = 1
        r = multivariate.multivariate_split(test_data, weights, MIN_LEAF_SIZE)
        for k in ["WEIGHT_LEFT", "WEIGHT_RIGHT", "GINI_LEFT", "GINI_RIGHT", 
            "GINI", "SPLIT", "VECTOR", "SPLIT_AT_VALUE", "TYPE", "MASK"]:
            self.failUnless(r.has_key(k))
        self.assertAlmostEqual(r["SPLIT"], 2)
        # since this basically boils down to a test of simplex_on_sphere I rely
        # on the tests that are in place to test that function
        
        
            

if __name__ == "__main__":
    unittest.main()