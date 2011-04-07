# By Thijs Coenen oktober 2007 for Research with the Transients Key Project
"""Unit test that go with core.py"""
import core
import unittest

class test_initial_weights(unittest.TestCase):
    w1 = [(i, 1, 0) for i in range(10)]
    w1.extend([(i + 10, 1,1) for i in range(10)])
    w1.extend([(i + 20, 1,2) for i in range(10)])
    def test1(self):
        """test the calculation of initial weights and gini value"""
        result = core.initial_weights(self.w1, 3)
        self.assertEqual(result[0], [10, 10, 10])
        self.assertAlmostEqual(result[1], 20.)

class test_multi_class_split(unittest.TestCase):
    def test1(self):
        """test wether the correct split is found, checks off by ones"""
        test_data = [(0, 1, 0), (1, 1, 0), (2, 1, 1), (3, 1, 1)]
        test_weights = [2,2]
        r = core.multi_class_split(test_data, test_weights, 1)
        self.assertEqual(r["SPLIT"], 2)
    def test2(self):
        """tests wether all expected values are present in result_dict"""
        test_data = [(0, 1, 0), (1, 1, 0), (2, 1, 1), (3, 1, 1)]
        test_weights = [2,2]
        r = core.multi_class_split(test_data, test_weights, 1)
        self.failUnless(r.has_key("WEIGHT_LEFT"))
        self.failUnless(r.has_key("WEIGHT_RIGHT"))
        self.failUnless(r.has_key("GINI_LEFT"))
        self.failUnless(r.has_key("GINI_RIGHT"))
        self.failUnless(r.has_key("GINI"))
        self.failUnless(r.has_key("SPLIT"))
    def test3(self):
        """test checks calculation of the weights and gini values"""
        test_data = [(0, 1, 0), (1, 1, 0), (2, 1, 1), (3, 1, 1)]
        test_weights = [2, 2]
        r = core.multi_class_split(test_data, test_weights, 1)
        self.failUnless(r["WEIGHT_LEFT"] == [2, 0])
        self.failUnless(r["WEIGHT_RIGHT"] == [0, 2])
        self.assertEqual(r["GINI_LEFT"], 0)
        self.assertEqual(r["GINI_RIGHT"], 0)
        self.assertEqual(r["GINI"], 0)

    
if __name__ == "__main__":
    unittest.main()
