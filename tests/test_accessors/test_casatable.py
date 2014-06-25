import os

import unittest

import tkp.accessors as accessors
from tkp.testutil.data import DATAPATH
from tkp.testutil.decorators import requires_data

casatable = os.path.join(DATAPATH, 'accessors/casa.table')

@requires_data(casatable)
class TestLofarCasaImage(unittest.TestCase):
    # CasaImages can't be directly instantiated, since they don't provide the
    # DataAccessor interface.
    def test_casaimage(self):
        self.assertRaises(IOError, accessors.open, casatable)
