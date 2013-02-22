import unittest2 as unittest
import os
from tkp.utility.accessors.casaimage import CasaImage
import tkp.config
from tkp.testutil.decorators import requires_data


DATAPATH = tkp.config.config['test']['datapath']

casatable =  os.path.join(DATAPATH, 'L21641_SB098.restored.image')

@requires_data(casatable)
class TestLofarCasaImage(unittest.TestCase):
    def test_casaimage(self):
        self.assertRaises(NotImplementedError, CasaImage, (casatable,))
