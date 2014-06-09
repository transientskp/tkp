import unittest
import pickle
from tkp.utility import adict

data = (('a', 'b'), ('c', 'd'), ('e', {'nested': 'dict'}))


class TestAdict(unittest.TestCase):
    def test_pickle(self):
        """
        check if we can pickle and unpickle the adict
        """
        cucumis_sativus = adict(data)
        pickled = pickle.dumps(cucumis_sativus)
        unpickled = pickle.loads(pickled)
        self.assertEqual(cucumis_sativus, unpickled)