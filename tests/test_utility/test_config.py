import unittest2 as unittest
from tkp.config import double_list_from_string


class TestListParse(unittest.TestCase):
    """Check parsing of string into double list"""
    
    def setUp(self):
        pass


    def tearDown(self):
        pass


    def test_correct(self):
        text = "[[1, 2, 3], [4, 5, 6], [6, 7, 8]]"
        
        [[1, 2, 3], [4, 5, 6], [6, 7, 8]]
        [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [6.0, 7.0, 8.0]]
        
        self.assertEqual(double_list_from_string(text),
                         [['1', ' 2', ' 3'], ['4', ' 5', ' 6'], ['6', ' 7', ' 8']])
        self.assertEqual(double_list_from_string(text, contenttype=int),
                         [[1, 2, 3], [4, 5, 6], [6, 7, 8]])
        self.assertEqual(double_list_from_string(text, contenttype=float),
                         [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [6.0, 7.0, 8.0]])
        

    def test_incorrect(self):
        try:
            double_list_from_string("[1, 2, 3], [2, 3, 4]")
        except ValueError, exc:
            self.assertEqual(exc.args[0], "[1, 2, 3], [2, 3, 4] is not a valid double list")
        except Exception, msg:
            self.fail("incorrect exception raised: %s" % str(msg))

        try:
            double_list_from_string("[[1, 2, 3]], [2, 3, 4]")
        except ValueError, exc:
            self.assertEqual(exc.args[0], "[[1, 2, 3]], [2, 3, 4] is not a valid double list")
        except Exception, msg:
            self.fail("incorrect exception raised: %s" % str(msg))

        try:
            double_list_from_string("[[1 2 3], [2, 3, 4]]")
        except ValueError, exc:
            self.assertEqual(exc.args[0], "[[1 2 3], [2, 3, 4]] is not a valid double list")
        except Exception, msg:
            self.fail("incorrect exception raised: %s" % str(msg))

        try:
            double_list_from_string("[[1, 2, 3] [2, 3, 4]]")
        except ValueError, exc:
            self.assertEqual(exc.args[0], "missing separating comma in [[1, 2, 3] [2, 3, 4]]")
        except Exception, msg:
            self.fail("incorrect exception raised: %s" % str(msg))

        try:
            double_list_from_string("[[1, 2, 3], [2, 3, 4]]", contenttype=list)
        except ValueError, exc:
            self.assertEqual(exc.args[0], "unknown or not allowed contenttype")
        except Exception, msg:
            self.fail("incorrect exception raised: %s" % str(msg))

        
    
if __name__ == "__main__":
    unittest.main()
