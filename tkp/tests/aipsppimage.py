# Tests for generic utility functions written for the TKP pipeline.

import unittest
try:
    unittest.TestCase.assertIsInstance
except AttributeError:
    import unittest2 as unittest

# This test fails if we can't import pyrap.
import pyrap
import os
from tkp.utility import accessors
from tkp.sourcefinder import image
import tkp.config
from utilities.decorators import requires_data
from utilities.decorators import requires_module

DATAPATH = tkp.config.config['test']['datapath']

class AIPSppImage(unittest.TestCase):
    def setUp(self):
        self.filename = os.path.join(DATAPATH, 'CX3_peeled.image/')
        # Beam here is a random beam, in this case the WENSS beam
        # without the declination dependence.
        aipsppim = accessors.AIPSppImage(self.filename,
                                         beam=(54./3600, 54./3600, 0.))
        self.image = image.ImageData(aipsppim.data, aipsppim.beam,
                                     aipsppim.wcs)

    @requires_data(os.path.join(DATAPATH, 'CX3_peeled.image/'))
    def testExtractPython(self):
        self.image.extract(det=15)

if __name__ == '__main__':
    unittest.main()
