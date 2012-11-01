
import unittest
import trap.persistence

images = [] # list of image paths

@unittest.skip("we need some datafiles first")
class TestPersistence(unittest.TestCase):
    def testSimpleStore(self):
        trap.persistence.store(images, "unittesting", False)
