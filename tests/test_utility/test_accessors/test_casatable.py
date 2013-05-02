import os

import unittest2 as unittest

from tkp.utility.accessors.casaimage import CasaImage
from tkp.testutil.data import DATAPATH
from tkp.testutil.decorators import requires_data



casatable =  os.path.join(DATAPATH, 'L21641_SB098.restored.image')

@requires_data(casatable)
class TestLofarCasaImage(unittest.TestCase):
    def test_casaimage(self):
        self.assertRaises(NotImplementedError, CasaImage, (casatable,))
