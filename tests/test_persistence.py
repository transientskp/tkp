
import unittest
import trap.ingredients.persistence

images = [] # list of image paths

@unittest.skip("we need some datafiles first")
class TestPersistence(unittest.TestCase):
    def testSimpleStore(self):
        trap.ingredients.persistence.store(images, "unittesting", False)
