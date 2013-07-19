import os

import unittest2 as unittest

import tkp.accessors as accessors
from tkp.testutil.data import DATAPATH
from tkp.testutil.decorators import requires_data



casatable = os.path.join(DATAPATH, 'L21641_SB098.restored.image')

@requires_data(casatable)
class TestLofarCasaImage(unittest.TestCase):
    def test_casaimage(self):
        image = accessors.open(casatable)
        self.assertEqual(type(image), accessors.CasaImage)
